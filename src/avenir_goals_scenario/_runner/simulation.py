from typing import TypeAlias, TypedDict, assert_never, cast, get_args

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
    RN_DegreeAction,
    RN_Diff,
    RN_Duration,
    RN_Effectiveness,
    RN_Efficacy,
    RN_Infectiousness,
    RN_POC_CD4_Int,
    RN_POC_VL_Int,
    RN_PrEP_PEP,
    RN_PrEPbNABs,
    RN_PrEPImplant,
    RN_PrEPInject1Mo,
    RN_PrEPInject2Mo,
    RN_PrEPInject6Mo,
    RN_PrEPOralDaily,
    RN_PrEPOralMonthly,
    RN_PrEPOralPlusCon,
    RN_PrEPRing,
    RN_Progression,
    RN_Single,
    RN_TakeAction,
    RN_Type,
    RN_Vaccines,
)

from avenir_goals_scenario._runner.indicator_dims import CALCULATED_INDICATORS
from avenir_goals_scenario._scenario_generator.scenario_generator import _product_to_id
from avenir_goals_scenario.models.scenario_definition import (
    PrepProduct,
    RiskGroupNames,
    SexName,
)
from avenir_goals_scenario.models.scenario_simulations import InterventionOut, InterventionSimulation, TargetCoverage

# Opaque dict produced by import_pjnz() and modified in-place before running Goals.
LeapfrogParams = dict

_interv_map: dict[str, int] = {
    "one_month_pill_for_prep": RN_PrEPOralMonthly,
    "daily_prep": RN_PrEPOralDaily,
    "one_month_injectable_prep": RN_PrEPInject1Mo,
    "two_month_injectable_prep": RN_PrEPInject2Mo,
    "six_month_injectable_prep": RN_PrEPInject6Mo,
    "oral_prep_plus_contraceptive": RN_PrEPOralPlusCon,
    "ring_prep": RN_PrEPRing,
    "implantable_prep": RN_PrEPImplant,
    "bnabs": RN_PrEPbNABs,
    "pep": RN_PrEP_PEP,
    "vaccine": RN_Vaccines,
    "cure": RN_CureAdultsChildren,
    "ahd_treatment": RN_AHDTreatment,
    "point_of_care_cd4_test": RN_POC_CD4_Int,
    "point_of_care_viral_load_test": RN_POC_VL_Int,
    # "long_acting_treatment": RN_LongActingTreatment,
}


# Derived from PrepProduct so the two stay in sync automatically.
_PREP_IDS = frozenset(_product_to_id(p) for p in get_args(PrepProduct))


def _risk_group_idx(risk_group: RiskGroupNames, *, female: bool = False) -> int:
    """Return the leapfrog risk group index for *risk_group*.

    Pass ``female=True`` for vaccine/cure coverage arrays, where male and
    female populations have distinct indices. For PrEP, the sex dimension is
    a separate axis, so always use the default ``female=False``.
    """
    match risk_group:
        case "Low risk heterosexual":
            return RN_LRH_F if female else RN_LRH
        case "Medium risk heterosexual":
            return RN_MRH_F if female else RN_MRH
        case "High risk heterosexual":
            return RN_HRH_F if female else RN_HRH
        case "People who inject drugs":
            return RN_IDU_F if female else RN_IDU
        case "Men who have sex with men":
            return RN_MSM_F if female else RN_MSM
        case _ as unreachable:
            assert_never(unreachable)


def _sex_idx(sex: SexName) -> int:
    """Return the sex-axis index for ``prep_cov`` (Male=0, Female=1).

    Adding a new value to ``SexName`` in scenario_definition.py will cause a
    static type error here until the new case is handled.
    """
    match sex:
        case "Male":
            return 0
        case "Female":
            return 1
        case "Both":
            msg = "'Both' sex is not yet supported in per-sex coverage arrays."
            raise NotImplementedError(msg)
        case _ as unreachable:
            assert_never(unreachable)


# ---------------------------------------------------------------------------
# Typed shapes for sampled draw dicts (mirrors *Parameters models but with
# concrete values instead of distributions).
# ---------------------------------------------------------------------------


class _PrepDraw(TypedDict):
    efficacy: float
    adherence: float
    target_year: int
    target_coverages: list[TargetCoverage]


