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
    RN_Vaccines,
)

from avenir_goals_scenario._scenario_generator.scenario_generator import _product_to_id
from avenir_goals_scenario.models import PopulationTarget
from avenir_goals_scenario.models.scenario_definition import PopulationName, PrepProduct, SexName
from avenir_goals_scenario.models.scenario_simulations import InterventionOut, InterventionSimulation

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


def _pop_idx(pop: PopulationName, *, female: bool = False) -> int:
    """Return the leapfrog population index for *pop*.

    Pass ``female=True`` for vaccine/cure coverage arrays, where male and
    female populations have distinct indices. For PrEP, the sex dimension is
    a separate axis, so always use the default ``female=False``.
    """
    match pop:
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
    target_coverage: float
    target_year: int


class _VaccineDraw(TypedDict):
    target_year: int
    target_coverage: float
    reduction_in_susceptibility: float
    reduction_in_infectiousness: float
    increase_in_progression_time_to_aids: float
    vaccine_duration_years: float
    vaccine_action_type: str
    targeting: str


class _CureDraw(TypedDict):
    target_year: int
    target_coverage: float
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


_Draw: TypeAlias = _PrepDraw | _VaccineDraw | _CureDraw | _AHDTreatmentDraw | _POCTestDraw


def _target_year_idx(lp: LeapfrogParams, draw: _Draw) -> int:
    """Convert ``draw["target_year"]`` to a zero-based year index into leapfrog arrays."""
    return int(draw["target_year"]) - lp["projection_start_year"]


# ---------------------------------------------------------------------------
# Per-intervention application functions
# ---------------------------------------------------------------------------


def _apply_prep(lp: LeapfrogParams, iv_id: str, targets: list[PopulationTarget], draw: _PrepDraw) -> None:
    year_idx = _target_year_idx(lp, draw)
    prep_offset = _interv_map[iv_id] - RN_PrEPOralDaily
    lp["prep_effectiveness"][prep_offset, RN_Effectiveness] = draw["efficacy"]
    lp["prep_effectiveness"][prep_offset, RN_Adherence] = draw["adherence"]
    ## TODO: Do we need to set all other coverages to 0?
    ## TODO: Set method mix coverage, not overall coverage? And set others to 0?
    for target in targets:
        lp["prep_cov"][_sex_idx(target.sex), _pop_idx(target.population), year_idx] = draw["target_coverage"]


def _apply_vaccine(lp: LeapfrogParams, targets: list[PopulationTarget], draw: _VaccineDraw) -> None:
    year_idx = _target_year_idx(lp, draw)
    for target in targets:
        if lp["rn_vac_cov_type"] == RN_Single:
            lp["rn_vac_coverage_rg"][RN_AllRisk, year_idx] = draw["target_coverage"]
        else:
            lp["rn_vac_coverage_rg"][_pop_idx(target.population, female=(target.sex == "Female")), year_idx] = draw[
                "target_coverage"
            ]
    lp["rn_vac_params"][RN_Efficacy] = draw["reduction_in_susceptibility"]
    lp["rn_vac_params"][RN_Infectiousness] = draw["reduction_in_infectiousness"]
    lp["rn_vac_params"][RN_Progression] = draw["increase_in_progression_time_to_aids"]
    lp["rn_vac_params"][RN_Duration] = draw["vaccine_duration_years"]

    if draw["vaccine_action_type"] == "Take":
        ## TODO: Implement these in model see issue https://trello.com/c/Qqzniap4
        pass
        # lp["rn_vac_params"][RN_Type] = RN_TakeAction - RN_TakeAction  # start count at 0 in lf
    elif draw["vaccine_action_type"] == "Degree":
        pass
        # lp["rn_vac_params"][RN_Type] = RN_DegreeAction - RN_TakeAction
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


def _apply_cure(lp: LeapfrogParams, targets: list[PopulationTarget], draw: _CureDraw) -> None:
    year_idx = _target_year_idx(lp, draw)
    for target in targets:
        if lp["rn_cure_coverage_type"] == RN_Single:
            lp["rn_cure_coverage_rg"][RN_AllRisk, year_idx] = draw["target_coverage"]
        else:
            lp["rn_cure_coverage_rg"][_pop_idx(target.population, female=(target.sex == "Female")), year_idx] = draw[
                "target_coverage"
            ]
    lp["rn_cure_effect"][RN_Efficacy] = draw["efficacy"]
    lp["rn_cure_effect"][RN_Duration] = draw["duration_of_cure"]


def _apply_ahd(lp: LeapfrogParams, draw: _AHDTreatmentDraw) -> None:
    year_idx = _target_year_idx(lp, draw)
    # TODO: fix typo in adh see https://trello.com/c/fEiv46rE
    lp["rn_adh_treat_cov"][year_idx] = draw["target_coverage"]
    lp["rn_adh_treat_reduc_mort"] = draw["reduction_in_mortality"]


def _apply_poc(lp: LeapfrogParams, poc_type: int, draw: _POCTestDraw) -> None:
    """Apply point-of-care test coverage. *poc_type* is ``RN_POC_CD4_Int`` or ``RN_POC_VL_Int``."""
    year_idx = _target_year_idx(lp, draw)
    rn_poc = RN_POC_CD4 if poc_type == RN_POC_CD4_Int else RN_POC_VL
    lp["rn_poc_cov"][rn_poc, year_idx] = draw["target_coverage"]
    lp["rn_poc_effect"][rn_poc] = draw["effect"]


def _dispatch(lp: LeapfrogParams, iv: InterventionOut, draw: dict[str, float | int | str]) -> None:
    match iv.id:
        case prep_id if prep_id in _PREP_IDS:
            _apply_prep(lp, prep_id, cast(list[PopulationTarget], iv.targets), cast(_PrepDraw, draw))
        case "vaccine":
            _apply_vaccine(lp, cast(list[PopulationTarget], iv.targets), cast(_VaccineDraw, draw))
        case "cure":
            _apply_cure(lp, cast(list[PopulationTarget], iv.targets), cast(_CureDraw, draw))
        case "ahd_treatment":
            _apply_ahd(lp, cast(_AHDTreatmentDraw, draw))
        case "point_of_care_viral_load_test":
            _apply_poc(lp, RN_POC_VL_Int, cast(_POCTestDraw, draw))
        case "point_of_care_cd4_test":
            _apply_poc(lp, RN_POC_CD4_Int, cast(_POCTestDraw, draw))
        case "long_acting_treatment":
            raise NotImplementedError("Long-acting treatment application is not yet implemented.")
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
    for intervention_id, sim in simulation.items():
        _dispatch(leapfrog_params, meta[intervention_id], sim.root)


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
    missing = [k for k in output_indicators if k not in goals_output]
    if missing:
        msg = f"Output indicators not found in Goals output: {missing}"
        raise ValueError(msg)
    return {k: goals_output[k] for k in output_indicators}
