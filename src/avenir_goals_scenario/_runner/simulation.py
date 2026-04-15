import numpy as np
from leapfrog_goals import run_goals

from avenir_goals_scenario.models.scenario_simulations import InterventionSimulation


def apply_simulation(leapfrog_params: dict, simulation: dict[str, InterventionSimulation]) -> None:
    """Apply sampled intervention parameters to leapfrog_params.

    This is the integration point between scenario simulation data and the
    Goals model.  Implement this function to translate the sampled values
    (efficacy, adherence, target coverage, target year) for each intervention
    into the corresponding leapfrog_params entries before the model is run.

    Args:
        leapfrog_params: Mutable leapfrog params dict.  Modify in-place to
            reflect the scenario parameters.
        simulation: Mapping of intervention ID to sampled parameter values for
            one draw.
    """


def run_simulation(
    leapfrog_params: dict,
    simulation: dict[str, InterventionSimulation],
    output_indicators: list[str],
    output_years: range,
) -> dict[str, np.ndarray]:
    """Run one simulation and return the requested output indicators.

    Applies the simulation parameters to *leapfrog_params* in-place, runs
    Goals, and returns the raw indicator arrays exactly as produced by
    ``run_goals`` — no dimension reduction.

    Args:
        leapfrog_params: Leapfrog params for one PJNZ.
        simulation: Sampled intervention parameters for one draw.
        output_indicators: Indicator names to extract from Goals output.
        output_years: Year range passed to ``run_goals``.

    Returns:
        Dict mapping each indicator name to a NumPy array whose last axis is
        indexed by year.  All other dimensions are preserved as-is.

    Raises:
        ValueError: If any of *output_indicators* are not present in the
            Goals output.
    """
    apply_simulation(leapfrog_params, simulation)
    goals_output = run_goals(leapfrog_params, output_years)
    return _extract_indicators(goals_output, output_indicators)


def _extract_indicators(goals_output: dict, output_indicators: list[str]) -> dict[str, np.ndarray]:
    missing = [k for k in output_indicators if k not in goals_output]
    if missing:
        err_msg = f"Output indicators not found in Goals output: {missing}"
        raise ValueError(err_msg)
    return {k: goals_output[k] for k in output_indicators}
