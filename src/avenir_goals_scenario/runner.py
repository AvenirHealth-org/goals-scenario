from pathlib import Path

from leapfrog_goals import get_goals_ss
from loguru import logger
from SpectrumCommon.Const.PJ.PJNTags import PJN_FinalYearTag

from avenir_goals_scenario._runner.output import write_scenario_results
from avenir_goals_scenario._runner.pjnz import find_pjnz_files, import_pjnz
from avenir_goals_scenario._runner.simulation import run_simulation
from avenir_goals_scenario.models import RunConfig, ScenarioSimulations


def run_scenario_analysis(config: RunConfig) -> Path:
    """Run scenario analysis across a directory of PJNZ files.

    For every combination of PJNZ file, scenario, and simulation draw, this
    function:

    1. Imports the PJNZ file into a modvars dict.
    2. Applies the sampled intervention parameters via
       :func:`~avenir_goals_scenario._runner.simulation.apply_simulation`.
    3. Converts modvars to Leapfrog parameters and runs the Goals model.
    4. Extracts the requested output indicators.

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
    pjnz_files = find_pjnz_files(config.pjnz_dir)
    logger.info("Found {} PJNZ file(s) in {}", len(pjnz_files), config.pjnz_dir)

    scenarios = ScenarioSimulations.model_validate_json(config.scenario_path.read_bytes())
    ss = get_goals_ss()

    for pjnz_path in pjnz_files:
        logger.debug("Importing {}", pjnz_path.name)
        modvars_base = import_pjnz(pjnz_path)
        output_years = range(config.base_year, modvars_base[PJN_FinalYearTag] + 1)

        for scenario in scenarios.scenarios:
            logger.info(
                "Running scenario {} ({} simulation(s)) for {}",
                scenario.scenario_id,
                len(scenario.simulations),
                pjnz_path.name,
            )
            sim_arrays = {
                indicator: [
                    run_simulation(modvars_base, simulation, config.output_indicators, output_years, ss)[indicator]
                    for simulation in scenario.simulations
                ]
                for indicator in config.output_indicators
            }
            out_path = write_scenario_results(scenario.scenario_id, pjnz_path.stem, sim_arrays, config.output_dir)
            logger.info("Written {}", out_path)

    return config.output_dir
