import datetime
import pickle
import tempfile
import threading
from multiprocessing import Manager
from pathlib import Path
from queue import Queue

from joblib import Parallel, delayed
from loguru import logger

from avenir_goals_scenario._cli.cli_utils import (
    configure_worker_logging,
    get_number_of_workers,
    make_log_queue_listener,
    make_progress,
    stop_log_queue_listener,
)
from avenir_goals_scenario._runner.output import write_scenario_results
from avenir_goals_scenario._runner.pjnz import find_pjnz_files, import_pjnz
from avenir_goals_scenario._runner.simulation import run_simulation
from avenir_goals_scenario.models import RunConfig, ScenarioSimulations
from avenir_goals_scenario.models.scenario_simulations import ScenarioSimulation


def _run_pjnz_scenario(
    params_path: str,
    pjnz_stem: str,
    scenario: ScenarioSimulation,
    config: RunConfig,
    end_year: int,
    log_queue: Queue | None,
) -> str:
    """Run all simulations for one PJNZ/scenario combination and write results.

    Args:
        params_path: Path to a pickle-dumped leapfrog params dict.
        pjnz_stem: Stem of the source PJNZ file, used for the output subdir.
        scenario: Scenario with all simulation draws to run.
        config: Run configuration.
        end_year: Final year of the projection (exclusive upper bound).
        log_queue: Queue shared with the main-process log listener thread, or
            ``None`` when running in the main process (``n_workers=1``).

    Returns:
        Stem of the source PJNZ file.
    """
    if log_queue is not None:
        configure_worker_logging(log_queue)

    with open(params_path, "rb") as f:
        params = pickle.load(f)  # noqa: S301 This only loads data we saved

    output_years = range(config.base_year, end_year)

    start = datetime.datetime.now()
    simulations_out = [
        run_simulation(params, simulation, config.output_indicators, output_years)
        for simulation in scenario.simulations
    ]
    elapsed_ms = (datetime.datetime.now() - start).total_seconds() * 1000
    logger.debug(
        "Scenario run finished {} ({} simulation(s)) for {} in {}ms",
        scenario.scenario_id,
        len(scenario.simulations),
        pjnz_stem,
        elapsed_ms,
    )
    write_scenario_results(scenario.scenario_id, pjnz_stem, simulations_out, config.output_dir)
    return pjnz_stem


def _execute(
    config: RunConfig,
    pjnz_files: list[Path],
    scenarios: ScenarioSimulations,
    effective_workers: int,
    log_queue: Queue | None,
    advance,
    on_import=None,
    on_imports_complete=None,
) -> None:
    """Run the parallel work units, calling advance(stem) as each completes."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        params_paths: dict[Path, str] = {}
        end_years: dict[Path, int] = {}
        logger.info("Loading {} PJNZ files", len(pjnz_files))
        for pjnz_path in pjnz_files:
            logger.debug("Importing {}", pjnz_path.name)
            leapfrog_params = import_pjnz(pjnz_path)
            dump_path = str(Path(tmp_dir) / f"{pjnz_path.stem}.pkl")
            with open(dump_path, "wb") as f:
                pickle.dump(leapfrog_params, f)
            params_paths[pjnz_path] = dump_path
            end_years[pjnz_path] = leapfrog_params["projection_end_year"] + 1
            if on_import is not None:
                on_import()

        if on_imports_complete is not None:
            on_imports_complete()

        work_units = [(params_paths[p], p.stem, s, end_years[p]) for p in pjnz_files for s in scenarios.scenarios]
        logger.info(
            "Running {} work unit(s) ({} PJNZ x {} scenario(s)) with n_workers={}",
            len(work_units),
            len(pjnz_files),
            len(scenarios.scenarios),
            config.n_workers,
        )
        logger.info("Running {} simulations per scenario", len(scenarios.scenarios[0].simulations))

        if effective_workers == 1:
            # If only 1 worker, then run this in process. Less overhead
            # to run within the single process.
            results = (
                _run_pjnz_scenario(params_path, pjnz_stem, scenario, config, end_year, log_queue=None)
                for params_path, pjnz_stem, scenario, end_year in work_units
            )
        else:
            results = Parallel(n_jobs=effective_workers, return_as="generator_unordered")(
                delayed(_run_pjnz_scenario)(params_path, pjnz_stem, scenario, config, end_year, log_queue)
                for params_path, pjnz_stem, scenario, end_year in work_units
            )

        for stem in results:
            advance(stem)


def run_scenario_analysis(config: RunConfig) -> Path:
    """Run scenario analysis across a directory of PJNZ files.

    Converts each PJNZ to leapfrog params once in the main process, dumps them
    to a temporary file using ``pickle.dump``, then distributes
    ``(PJNZ, scenario)`` work units across worker processes. Workers load
    params via ``pickle.load``.

    joblib avoids over-subscription of CPU resources automatically. It sets
    the number of CPUs available to BLAS runtime (which is used by numpy)
    automatically to the maximum cpu_count / n_jobs.

    Results are written to HDF5 files under ``config.output_dir``, one file
    per PJNZ/scenario combination at
    ``{output_dir}/{pjnz_stem}/scenario_{id}.h5``. Each file contains one
    dataset per indicator with shape ``(n_simulations, *indicator_dims)``.

    Args:
        config: Validated run configuration.

    Raises:
        FileNotFoundError: If no PJNZ files are found in ``config.pjnz_dir``.
        ValueError: If any output indicator is not present in the Goals output,
            or if a PJNZ file cannot be parsed.
    """
    config.output_dir.mkdir(exist_ok=True)
    pjnz_files = find_pjnz_files(config.pjnz_dir)
    scenarios = ScenarioSimulations.model_validate_json(config.scenario_path.read_bytes())
    effective_workers = get_number_of_workers(config)
    _execute(config, pjnz_files, scenarios, effective_workers, log_queue=None, advance=lambda _: None)
    return config.output_dir


def _run_scenario_analysis_cli(config: RunConfig) -> None:
    """CLI entry point — adds Rich progress bars and routes worker logs through
    the main-process Rich console to prevent display corruption.

    Args:
        config: Validated run configuration.
    """
    config.output_dir.mkdir(exist_ok=True)
    pjnz_files = find_pjnz_files(config.pjnz_dir)
    scenarios = ScenarioSimulations.model_validate_json(config.scenario_path.read_bytes())
    effective_workers = get_number_of_workers(config)
    n_scenarios = len(scenarios.scenarios)

    use_subprocess = effective_workers != 1
    mp_manager = Manager() if use_subprocess else None
    log_queue: Queue | None = mp_manager.Queue() if mp_manager is not None else None
    listener: threading.Thread | None = make_log_queue_listener(log_queue) if log_queue is not None else None

    try:
        progress = make_progress()
        with progress:
            import_task = progress.add_task("Importing PJNZ files", total=len(pjnz_files))

            def on_import() -> None:
                progress.advance(import_task)

            def on_imports_complete() -> None:
                progress.stop_task(import_task)
                for pjnz_path in pjnz_files:
                    progress.add_task(pjnz_path.stem, total=n_scenarios)

            def advance(stem: str) -> None:
                """Advance the scenario run progress bars"""
                for task in progress.tasks:
                    if task.description == stem:
                        progress.advance(task.id)
                        break

            _execute(
                config, pjnz_files, scenarios, effective_workers, log_queue, advance, on_import, on_imports_complete
            )
    finally:
        if log_queue is not None and listener is not None:
            stop_log_queue_listener(log_queue, listener)
        if mp_manager is not None:
            mp_manager.shutdown()
