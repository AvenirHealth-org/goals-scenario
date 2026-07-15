import datetime
import json
import os
import pickle
import tempfile
from multiprocessing import Pool
from pathlib import Path
from queue import Queue

from loguru import logger

from avenir_goals_scenario._runner.indicator_dims import build_indicator_dims
from avenir_goals_scenario._runner.output import (
    check_indicator_dims,
    consolidate_metadata,
    remove_scenario_partitions,
    write_scenario_results,
)
from avenir_goals_scenario._runner.pjnz import (
    ART_ENTRY_INITIATION_RATE,
    find_pjnz_files,
    import_pjnz,
    uses_art_initiation_rate,
)
from avenir_goals_scenario._runner.simulation import run_simulation
from avenir_goals_scenario._runner.utils import RunCallbacks, RunResult, WorkUnitResult, get_effective_workers
from avenir_goals_scenario.models import RunConfig, ScenarioSimulations
from avenir_goals_scenario.models.scenario_simulations import ScenarioSimulation

_FAILURES_FILENAME = "failures.json"


def _fmt_error(e: Exception) -> str:
    """Short error message, falling back to the exception type name."""
    return str(e) or type(e).__name__


def _run_pjnz_scenario(
    params_path: str,
    pjnz_stem: str,
    scenario: ScenarioSimulation,
    config: RunConfig,
    end_year: int,
    log_queue=None,
) -> WorkUnitResult:
    """Run all simulations for one PJNZ/scenario combination and write results.

    Per-unit failures are non-fatal: any exception while simulating or writing
    is caught, logged, and returned as a failed :class:`WorkUnitResult` so the
    overall run can continue with the remaining units.
    """
    if log_queue is not None:
        from avenir_goals_scenario._cli.cli_utils import configure_worker_logging

        configure_worker_logging(log_queue)

    try:
        with open(params_path, "rb") as f:
            params = pickle.load(f)  # noqa: S301 - only loads data we saved ourselves

        output_years = range(config.base_year, end_year + 1)

        start = datetime.datetime.now()
        simulations_out = [
            run_simulation(params, scenario.interventions, simulation, config.output_indicators, output_years)
            for simulation in scenario.simulations
        ]
        elapsed_ms = (datetime.datetime.now() - start).total_seconds() * 1000
        logger.debug(
            "Scenario run finished {} ({} simulation(s)) for {} in {}ms",
            scenario.id,
            len(scenario.simulations),
            pjnz_stem,
            elapsed_ms,
        )
        write_scenario_results(
            scenario.id,
            pjnz_stem,
            simulations_out,
            config.output_dir,
            indicator_dims=build_indicator_dims(config.base_year),
        )
    except Exception as e:
        error = _fmt_error(e)
        logger.warning("Scenario {} failed for {}: {}", scenario.id, pjnz_stem, error)
        # Drop any partial output so consolidate_metadata stays consistent.
        remove_scenario_partitions(config.output_dir, pjnz_stem, scenario.id)
        return WorkUnitResult(pjnz=pjnz_stem, scenario_id=scenario.id, ok=False, error=error)

    return WorkUnitResult(pjnz=pjnz_stem, scenario_id=scenario.id, ok=True)


def _scenarios_use_adult_art(simulations: ScenarioSimulations) -> bool:
    """Return True if any scenario contains an 'Adult ART' intervention."""
    return any(iv.id == "adult_art" for s in simulations.scenarios for iv in s.interventions)


