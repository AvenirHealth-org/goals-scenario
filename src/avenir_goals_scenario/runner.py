import copy
import datetime
import json
import os
import pickle
import tempfile
import uuid
from collections.abc import Iterator
from multiprocessing import Pool
from pathlib import Path
from queue import Queue

from loguru import logger

from avenir_goals_scenario._runner.indicator_dims import build_indicator_dims
from avenir_goals_scenario._runner.output import (
    check_indicator_dims,
    consolidate_metadata,
    write_scenario_batch,
)
from avenir_goals_scenario._runner.pjnz import find_pjnz_files, import_pjnz
from avenir_goals_scenario._runner.simulation import run_simulation
from avenir_goals_scenario._runner.utils import RunCallbacks, RunResult, WorkUnitResult, get_effective_workers
from avenir_goals_scenario.models import RunConfig, ScenarioSimulations
from avenir_goals_scenario.models.scenario_simulations import ScenarioSimulation, TargetCoverage

_FAILURES_FILENAME = "failures.json"


def _fmt_error(e: Exception) -> str:
    """Short error message, falling back to the exception type name."""
    return str(e) or type(e).__name__


def _run_pjnz_batch(
    params_path: str,
    pjnz_stem: str,
    scenarios: list[ScenarioSimulation],
    config: RunConfig,
    end_year: int,
    part_name: str,
    log_queue=None,
    progress=None,
) -> list[WorkUnitResult]:
    """Run a batch of scenarios for one PJNZ and write them as one file per indicator.

    The PJNZ params are loaded once and kept as a pristine template; each
    scenario runs on a fresh ``deepcopy`` (``apply_simulation`` mutates in place,
    so scenarios must not share a params dict — see the module tests). The whole
    batch is then written by :func:`write_scenario_batch`, so peak memory is one
    batch in flight.

    ``progress``, if given, is called ``progress(pjnz_stem, ok)`` as each scenario
    *finishes simulating* — before the batch is written — so progress advances in
    real time rather than in one jump per batch. A later batch-write failure does
    not un-report those scenarios (rare, and progress is only an indicator; the
    returned results and ``failures.json`` remain authoritative).

    Failure handling: a scenario whose *simulations* raise is skipped (not
    written) and returned as a failed :class:`WorkUnitResult`; the rest of the
    batch continues. A failure while *writing* the batch discards the part file
    and marks every successfully-simulated scenario in the batch as failed, so
    ``--retry`` regenerates the file.
    """
    if log_queue is not None:
        from avenir_goals_scenario._cli.cli_utils import configure_worker_logging

        configure_worker_logging(log_queue)

    with open(params_path, "rb") as f:
        pristine = pickle.load(f)  # noqa: S301 - only loads data we saved ourselves

    output_years = range(config.base_year, end_year + 1)

    results: list[WorkUnitResult] = []
    batch: list[tuple[str, list]] = []
    for scenario in scenarios:
        try:
            # Reset to pristine params: apply_simulation mutates in place and
            # different scenarios must not contaminate each other.
            params = copy.deepcopy(pristine)
            start = datetime.datetime.now()
            simulations_out = [
                run_simulation(params, scenario.interventions, simulation, config.output_indicators, output_years)
                for simulation in scenario.simulations
            ]
            elapsed_ms = (datetime.datetime.now() - start).total_seconds() * 1000
            logger.debug(
                "Scenario {} ({} simulation(s)) for {} finished in {}ms",
                scenario.id,
                len(scenario.simulations),
                pjnz_stem,
                elapsed_ms,
            )
        except Exception as e:
            error = _fmt_error(e)
            logger.warning("Scenario {} failed for {}: {}", scenario.id, pjnz_stem, error)
            results.append(WorkUnitResult(pjnz=pjnz_stem, scenario_id=scenario.id, ok=False, error=error))
            if progress is not None:
                progress(pjnz_stem, False)
            continue
        batch.append((scenario.id, simulations_out))
        if progress is not None:
            progress(pjnz_stem, True)

    try:
        write_scenario_batch(config.output_dir, pjnz_stem, part_name, batch, build_indicator_dims(config.base_year))
    except Exception as e:
        error = _fmt_error(e)
        logger.warning(
            "Writing batch {} for {} failed: {}; re-run affected scenarios with --retry", part_name, pjnz_stem, error
        )
        # The part file is discarded, so every simulated scenario must re-run.
        results.extend(WorkUnitResult(pjnz=pjnz_stem, scenario_id=sid, ok=False, error=error) for sid, _ in batch)
        return results

    results.extend(WorkUnitResult(pjnz=pjnz_stem, scenario_id=sid, ok=True) for sid, _ in batch)
    return results