class _VaccineDraw(TypedDict):
    target_year: int
    target_coverages: list[TargetCoverage]
    reduction_in_susceptibility: float
    reduction_in_infectiousness: float
    increase_in_progression_time_to_aids: float
    vaccine_duration_years: float
    vaccine_action_type: str
    targeting: str


class _CureDraw(TypedDict):
    target_year: int
    target_coverages: list[TargetCoverage]
    efficacy: float
    duration_of_cure: float


class _AHDTreatmentDraw(TypedDict):
    target_year: int
    target_coverage: float
    reduction_in_mortality: float


class _POCTestDraw(TypedDict):
    target_year: int
    target_coverage: float
    effect: float


class _AdultARTDraw(TypedDict):
    target_year: int
    target_coverages: list[TargetCoverage]


_Draw: TypeAlias = _PrepDraw | _VaccineDraw | _CureDraw | _AHDTreatmentDraw | _POCTestDraw | _AdultARTDraw


def _target_year_idx(lp: LeapfrogParams, draw: _Draw) -> int:
    """Convert ``draw["target_year"]`` to a zero-based year index into leapfrog arrays."""
    return int(draw["target_year"]) - lp["projection_start_year"]


# ---------------------------------------------------------------------------
# Per-intervention application functions
# ---------------------------------------------------------------------------


def _apply_all_prep(
    lp: LeapfrogParams,
    prep_draws: list[tuple[str, dict]],
) -> None:
    """Apply all PrEP products together, computing prep_cov and prep_method_mix.

    Coverage for each (sex, risk_group, year) is the sum across all products targeting
    that population. prep_method_mix holds each product's share of that total.
    """
    # (sex_idx, rg_idx, method_offset, year_idx) → coverage
    coverage_by_method: dict[tuple[int, int, int, int], float] = {}

    for iv_id, draw in prep_draws:
        method_offset = _interv_map[iv_id] - RN_PrEPOralDaily
        year_idx = int(draw["target_year"]) - lp["projection_start_year"]
        lp["prep_effectiveness"][method_offset, RN_Effectiveness] = draw["efficacy"]
        lp["prep_effectiveness"][method_offset, RN_Adherence] = draw["adherence"]
        for tc in draw["target_coverages"]:
            key = (
                _sex_idx(cast(SexName, tc.sex)),
                _risk_group_idx(cast(RiskGroupNames, tc.risk_group)),
                method_offset,
                year_idx,
            )
            coverage_by_method[key] = coverage_by_method.get(key, 0.0) + tc.coverage

    # Sum per (sex, rg, year)
    totals: dict[tuple[int, int, int], float] = {}
    for (sex_idx, rg_idx, _, year_idx), cov in coverage_by_method.items():
        k = (sex_idx, rg_idx, year_idx)
        totals[k] = totals.get(k, 0.0) + cov

    for (sex_idx, rg_idx, year_idx), total in totals.items():
        lp["prep_cov"][sex_idx, rg_idx, year_idx] = min(total, 1.0)
        lp["prep_method_mix"][sex_idx, rg_idx, :, year_idx] = 0.0

    for (sex_idx, rg_idx, method_offset, year_idx), cov in coverage_by_method.items():
        total = totals[(sex_idx, rg_idx, year_idx)]
        if total > 0:
            lp["prep_method_mix"][sex_idx, rg_idx, method_offset, year_idx] = cov / total


