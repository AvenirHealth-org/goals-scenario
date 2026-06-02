import numpy as np
from leapfrog_goals import run_goals
from SpectrumCommon.Const.RN import (
    RN_HRH,
    RN_HRH_F,
    RN_IDU,
    RN_IDU_F,
    RN_LRH,
    RN_LRH_F,
    RN_MRH,
    RN_MRH_F,
    RN_MSM,
    RN_MSM_F,
    RN_POC_CD4,
    RN_POC_VL,
    # RN_LongActingTreatment,
    RN_Adherence,
    RN_AHDTreatment,
    RN_AllRisk,
    RN_CureAdultsChildren,
    RN_Effectiveness,
    RN_POC_CD4_Int,
    RN_POC_VL_Int,
    RN_PrEPbNABs,
    RN_PrEPImplant,
    RN_PrEPInject1Mo,
    RN_PrEPInject2Mo,
    RN_PrEPInject6Mo,
    RN_PrepInterventions,
    RN_PrEPOralDaily,
    RN_PrEPOralMonthly,
    RN_PrEPOralPlusCon,
    RN_PrEPRing,
    RN_Single,
    RN_Vaccines,
)

from avenir_goals_scenario.models.scenario_simulations import InterventionSimulation

_interv_map = {
    "one_month_pill_for_prep": RN_PrEPOralMonthly,
    "daily_prep": RN_PrEPOralDaily,
    "one_month_injectable_prep": RN_PrEPInject1Mo,
    "two_month_injectable_prep": RN_PrEPInject2Mo,
    "six_month_injectable_prep": RN_PrEPInject6Mo,
    "oral_prep_plus_contraceptive": RN_PrEPOralPlusCon,
    "ring_prep": RN_PrEPRing,
    "implantable_prep": RN_PrEPImplant,
    "bnabs": RN_PrEPbNABs,
    "vaccine": RN_Vaccines,
    "cure": RN_CureAdultsChildren,
    "ahd_treatment": RN_AHDTreatment,
    "point_of_care_cd4_test": RN_POC_CD4_Int,
    "point_of_care_viral_load_test": RN_POC_VL_Int,
    # 'long_acting_treatment': RN_LongActingTreatment
}

_sex_map = {"all": 0, "male": 1, "female": 2}

_pop_map = {
    "low risk heterosexual": RN_LRH,
    "medium risk heterosexual": RN_MRH,
    "high risk heterosexual": RN_HRH,
    "people who inject drugs": RN_IDU,
    "men who have sex with men": RN_MSM,
}

_pop_map_female = {
    "low risk heterosexual": RN_LRH_F,
    "medium risk heterosexual": RN_MRH_F,
    "high risk heterosexual": RN_HRH_F,
    "people who inject drugs": RN_IDU_F,
    "men who have sex with men": RN_MSM_F,
}


def _apply_prep_intervention(
    leapfrog_params: dict,
    interv_id: int,
    efficacy: float,
    adherence: float,
    target_coverage: float,
    sex_idx: int,
    pop_type_idx: int,
    target_idx: int,
) -> None:
    prep_offset = interv_id - RN_PrEPOralDaily  # Index offset to align all PrEP interventions in the same slice
    sex_offset = sex_idx - 1 # BothSexes is removed so need to shift
    leapfrog_params["prep_effectiveness"][prep_offset, RN_Effectiveness] = efficacy
    leapfrog_params["prep_effectiveness"][prep_offset, RN_Adherence] = adherence
    leapfrog_params["prep_cov"][sex_offset, pop_type_idx, target_idx] = target_coverage


def _apply_vaccine_intervention(
    leapfrog_params: dict,
    target_coverage: float,
    pop_type_idx: int,
    sex: str,
    pop_type: str,
    target_idx: int,
) -> None:
    if leapfrog_params["rn_vac_cov_type"] == RN_Single:
        leapfrog_params["rn_vac_coverage"][RN_AllRisk, target_idx] = target_coverage
    else:
        if sex == "female":
            pop_type_idx = _pop_map_female[pop_type]
        leapfrog_params["rn_vac_coverage"][pop_type_idx, target_idx] = target_coverage