def _dump_pjnz_files(
    pjnz_files: list[Path],
    tmp_dir: str,
    cb: RunCallbacks,
) -> tuple[dict[Path, str], dict[Path, int]]:
    """Import each PJNZ, pickle it to tmp_dir, return paths and end years."""
    params_paths: dict[Path, str] = {}
    end_years: dict[Path, int] = {}
    logger.info("Loading {} PJNZ file(s)", len(pjnz_files))
    for pjnz_path in pjnz_files:
        logger.debug("Importing {}", pjnz_path.name)
        leapfrog_params = import_pjnz(pjnz_path)
        dump_path = str(Path(tmp_dir) / f"{pjnz_path.stem}.pkl")
        with open(dump_path, "wb") as f:
            pickle.dump(leapfrog_params, f)
        params_paths[pjnz_path] = dump_path
        end_years[pjnz_path] = leapfrog_params["projection_end_year"]
        cb.on_pjnz_imported()

    cb.on_imports_complete()
    return params_paths, end_years


def run_scenario_analysis(config: RunConfig, simulations: ScenarioSimulations) -> RunResult:
    """Run scenario analysis across a directory of PJNZ files.

    Converts each PJNZ to leapfrog params once in the main process, dumps them
    to a temporary file using ``pickle.dump``, then distributes ``(PJNZ, batch)``
    work units — each a batch of ``config.scenarios_per_file`` scenarios — across
    worker processes. Workers load params via ``pickle.load``.

    Results are written to Parquet files under ``config.output_dir`` in
    long format, one file per ``(indicator, PJNZ, batch)`` at
    ``{output_dir}/{indicator}/pjnz_name={pjnz_stem}/{part_name}.parquet``. Each
    file holds every scenario in the batch, identified by a ``scenario_id``
    column.

    Scenarios whose simulations fail are logged and skipped rather than aborting
    the run; the rest still complete. Failed scenarios are recorded in the
    returned :class:`RunResult` and written to a ``failures.json`` manifest under
    ``config.output_dir`` for re-running. PJNZ *import* failures remain fatal and
    raise.

    Args:
        config: Validated run configuration.
        simulations: Scenario simulations to run. Use
            `avenir_goals_scenario.draw_simulations` to generate them or
            `avenir_goals_scenario.read_simulations` to load from a file.

    Returns:
        A :class:`RunResult` with the output directory and any failed units.

    Raises:
        FileNotFoundError: If no PJNZ files are found in ``config.pjnz_dir``.
        ValueError: If any output indicator is not present in the Goals output,
            or if a PJNZ file cannot be parsed.
    """
    return _run_scenario_analysis(config, simulations, RunCallbacks())


def _scenario_applies(scenario, pjnz_stem: str, selected: set[tuple[str, str]] | None = None) -> bool:
    """Return True if this scenario should run against the given PJNZ file.

    ``selected``, when supplied, restricts the run to the given
    ``(pjnz_stem, scenario_id)`` pairs (used by ``--retry``).
    """
    if scenario.pjnz_names is not None and pjnz_stem not in scenario.pjnz_names:
        return False
    return selected is None or (pjnz_stem, scenario.id) in selected


def _series_coverages(draw: dict) -> Iterator[list[float]]:
    """Yield every per-year coverage array in one intervention's draw dict.

    A ``list`` value is either the per-target coverages (a list of
    :class:`TargetCoverage`, each of whose ``coverage`` may itself be a per-year
    array) or a bare per-year array for a target-less product (AHD/POC/long-acting).
    """
    for value in draw.values():
        if not isinstance(value, list) or not value:
            continue
        if isinstance(value[0], TargetCoverage):
            for tc in value:
                if isinstance(tc.coverage, list):
                    yield tc.coverage
        else:
            yield value