def _apply_vaccine(lp: LeapfrogParams, draw: _VaccineDraw) -> None:
    year_idx = _target_year_idx(lp, draw)
    for tc in draw["target_coverages"]:
        if tc.risk_group == "PLHIV":
            lp["rn_vac_cov_type"] = RN_Single
            lp["rn_vac_coverage_rg"][RN_AllRisk, year_idx] = tc.coverage
        elif tc.sex == "Both" or tc.sex is None:
            lp["rn_vac_cov_type"] = RN_Diff
            lp["rn_vac_coverage_rg"][_risk_group_idx(cast(RiskGroupNames, tc.risk_group), female=False), year_idx] = (
                tc.coverage
            )
            lp["rn_vac_coverage_rg"][_risk_group_idx(cast(RiskGroupNames, tc.risk_group), female=True), year_idx] = (
                tc.coverage
            )
        else:
            lp["rn_vac_cov_type"] = RN_Diff
            lp["rn_vac_coverage_rg"][
                _risk_group_idx(cast(RiskGroupNames, tc.risk_group), female=(tc.sex == "Female")), year_idx
            ] = tc.coverage
    lp["rn_vac_params"][RN_Efficacy] = draw["reduction_in_susceptibility"]
    lp["rn_vac_params"][RN_Infectiousness] = draw["reduction_in_infectiousness"]
    lp["rn_vac_params"][RN_Progression] = draw["increase_in_progression_time_to_aids"]
    lp["rn_vac_params"][RN_Duration] = draw["vaccine_duration_years"]

    if draw["vaccine_action_type"] == "Take":
        lp["rn_vac_params"][RN_Type] = RN_TakeAction - RN_TakeAction  # start count at 0 in lf
    elif draw["vaccine_action_type"] == "Degree":
        lp["rn_vac_params"][RN_Type] = RN_DegreeAction - RN_TakeAction
    else:
        msg = (
            'Invalid value for vaccine intervention "vaccine_action_type" '
            f"received {draw['vaccine_action_type']} must be either "
            '"Take" or "Degree".'
        )
        raise ValueError(msg)

    if draw["targeting"] == "Vaccinate without HIV testing":
        lp["rn_vac_targetting"] = 0  # targeting turned off
    elif draw["targeting"] == "Vaccinate only HIV-negative individuals":
        lp["rn_vac_targetting"] = 1  # targeting turned on
    else:
        msg = (
            'Invalid value for vaccine intervention "targeting" '
            f"received {draw['targeting']} must be either "
            '"Vaccinate without HIV testing" or '
            '"Vaccinate only HIV-negative individuals".'
        )
        raise ValueError(msg)


def _apply_cure(lp: LeapfrogParams, draw: _CureDraw) -> None:
    year_idx = _target_year_idx(lp, draw)
    for tc in draw["target_coverages"]:
        if tc.risk_group == "PLHIV":
            lp["rn_cure_coverage_type"] = RN_Single
            lp["rn_cure_coverage_rg"][RN_AllRisk, year_idx] = tc.coverage
        elif tc.sex == "Both" or tc.sex is None:
            lp["rn_cure_coverage_type"] = RN_Diff
            lp["rn_cure_coverage_rg"][_risk_group_idx(cast(RiskGroupNames, tc.risk_group), female=False), year_idx] = (
                tc.coverage
            )
            lp["rn_cure_coverage_rg"][_risk_group_idx(cast(RiskGroupNames, tc.risk_group), female=True), year_idx] = (
                tc.coverage
            )
        else:
            lp["rn_cure_coverage_type"] = RN_Diff
            lp["rn_cure_coverage_rg"][
                _risk_group_idx(cast(RiskGroupNames, tc.risk_group), female=(tc.sex == "Female")), year_idx
            ] = tc.coverage
    lp["rn_cure_effect"][RN_Efficacy] = draw["efficacy"]
    lp["rn_cure_effect"][RN_Duration] = draw["duration_of_cure"]


def _apply_ahd(lp: LeapfrogParams, draw: _AHDTreatmentDraw) -> None:
    year_idx = _target_year_idx(lp, draw)
    # TODO: fix typo in adh see https://trello.com/c/fEiv46rE
    lp["rn_adh_treat_cov"][year_idx] = draw["target_coverage"]
    lp["rn_adh_treat_reduc_mort"] = draw["reduction_in_mortality"]


def _apply_adult_art(lp: LeapfrogParams, draw: _AdultARTDraw) -> None:
    year_idx = _target_year_idx(lp, draw)
    for tc in draw["target_coverages"]:
        if tc.sex == "Both":
            sex_indices = [0, 1]
        elif tc.sex == "Male":
            sex_indices = [0]
        else:
            sex_indices = [1]
        for sex_idx in sex_indices:
            lp["adults_on_art"][sex_idx, year_idx] = tc.coverage
            lp["adults_on_art_is_percent"][sex_idx, year_idx] = 1


def _apply_poc(lp: LeapfrogParams, poc_type: int, draw: _POCTestDraw) -> None:
    """Apply point-of-care test coverage. *poc_type* is ``RN_POC_CD4_Int`` or ``RN_POC_VL_Int``."""
    year_idx = _target_year_idx(lp, draw)
    rn_poc = RN_POC_CD4 if poc_type == RN_POC_CD4_Int else RN_POC_VL
    lp["rn_poc_cov"][rn_poc, year_idx] = draw["target_coverage"]
    lp["rn_poc_effect"][rn_poc] = draw["effect"]