def _apply_cure_intervention(
    leapfrog_params: dict,
    target_coverage: float,
    pop_type_idx: int,
    sex: str,
    pop_type: str,
    target_idx: int,
) -> None:
    if leapfrog_params["rn_cure_cov_type"] == RN_Single:
        leapfrog_params["rn_cure_coverage"][RN_AllRisk, target_idx] = target_coverage
    else:
        if sex == "female":
            pop_type_idx = _pop_map_female[pop_type]
        leapfrog_params["rn_cure_coverage"][pop_type_idx, target_idx] = target_coverage


def _apply_poc_intervention(
    leapfrog_params: dict,
    interv_id: int,
    target_coverage: float,
    target_idx: int,
) -> None:
    if interv_id == RN_POC_CD4_Int:
        leapfrog_params["rn_poc_coverage"][RN_POC_CD4, target_idx] = target_coverage
    elif interv_id == RN_POC_VL_Int:
        leapfrog_params["rn_poc_coverage"][RN_POC_VL, target_idx] = target_coverage


def _apply_intervention_target(
    leapfrog_params: dict,
    interv_id: int,
    efficacy: float,
    adherence: float,
    target_coverage: float,
    sex: str,
    sex_idx: int,
    pop_type: str,
    pop_type_idx: int,
    target_idx: int,
) -> None:
    if interv_id in RN_PrepInterventions:
        _apply_prep_intervention(
            leapfrog_params,
            interv_id,
            efficacy,
            adherence,
            target_coverage,
            sex_idx,
            pop_type_idx,
            target_idx,
        )
        return

    if interv_id == RN_Vaccines:
        _apply_vaccine_intervention(
            leapfrog_params,
            target_coverage,
            pop_type_idx,
            sex,
            pop_type,
            target_idx,
        )
        return

    if interv_id == RN_CureAdultsChildren:
        _apply_cure_intervention(
            leapfrog_params,
            target_coverage,
            pop_type_idx,
            sex,
            pop_type,
            target_idx,
        )
        return

    if interv_id == RN_AHDTreatment:
        leapfrog_params["rn_ahd_treatment_coverage"][target_idx] = target_coverage
        return

    if interv_id in {RN_POC_CD4_Int, RN_POC_VL_Int}:
        _apply_poc_intervention(leapfrog_params, interv_id, target_coverage, target_idx)
        return

    leapfrog_params["rn_coverage"][interv_id, target_idx] = target_coverage


def apply_simulation(
    leapfrog_params: dict,
    simulation: dict[str, InterventionSimulation],
    interventions: list[InterventionSimulation],
) -> None:
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

    intervention_meta = {iv.id: iv for iv in interventions}
    for intervention_id, sim in simulation.items():
        params = sim.root
        efficacy = params["efficacy"]
        adherence = params["adherence"]
        target_coverage = params["target_coverage"]
        target_year = params["target_year"]
        target_idx = target_year - leapfrog_params["projection_start_year"]
        targets = intervention_meta[intervention_id].targets
        for target in targets:
            pop_type = target.population.lower()
            pop_type_idx = _pop_map[pop_type]
            sex = target.sex.lower()
            sex_idx = _sex_map[sex]
            interv_id = _interv_map[intervention_id]
            _apply_intervention_target(
                leapfrog_params,
                interv_id,
                efficacy,
                adherence,
                target_coverage,
                sex,
                sex_idx,
                pop_type,
                pop_type_idx,
                target_idx,
            )


def run_simulation(
    leapfrog_params: dict,
    simulation: dict[str, InterventionSimulation],
    output_indicators: list[str],
    output_years: range,
    interventions: list[InterventionSimulation],
) -> dict[str, np.ndarray]:
    """Run one simulation and return the requested output indicators.

    Applies the simulation parameters to *leapfrog_params* in-place, runs
    Goals, and returns the raw indicator arrays exactly as produced by
    ``run_goals`` - no dimension reduction.

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
    apply_simulation(leapfrog_params, simulation, interventions)
    goals_output = run_goals(leapfrog_params, output_years)
    return _extract_indicators(goals_output, output_indicators)


def _extract_indicators(goals_output: dict, output_indicators: list[str]) -> dict[str, np.ndarray]:
    missing = [k for k in output_indicators if k not in goals_output]
    if missing:
        err_msg = f"Output indicators not found in Goals output: {missing}"
        raise ValueError(err_msg)
    return {k: goals_output[k] for k in output_indicators}