def _validate_series_lengths(
    pjnz_files: list[Path],
    end_years: dict[Path, int],
    simulations: ScenarioSimulations,
    base_year: int,
    selected_units: set[tuple[str, str]] | None,
) -> None:
    """Check every per-year coverage array against each PJNZ's projection length.

    A per-year coverage/initiation-rate array must carry one value per year from
    ``base_year`` to the PJNZ's projection end year (inclusive). That end year is
    only known once the PJNZ is imported, so this cannot be checked at config
    parse time. Any mismatch raises, aborting the whole run before any scenario is
    executed (a fatal config error, exit code 1).
    """
    for p in pjnz_files:
        expected = end_years[p] - base_year + 1
        for scenario in simulations.scenarios:
            if not _scenario_applies(scenario, p.stem, selected_units):
                continue
            for simulation in scenario.simulations:
                for iv_id, sim in simulation.items():
                    for values in _series_coverages(sim.root):
                        if len(values) != expected:
                            msg = (
                                f"Scenario {scenario.id!r} intervention {iv_id!r}: a per-year coverage array "
                                f"has {len(values)} value(s), but PJNZ {p.stem!r} needs {expected} "
                                f"(one per year from base_year {base_year} to projection end year "
                                f"{end_years[p]} inclusive)."
                            )
                            raise ValueError(msg)


def _select_pjnz_files(pjnz_dir: Path, simulations: ScenarioSimulations) -> list[Path]:
    """Return the PJNZ files that need to be loaded for this run.

    If any scenario has ``pjnz_names=None`` (applies to all PJNZ files), every
    file in ``pjnz_dir`` is returned. Otherwise only the files whose stem appears
    in at least one scenario's ``pjnz_names`` are returned.

    Warns for each named PJNZ that is not present on disk. Raises
    ``FileNotFoundError`` if no matching files are found at all (e.g. every
    specified name is missing), so the caller gets a clear reason instead of
    silently producing no output.
    """
    all_files = find_pjnz_files(pjnz_dir)

    if any(s.pjnz_names is None for s in simulations.scenarios):
        return all_files

    needed = {name for s in simulations.scenarios for name in (s.pjnz_names or [])}
    by_stem = {f.stem: f for f in all_files}

    missing = needed - set(by_stem)
    for name in sorted(missing):
        logger.warning(
            "PJNZ '{}' is listed in scenario pjnz_names but not found in {} — scenarios targeting it will be skipped.",
            name,
            pjnz_dir,
        )

    found = [by_stem[stem] for stem in sorted(needed) if stem in by_stem]
    if not found:
        msg = (
            f"No PJNZ files matched any scenario's pjnz_names. "
            f"Needed: {sorted(needed)}. "
            f"Available in {pjnz_dir}: {sorted(by_stem)}."
        )
        raise FileNotFoundError(msg)

    return found