def _dispatch(lp: LeapfrogParams, iv: InterventionOut, draw: dict) -> None:
    match iv.id:
        case "vaccine":
            _apply_vaccine(lp, cast(_VaccineDraw, draw))
        case "cure":
            _apply_cure(lp, cast(_CureDraw, draw))
        case "ahd_treatment":
            _apply_ahd(lp, cast(_AHDTreatmentDraw, draw))
        case "point_of_care_viral_load_test":
            _apply_poc(lp, RN_POC_VL_Int, cast(_POCTestDraw, draw))
        case "point_of_care_cd4_test":
            _apply_poc(lp, RN_POC_CD4_Int, cast(_POCTestDraw, draw))
        case "long_acting_treatment":
            raise NotImplementedError("Long-acting treatment application is not yet implemented.")
        case "adult_art":
            _apply_adult_art(lp, cast(_AdultARTDraw, draw))
        case _:
            msg = f"Unknown intervention: {iv.id!r}"
            raise ValueError(msg)


def apply_simulation(
    leapfrog_params: LeapfrogParams,
    interventions: list[InterventionOut],
    simulation: dict[str, InterventionSimulation],
) -> None:
    """Apply one sampled draw of intervention parameters to *leapfrog_params* in-place.

    Args:
        leapfrog_params: Goals model parameter dict from ``import_pjnz``. Modified in-place.
        interventions: Intervention metadata for the current scenario.
        simulation: Mapping of intervention ID → sampled parameter values for one draw.
    """
    meta = {iv.id: iv for iv in interventions}
    prep_draws: list[tuple[str, dict]] = []
    for intervention_id, sim in simulation.items():
        iv = meta[intervention_id]
        if intervention_id in _PREP_IDS:
            prep_draws.append((intervention_id, sim.root))
        else:
            _dispatch(leapfrog_params, iv, sim.root)
    if prep_draws:
        _apply_all_prep(leapfrog_params, prep_draws)


def run_simulation(
    leapfrog_params: LeapfrogParams,
    interventions: list[InterventionOut],
    simulation: dict[str, InterventionSimulation],
    output_indicators: list[str],
    output_years: range,
) -> dict[str, np.ndarray]:
    """Apply a sampled draw, run Goals, and return the requested indicator arrays.

    Applies *simulation* to *leapfrog_params* in-place, runs Goals, and returns
    the raw indicator arrays as produced by ``run_goals`` — no dimension reduction.

    Args:
        leapfrog_params: Goals model parameter dict for one PJNZ. Modified in-place.
        interventions: Intervention metadata for the current scenario.
        simulation: Sampled parameter values for one draw.
        output_indicators: Indicator names to extract from Goals output.
        output_years: Year range passed to ``run_goals``.

    Returns:
        Mapping of indicator name → NumPy array (last axis indexed by year).

    Raises:
        ValueError: If any indicator in *output_indicators* is absent from Goals output.
    """
    apply_simulation(leapfrog_params, interventions, simulation)
    leapfrog_params["hc_nosocomial"] = leapfrog_params["hc_nosocomial_infections_by_age"][0, :]
    goals_output = run_goals(leapfrog_params, output_years)
    return _extract_indicators(goals_output, output_indicators)


def _extract_indicators(goals_output: dict, output_indicators: list[str]) -> dict[str, np.ndarray]:
    missing = [k for k in output_indicators if k not in goals_output and k not in CALCULATED_INDICATORS]
    if missing:
        msg = f"Output indicators not found in Goals output: {missing}"
        raise ValueError(msg)

    def get_indicator(k: str):
        if k == "p_prevalence":
            denom = np.where(goals_output["p_totpop"] == 0, np.nan, goals_output["p_totpop"])
            return goals_output["p_hivpop"] / denom
        elif k == "p_incidence":
            hiv_neg = goals_output["p_totpop"] - goals_output["p_hivpop"]
            denom = np.where(hiv_neg == 0, np.nan, hiv_neg)
            return goals_output["p_totpop"] / denom
        else:
            return goals_output[k]

    return {k: get_indicator(k) for k in output_indicators}
