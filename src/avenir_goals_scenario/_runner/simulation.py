import copy

import numpy as np
from leapfrog_goals import run_goals

from avenir_goals_scenario._leapfrog.LeapfrogDataMapping import modvars_to_leapfrog
from avenir_goals_scenario.models.scenario_simulations import InterventionSimulation


def apply_simulation(modvars: dict, simulation: dict[str, InterventionSimulation]) -> None:
    """Apply sampled intervention parameters to modvars.

    This is the integration point between scenario simulation data and the
    Goals model.  Implement this function to translate the sampled values
    (efficacy, adherence, target coverage, target year) for each intervention
    into the corresponding modvars entries before the model is run.

    Args:
        modvars: Mutable modvars dict imported from a PJNZ file.  Modify
            in-place to reflect the scenario parameters.
        simulation: Mapping of intervention ID to sampled parameter values for
            one draw.
    """


def run_simulation(
    modvars_base: dict,
    simulation: dict[str, InterventionSimulation],
    output_indicators: list[str],
    output_years: range,
    ss: dict,
) -> dict[str, np.ndarray]:
    """Run one simulation and return the requested output indicators.

    Makes a deep copy of *modvars_base*, applies the simulation parameters,
    converts to Leapfrog format, runs Goals, and returns the raw indicator
    arrays exactly as produced by ``run_goals`` — no dimension reduction.

    Args:
        modvars_base: Modvars imported from a PJNZ file.  Not mutated.
        simulation: Sampled intervention parameters for one draw.
        output_indicators: Indicator names to extract from Goals output.
        output_years: Year range passed to ``run_goals``.
        ss: Goals state-space dict from ``leapfrog_goals.get_goals_ss``.

    Returns:
        Dict mapping each indicator name to a NumPy array whose last axis is
        indexed by year.  All other dimensions are preserved as-is.

    Raises:
        ValueError: If any of *output_indicators* are not present in the
            Goals output.
    """
    modvars = copy.deepcopy(modvars_base)
    apply_simulation(modvars, simulation)
    leapfrog_params = modvars_to_leapfrog(modvars, ss)
    # Temporarily add in required input data for this in-progress
    # version of leapfrog goals
    leapfrog_params["ex_input"] = np.full((ss["pAG"], ss["NS"]), 1)
    goals_output = run_goals(leapfrog_params, output_years)
    return _extract_indicators(goals_output, output_indicators)


def _extract_indicators(goals_output: dict, output_indicators: list[str]) -> dict[str, np.ndarray]:
    missing = [k for k in output_indicators if k not in goals_output]
    if missing:
        err_msg = f"Output indicators not found in Goals output: {missing}"
        raise ValueError(err_msg)
    return {k: goals_output[k] for k in output_indicators}
