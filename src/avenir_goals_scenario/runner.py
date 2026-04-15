import datetime
import pickle
import tempfile
from pathlib import Path

from joblib import Parallel, delayed
from loguru import logger

from avenir_goals_scenario._runner.output import write_scenario_results
from avenir_goals_scenario._runner.pjnz import find_pjnz_files, import_pjnz
from avenir_goals_scenario._runner.simulation import run_simulation
from avenir_goals_scenario._runner.worker_utils import (
    get_number_of_workers,
)
from avenir_goals_scenario.models import RunConfig, ScenarioSimulations
from avenir_goals_scenario.models.scenario_simulations import ScenarioSimulation


def _run_pjnz_scenario(
    params_path: str,
    pjnz_stem: str,
    scenario: ScenarioSimulation,
    config: RunConfig,
    end_year: int,
) -> Path:
    """Run all simulations for one PJNZ/scenario combination and write results.

    Loads leapfrog params from a pickle dump. And runs all simulations for the
    PJNZ and scenario.

    Args:
        params_path: Path to a pickle-dumped leapfrog params dict.
        pjnz_stem: Stem of the source PJNZ file, used for the output subdir.
        scenario: Scenario with all simulation draws to run.
        config: Run configuration.
        end_year: Final year of the projection (exclusive upper bound).

    Returns:
        Path to the written HDF5 file.
    """

    with open(params_path, "rb") as f:
        params = pickle.load(f)  # noqa: S301 This only loads data we saved

    output_years = range(config.base_year, end_year)

    start = datetime.datetime.now()
    simulations_out = [
        run_simulation(params, simulation, config.output_indicators, output_years)
        for simulation in scenario.simulations
    ]
    elapsed_ms = (datetime.datetime.now() - start).total_seconds() * 1000
    logger.info(
        "Scenario run finished {} ({} simulation(s)) for {} in {}ms",
        scenario.scenario_id,
        len(scenario.simulations),
        pjnz_stem,
        elapsed_ms,
    )
    return write_scenario_results(scenario.scenario_id, pjnz_stem, simulations_out, config.output_dir)


def run_scenario_analysis(config: RunConfig) -> Path:
    """Run scenario analysis across a directory of PJNZ files.

    Converts each PJNZ to leapfrog params once in the main process, dumps them
    to a temporary file using `pickle.dump`, then distributes
    ``(PJNZ, scenario)`` work units across worker processes.  Workers load
    params `pickle.load`.

    joblib avoids over-subscription of CPU resources automatically. It sets
    the number of CPUs avaialble to BLAS runtime (which is used by numpy)
    automatically to the maximum cpu_count / n_jobs. We don't have to
    control this manually.

    Results are written to HDF5 files under ``config.output_dir``, one file
    per PJNZ/scenario combination at
    ``{output_dir}/{pjnz_stem}/scenario_{id}.h5``.  Each file contains one
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

    with tempfile.TemporaryDirectory() as tmp_dir:
        params_paths: dict[Path, str] = {}
        end_years: dict[Path, int] = {}
        for pjnz_path in pjnz_files:
            logger.debug("Importing {}", pjnz_path.name)
            leapfrog_params = import_pjnz(pjnz_path)
            dump_path = str(Path(tmp_dir) / f"{pjnz_path.stem}.pkl")
            with open(dump_path, "wb") as f:
                pickle.dump(leapfrog_params, f)
            params_paths[pjnz_path] = dump_path
            end_years[pjnz_path] = leapfrog_params["projection_end_year"] + 1

        work_units = [
            (params_paths[pjnz_path], pjnz_path.stem, scenario, end_years[pjnz_path])
            for pjnz_path in pjnz_files
            for scenario in scenarios.scenarios
        ]
        logger.info(
            "Running {} work unit(s) ({} PJNZ x {} scenario(s)) with n_workers={}",
            len(work_units),
            len(pjnz_files),
            len(scenarios.scenarios),
            config.n_workers,
        )

        if effective_workers == 1:
            # If only 1 worker, then run this in process. Less overhead
            # to run within the single process.
            for params_path, pjnz_stem, scenario, end_year in work_units:
                _run_pjnz_scenario(params_path, pjnz_stem, scenario, config, end_year)
        else:
            Parallel(n_jobs=effective_workers)(
                delayed(_run_pjnz_scenario)(params_path, pjnz_stem, scenario, config, end_year)
                for params_path, pjnz_stem, scenario, end_year in work_units
            )

    return config.output_dir