def _dump_pjnz_files(
    pjnz_files: list[Path],
    tmp_dir: str,
    cb: RunCallbacks,
    warn_adult_art: bool = False,
) -> tuple[dict[Path, str], dict[Path, int]]:
    """Import each PJNZ, pickle it to tmp_dir, return paths and end years.

    When ``warn_adult_art`` is set (some scenario uses 'Adult ART'), a warning is
    logged for each PJNZ that is not in ART initiation-rate mode, since 'Adult
    ART' interventions have no effect for it.
    """
    params_paths: dict[Path, str] = {}
    end_years: dict[Path, int] = {}
    logger.info("Loading {} PJNZ file(s)", len(pjnz_files))
    for pjnz_path in pjnz_files:
        logger.debug("Importing {}", pjnz_path.name)
        leapfrog_params = import_pjnz(pjnz_path)
        if warn_adult_art and not uses_art_initiation_rate(leapfrog_params):
            logger.warning(
                "PJNZ '{}' is not in ART initiation-rate mode (art_entry_option != {}); "
                "'Adult ART' interventions will not be applied for it.",
                pjnz_path.name,
                ART_ENTRY_INITIATION_RATE,
            )
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
    to a temporary file using ``pickle.dump``, then distributes
    ``(PJNZ, scenario)`` work units across worker processes. Workers load
    params via ``pickle.load``.

    Results are written to Parquet files under ``config.output_dir``, one file
    per PJNZ/scenario combination at
    ``{output_dir}/{pjnz_stem}/scenario_{id}.parquet``. Each file contains one
    dataset per indicator with shape ``(n_simulations, *indicator_dims)``.

    Individual ``(PJNZ, scenario)`` units that fail are logged and skipped
    rather than aborting the run; the rest still complete. Failed units are
    recorded in the returned :class:`RunResult` and written to a
    ``failures.json`` manifest under ``config.output_dir`` for re-running. PJNZ
    *import* failures remain fatal and raise.

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
) -> RunResult:
    """Internal run_scenario_analysis function.

    Args:
        config: Validated run configuration.
        simulations: Pre-drawn scenario simulations.
        callbacks: Hooks for progress reporting, can be no-op.
        log_queue: Optional queue to pass to _run_pjnz_scenario when running
          in parallel so logs can be raised to the same console as progress
          bars when run via CLI.
        selected_units: Optional set of ``(pjnz_stem, scenario_id)`` pairs to
          restrict the run to (used by ``--retry``). ``None`` runs every
          applicable unit.

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
    warn_adult_art = _scenarios_use_adult_art(simulations)
    with tempfile.TemporaryDirectory() as tmp_dir:
        params_paths, end_years = _dump_pjnz_files(pjnz_files, tmp_dir, callbacks, warn_adult_art)

        effective_workers = get_effective_workers(config)
        logger.info(
            "Using {} worker(s) (cpu_count={}, configured n_workers={})",
            effective_workers,
            os.cpu_count(),
            config.n_workers,
        )
        work_units = [
            (params_paths[p], p.stem, s, end_years[p])
            for p in pjnz_files
            for s in simulations.scenarios
            if _scenario_applies(s, p.stem, selected_units)
        ]
        logger.info(
            "Running {} work unit(s) ({} PJNZ file(s), {} scenario(s), n_workers={})",
            len(work_units),
            len(pjnz_files),
            len(simulations.scenarios),
            effective_workers,
        )
        logger.info("Running {} simulations per scenario", len(simulations.scenarios[0].simulations))

        if effective_workers == 1:
            for params_path, pjnz_stem, scenario, end_year in work_units:
                result = _run_pjnz_scenario(params_path, pjnz_stem, scenario, config, end_year)
                results.append(result)
                _report_unit(result, callbacks)
        else:
            packed = [
                (params_path, pjnz_stem, scenario, config, end_year, log_queue)
                for params_path, pjnz_stem, scenario, end_year in work_units
            ]
            with Pool(processes=effective_workers) as pool:
                for result in pool.imap_unordered(_run_pjnz_scenario_star, packed):
                    results.append(result)
                    _report_unit(result, callbacks)

    callbacks.on_run_complete()

    failures = [r for r in results if not r.ok]
    _write_failures_manifest(config.output_dir, failures)

    consolidate_metadata(config.output_dir)
    logger.info("Done. Results written to {}", config.output_dir)
    return RunResult(output_dir=config.output_dir, failures=failures)


def _report_unit(result: WorkUnitResult, callbacks: RunCallbacks) -> None:
    """Advance progress for a finished unit, success or failure."""
    if result.ok:
        callbacks.on_scenario_complete(result.pjnz)
    else:
        callbacks.on_scenario_failed(result.pjnz)


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


def _run_pjnz_scenario_star(args):
    return _run_pjnz_scenario(*args)  # pragma: no cover (used when running in parallel)


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