def _run_scenario_analysis(
    config: RunConfig,
    simulations: ScenarioSimulations,
    callbacks: RunCallbacks,
    log_queue: Queue | None = None,
    pjnz_files: list[Path] | None = None,
    selected_units: set[tuple[str, str]] | None = None,
    progress_queue: Queue | None = None,
) -> RunResult:
    """Internal run_scenario_analysis function.

    Args:
        config: Validated run configuration.
        simulations: Pre-drawn scenario simulations.
        callbacks: Hooks for progress reporting, can be no-op.
        log_queue: Optional queue to pass to _run_pjnz_batch when running
          in parallel so logs can be raised to the same console as progress
          bars when run via CLI.
        selected_units: Optional set of ``(pjnz_stem, scenario_id)`` pairs to
          restrict the run to (used by ``--retry``). ``None`` runs every
          applicable unit.
        progress_queue: Optional queue for per-scenario progress events when
          running in parallel. Each worker puts ``(pjnz_stem, ok)`` as each
          scenario *finishes simulating* (before the batch is written), and the
          caller drains it to advance progress in real time. ``None`` (serial
          runs, or callers without a progress display) reports progress by
          calling ``callbacks`` directly.

    Returns:
        A :class:`RunResult` with the output directory and any failed units.

    Raises:
        FileNotFoundError: If no PJNZ files are found in ``config.pjnz_dir``.
        ValueError: If any output indicator is not present in the Goals output,
            or if a PJNZ file cannot be parsed.
    """
    check_indicator_dims(config.output_indicators, build_indicator_dims(config.base_year))

    config.output_dir.mkdir(exist_ok=True)
    _warn_if_output_exists(config.output_dir)
    if pjnz_files is None:
        pjnz_files = _select_pjnz_files(config.pjnz_dir, simulations)
    logger.info("Loading {} PJNZ file(s) from {}", len(pjnz_files), config.pjnz_dir)

    results: list[WorkUnitResult] = []
    with tempfile.TemporaryDirectory() as tmp_dir:
        params_paths, end_years = _dump_pjnz_files(pjnz_files, tmp_dir, callbacks)
        _validate_series_lengths(pjnz_files, end_years, simulations, config.base_year, selected_units)

        effective_workers = get_effective_workers(config)
        logger.info(
            "Using {} worker(s) (cpu_count={}, configured n_workers={})",
            effective_workers,
            os.cpu_count(),
            config.n_workers,
        )
        # Supplemental part-file prefix so a --retry run writes new files
        # (never rewrites existing ones): "part-0.parquet" on a normal run,
        # "part-retry-<token>-0.parquet" per retry invocation.
        part_prefix = "part" if selected_units is None else f"part-retry-{uuid.uuid4().hex[:8]}"
        work_units = _build_work_units(
            pjnz_files, params_paths, end_years, simulations, config.scenarios_per_file, selected_units, part_prefix
        )
        n_scenario_units = sum(len(scenarios) for _, _, scenarios, _, _ in work_units)
        logger.info(
            "Running {} work unit(s) over {} scenario(s) ({} PJNZ file(s), {} scenario(s)/file, n_workers={})",
            len(work_units),
            n_scenario_units,
            len(pjnz_files),
            config.scenarios_per_file,
            effective_workers,
        )
        logger.info("Running {} simulations per scenario", len(simulations.scenarios[0].simulations))
        if len(work_units) < effective_workers:
            logger.warning(
                "Only {} work unit(s) for {} worker(s): {} core(s) will sit idle. "
                "Lower scenarios_per_file (currently {}) so units >= workers.",
                len(work_units),
                effective_workers,
                effective_workers - len(work_units),
                config.scenarios_per_file,
            )

        if effective_workers == 1:
            # Serial: the worker runs in this process, so it reports each scenario
            # straight to the callbacks as it finishes.
            def progress(pjnz_stem: str, ok: bool) -> None:
                _report_progress(callbacks, pjnz_stem, ok)

            for params_path, pjnz_stem, scenarios, end_year, part_name in work_units:
                batch_results = _run_pjnz_batch(
                    params_path, pjnz_stem, scenarios, config, end_year, part_name, progress=progress
                )
                results.extend(batch_results)
        else:
            # Parallel: workers push per-scenario events onto progress_queue,
            # which the caller drains to advance progress live.
            worker_progress = _QueueProgress(progress_queue) if progress_queue is not None else None
            packed = [
                (params_path, pjnz_stem, scenarios, config, end_year, part_name, log_queue, worker_progress)
                for params_path, pjnz_stem, scenarios, end_year, part_name in work_units
            ]
            with Pool(processes=effective_workers) as pool:
                for batch_results in pool.imap_unordered(_run_pjnz_batch_star, packed):
                    results.extend(batch_results)

    callbacks.on_run_complete()

    failures = [r for r in results if not r.ok]
    _write_failures_manifest(config.output_dir, failures)

    consolidate_metadata(config.output_dir)
    logger.info("Done. Results written to {}", config.output_dir)
    return RunResult(output_dir=config.output_dir, failures=failures)


def _batched(items: list, size: int) -> list[list]:
    """Split *items* into contiguous, non-empty batches of at most *size*."""
    size = max(1, size)
    return [items[i : i + size] for i in range(0, len(items), size)]


def _build_work_units(
    pjnz_files: list[Path],
    params_paths: dict[Path, str],
    end_years: dict[Path, int],
    simulations: ScenarioSimulations,
    scenarios_per_file: int,
    selected_units: set[tuple[str, str]] | None,
    part_prefix: str,
) -> list[tuple[str, str, list[ScenarioSimulation], int, str]]:
    """Build ``(params_path, pjnz_stem, scenarios, end_year, part_name)`` work units.

    Each PJNZ's applicable scenarios are split into contiguous batches of at most
    ``scenarios_per_file``; each batch is one unit that writes ``{part_prefix}-{i}``
    files. Batch index is per-PJNZ so file names are unique within a partition.
    """
    units: list[tuple[str, str, list[ScenarioSimulation], int, str]] = []
    for p in pjnz_files:
        applicable = [s for s in simulations.scenarios if _scenario_applies(s, p.stem, selected_units)]
        if not applicable:
            continue
        for i, batch in enumerate(_batched(applicable, scenarios_per_file)):
            units.append((params_paths[p], p.stem, batch, end_years[p], f"{part_prefix}-{i}"))
    return units


def _report_progress(callbacks: RunCallbacks, pjnz_stem: str, ok: bool) -> None:
    """Advance progress for one finished scenario, success or failure."""
    if ok:
        callbacks.on_scenario_complete(pjnz_stem)
    else:
        callbacks.on_scenario_failed(pjnz_stem)


class _QueueProgress:
    """Picklable per-scenario progress reporter that forwards events to a queue.

    Passed to worker processes (which cannot call the main process's callbacks
    directly); the caller drains the queue and applies each ``(pjnz_stem, ok)``
    event via :func:`_report_progress`.
    """

    def __init__(self, queue: Queue) -> None:
        self._queue = queue

    def __call__(self, pjnz_stem: str, ok: bool) -> None:
        self._queue.put((pjnz_stem, ok))


def _write_failures_manifest(output_dir: Path, failures: list[WorkUnitResult]) -> None:
    """Write (or clear) the failures.json manifest and log a grouped summary.

    Writes ``output_dir/failures.json`` when there are failures so they can be
    re-run with ``--retry``; otherwise removes any stale manifest from a
    previous run.
    """
    manifest_path = output_dir / _FAILURES_FILENAME
    if not failures:
        manifest_path.unlink(missing_ok=True)
        return

    by_pjnz: dict[str, list[WorkUnitResult]] = {}
    for f in failures:
        by_pjnz.setdefault(f.pjnz, []).append(f)

    logger.warning(
        "{} scenario unit(s) failed across {} PJNZ file(s). Manifest written to {} (re-run with --retry).",
        len(failures),
        len(by_pjnz),
        manifest_path,
    )
    for pjnz in sorted(by_pjnz):
        ids = ", ".join(sorted(r.scenario_id for r in by_pjnz[pjnz]))
        logger.warning("  {}: {} scenario(s) failed: {}", pjnz, len(by_pjnz[pjnz]), ids)

    payload = {"failures": [{"pjnz": f.pjnz, "scenario_id": f.scenario_id, "error": f.error} for f in failures]}
    with open(manifest_path, "w") as fh:
        json.dump(payload, fh, indent=2)


def _run_pjnz_batch_star(args):
    return _run_pjnz_batch(*args)  # pragma: no cover (used when running in parallel)


def _warn_if_output_exists(output_dir: Path) -> None:
    existing = [d for d in output_dir.iterdir() if d.is_dir()]
    if existing:
        logger.warning(
            "output_dir {} already contains data from a previous run ({} indicator(s): {}). "
            "Files for matching (PJNZ, scenario) combinations will be overwritten. "
            "Delete existing output_dir to start completely fresh.",
            output_dir,
            len(existing),
            ", ".join(d.name for d in existing),
        )
