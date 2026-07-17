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
    RN_VMM,
    RN_Adherence,
    RN_AHDTreatment,
    RN_AllRisk,
    RN_CureAdultsChildren,
    RN_CureNeonates,
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
    RN_Substitution,
    RN_TakeAction,
    RN_Type,
    RN_Vaccines,
)

from avenir_goals_scenario._runner.indicator_dims import CALCULATED_INDICATORS, RESOURCE_INDICATOR_ROWS
from avenir_goals_scenario._runner.pjnz import uses_art_initiation_rate
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
    "oral_prep_monthly": RN_PrEPOralMonthly,
    "oral_prep_daily": RN_PrEPOralDaily,
    "injectable_prep_1_month": RN_PrEPInject1Mo,
    "injectable_prep_2_month": RN_PrEPInject2Mo,
    "injectable_prep_6_month": RN_PrEPInject6Mo,
    "oral_prep_plus_contraceptive": RN_PrEPOralPlusCon,
    "prep_ring": RN_PrEPRing,
    "implantable_prep": RN_PrEPImplant,
    "bnabs": RN_PrEPbNABs,
    "pep": RN_PrEP_PEP,
    "vaccine": RN_Vaccines,
    "cure_adults_and_children": RN_CureAdultsChildren,
    "cure_neonates": RN_CureNeonates,
    "vaginal_microbiome_modification": RN_VMM,
    "ahd_treatment": RN_AHDTreatment,
    "poc_cd4_test": RN_POC_CD4_Int,
    "poc_vl_test": RN_POC_VL_Int,
}


# Derived from PrepProduct so the two stay in sync automatically.
_PREP_IDS = frozenset(_product_to_id(p) for p in get_args(PrepProduct))


# VMM coverage-type flags (leapfrog enum, not exported from SpectrumCommon). Note the
# naming is inverted relative to cure/vaccine's RN_Single/RN_Diff: ALLRISK uses the
# single "Percent of women treated" value, SINGLE splits across women's risk groups.
_VMM_COV_ALLRISK = 0
_VMM_COV_SINGLE = 1

# Row index into rn_vmm_coverage_rg for each women's risk group (RG_NONE..RG_HRH).
_VMM_RG_IDX: dict[str, int] = {
    "Not sexually active": 0,
    "Low risk heterosexual": 1,
    "Medium risk heterosexual": 2,
    "High risk heterosexual": 3,
}


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
    substitution: float | None
    duration: float | None


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


class _CureNeonateDraw(TypedDict):
    target_year: int
    target_coverages: list[TargetCoverage]
    effectiveness: float


class _VMMDraw(TypedDict):
    target_year: int
    target_coverages: list[TargetCoverage]
    effectiveness: float


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


class _LongActingTreatmentDraw(TypedDict):
    target_year: int
    target_coverage: float
    interruption_rate_reduction: float
    viral_load_suppression_ratio: float


_Draw: TypeAlias = (
    _PrepDraw
    | _VaccineDraw
    | _CureDraw
    | _CureNeonateDraw
    | _VMMDraw
    | _AHDTreatmentDraw
    | _POCTestDraw
    | _AdultARTDraw
    | _LongActingTreatmentDraw
)


def _target_year_idx(lp: LeapfrogParams, draw: _Draw) -> int:
    """Convert ``draw["target_year"]`` to a zero-based year index into leapfrog arrays."""
    return int(draw["target_year"]) - lp["projection_start_year"]


# Sentinel year index used when a draw has no ``target_year`` — the case where
# every coverage is a per-year array and so no ramp endpoint is needed.
_NO_TARGET_YEAR = -1


def _maybe_target_year_idx(lp: LeapfrogParams, draw: _Draw) -> int:
    """``target_year`` index, or a sentinel when the draw omits ``target_year``.

    ``target_year`` is dropped from a draw only when all of the intervention's
    coverages are per-year arrays, which ignore it; the sentinel is never used to
    build a ramp in that case.
    """
    return _target_year_idx(lp, draw) if "target_year" in draw else _NO_TARGET_YEAR


def _base_year_idx(lp: LeapfrogParams, base_year: int) -> int:
    """Zero-based index of the scale-up start year, clamped to the projection start."""
    return max(0, int(base_year) - lp["projection_start_year"])


def _coverage_ramp(base_value: float, target: float, base_idx: int, target_idx: int, n_years: int) -> np.ndarray:
    """Per-year coverage series covering ``[base_idx, n_years)``.

    Linear from *base_value* at *base_idx* to *target* at *target_idx*, held at
    *target* for all subsequent years. A target year beyond the projection end
    truncates the ramp mid-scale-up.
    """
    ramp = np.linspace(base_value, target, max(target_idx - base_idx, 0) + 1)
    series = np.full(max(n_years - base_idx, 0), target)
    n = min(ramp.size, series.size)
    series[:n] = ramp[:n]
    return series


def _apply_series(series: np.ndarray, base_idx: int, values: list[float]) -> None:
    """Write an explicit per-year coverage trajectory into ``series[base_idx:]`` in place.

    *values* is one value per year from the base year to the projection end year
    (inclusive), so its length must equal ``series.size - base_idx``. The runner
    validates this up front against each PJNZ before any scenario runs; the check
    here is a defensive backstop.
    """
    if base_idx >= series.size:
        return
    expected = series.size - base_idx
    if len(values) != expected:
        msg = (
            f"Per-year coverage array has {len(values)} value(s) but the projection needs "
            f"{expected} (one per year from the base year to the projection end year)."
        )
        raise ValueError(msg)
    series[base_idx:] = np.asarray(values, dtype=series.dtype)


def _prep_series_from_array(values: list[float], base_idx: int, n_years: int) -> np.ndarray:
    """Per-year PrEP coverage series over ``[base_idx, n_years)`` from an explicit array.

    Mirrors the length contract of :func:`_coverage_ramp` so array and ramped
    products compose in the same per-``(sex, rg)`` sum.
    """
    expected = max(n_years - base_idx, 0)
    if len(values) != expected:
        msg = (
            f"Per-year coverage array has {len(values)} value(s) but the projection needs "
            f"{expected} (one per year from the base year to the projection end year)."
        )
        raise ValueError(msg)
    return np.asarray(values, dtype=float)


def _ramp_to_target(
    series: np.ndarray,
    base_idx: int,
    target_idx: int,
    target: float | list[float],
    base_value: float | None = None,
) -> None:
    """Write a coverage scale-up into the per-year array *series* in place.

    If *target* is a per-year array it is written verbatim into ``series[base_idx:]``
    and *target_idx* is ignored. Otherwise coverage runs linearly from the
    base-year value (the existing value at *base_idx*, unless *base_value*
    overrides it) to *target* at *target_idx*, then stays at *target* to the end of
    the projection. Interpolates downwards when the base-year value exceeds the
    target. Years before *base_idx* are left untouched.
    """
    if base_idx >= series.size:
        return
    if isinstance(target, list):
        _apply_series(series, base_idx, target)
        return
    if base_value is None:
        base_value = float(series[base_idx])
    series[base_idx:] = _coverage_ramp(base_value, target, base_idx, target_idx, series.size)


# ---------------------------------------------------------------------------
# Per-intervention application functions
# ---------------------------------------------------------------------------


def _apply_prep_effectiveness(lp: LeapfrogParams, method_offset: int, draw: dict) -> None:
    """Write a PrEP product's effectiveness parameters into ``prep_effectiveness``."""
    lp["prep_effectiveness"][method_offset, RN_Effectiveness] = draw["efficacy"]
    lp["prep_effectiveness"][method_offset, RN_Adherence] = draw["adherence"]
    # Product-specific parameters; validation guarantees these are only set for the
    # correct product (substitution: oral+contraceptive, duration: implant).
    if draw.get("substitution") is not None:
        lp["prep_effectiveness"][method_offset, RN_Substitution] = draw["substitution"]
    if draw.get("duration") is not None:
        lp["prep_effectiveness"][method_offset, RN_Duration] = draw["duration"]


def _apply_all_prep(
    lp: LeapfrogParams,
    prep_draws: list[tuple[str, dict]],
    base_year: int,
) -> None:
    """Apply all PrEP products together, computing prep_cov and prep_method_mix.

    Each product's coverage scales up linearly from its base-year share of
    prep_cov to its target coverage at its target year, then holds at the
    target. Coverage for each (sex, risk_group, year) is the sum across all
    products targeting that population. prep_method_mix holds each product's
    share of that total.
    """
    base_idx = _base_year_idx(lp, base_year)
    n_years = lp["prep_cov"].shape[2]

    # (sex_idx, rg_idx, method_offset) → target coverage (a scalar to ramp toward,
    # or an explicit per-year array). Keys are unique across products (method_offset
    # is per-product; a product cannot have duplicate risk_group/sex targets), so
    # each is written once rather than summed.
    targets: dict[tuple[int, int, int], float | list[float]] = {}
    # Only set for products with at least one distribution coverage; array-only
    # products carry no target_year.
    target_idx_by_method: dict[int, int] = {}

    for iv_id, draw in prep_draws:
        method_offset = _interv_map[iv_id] - RN_PrEPOralDaily
        if "target_year" in draw:
            target_idx_by_method[method_offset] = int(draw["target_year"]) - lp["projection_start_year"]
        _apply_prep_effectiveness(lp, method_offset, draw)
        for tc in draw["target_coverages"]:
            key = (
                _sex_idx(cast(SexName, tc.sex)),
                _risk_group_idx(cast(RiskGroupNames, tc.risk_group)),
                method_offset,
            )
            targets[key] = tc.coverage

    # Per-method scale-up series over [base_idx, n_years). For a distribution the
    # base-year value of each method is its share of total base-year coverage per
    # the method mix; a per-year array is used verbatim.
    series_by_method: dict[tuple[int, int, int], np.ndarray] = {}
    for (sex_idx, rg_idx, method_offset), target_cov in targets.items():
        if isinstance(target_cov, list):
            series_by_method[(sex_idx, rg_idx, method_offset)] = _prep_series_from_array(target_cov, base_idx, n_years)
            continue
        base_value = float(
            lp["prep_cov"][sex_idx, rg_idx, base_idx] * lp["prep_method_mix"][sex_idx, rg_idx, method_offset, base_idx]
        )
        series_by_method[(sex_idx, rg_idx, method_offset)] = _coverage_ramp(
            base_value, target_cov, base_idx, target_idx_by_method[method_offset], n_years
        )

    # Sum per (sex, rg) per year
    totals: dict[tuple[int, int], np.ndarray] = {}
    for (sex_idx, rg_idx, _), series in series_by_method.items():
        k = (sex_idx, rg_idx)
        totals[k] = series.copy() if k not in totals else totals[k] + series

    for (sex_idx, rg_idx), total in totals.items():
        lp["prep_cov"][sex_idx, rg_idx, base_idx:] = np.minimum(total, 1.0)
        lp["prep_method_mix"][sex_idx, rg_idx, :, base_idx:] = 0.0

    for (sex_idx, rg_idx, method_offset), series in series_by_method.items():
        total = totals[(sex_idx, rg_idx)]
        lp["prep_method_mix"][sex_idx, rg_idx, method_offset, base_idx:] = np.divide(
            series, total, out=np.zeros_like(series), where=total > 0
        )


def _apply_vaccine(lp: LeapfrogParams, draw: _VaccineDraw, base_year: int) -> None:
    base_idx = _base_year_idx(lp, base_year)
    target_idx = _maybe_target_year_idx(lp, draw)
    for tc in draw["target_coverages"]:
        if tc.risk_group == "PLHIV":
            lp["rn_vac_cov_type"] = RN_Single
            _ramp_to_target(lp["rn_vac_coverage_rg"][RN_AllRisk], base_idx, target_idx, tc.coverage)
        elif tc.sex == "Both" or tc.sex is None:
            lp["rn_vac_cov_type"] = RN_Diff
            for female in (False, True):
                _ramp_to_target(
                    lp["rn_vac_coverage_rg"][_risk_group_idx(cast(RiskGroupNames, tc.risk_group), female=female)],
                    base_idx,
                    target_idx,
                    tc.coverage,
                )
        else:
            lp["rn_vac_cov_type"] = RN_Diff
            _ramp_to_target(
                lp["rn_vac_coverage_rg"][
                    _risk_group_idx(cast(RiskGroupNames, tc.risk_group), female=(tc.sex == "Female"))
                ],
                base_idx,
                target_idx,
                tc.coverage,
            )
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


def _apply_cure(lp: LeapfrogParams, draw: _CureDraw, base_year: int) -> None:
    base_idx = _base_year_idx(lp, base_year)
    target_idx = _maybe_target_year_idx(lp, draw)
    for tc in draw["target_coverages"]:
        if tc.risk_group == "PLHIV":
            lp["rn_cure_coverage_type"] = RN_Single
            _ramp_to_target(lp["rn_cure_coverage_rg"][RN_AllRisk], base_idx, target_idx, tc.coverage)
        elif tc.sex == "Both" or tc.sex is None:
            lp["rn_cure_coverage_type"] = RN_Diff
            for female in (False, True):
                _ramp_to_target(
                    lp["rn_cure_coverage_rg"][_risk_group_idx(cast(RiskGroupNames, tc.risk_group), female=female)],
                    base_idx,
                    target_idx,
                    tc.coverage,
                )
        else:
            lp["rn_cure_coverage_type"] = RN_Diff
            _ramp_to_target(
                lp["rn_cure_coverage_rg"][
                    _risk_group_idx(cast(RiskGroupNames, tc.risk_group), female=(tc.sex == "Female"))
                ],
                base_idx,
                target_idx,
                tc.coverage,
            )
    lp["rn_cure_effect"][RN_Efficacy] = draw["efficacy"]
    lp["rn_cure_effect"][RN_Duration] = draw["duration_of_cure"]


def _apply_cure_neonates(lp: LeapfrogParams, draw: _CureNeonateDraw, base_year: int) -> None:
    base_idx = _base_year_idx(lp, base_year)
    target_idx = _maybe_target_year_idx(lp, draw)
    # Neonates are the only population; coverage is a single value by year.
    for tc in draw["target_coverages"]:
        _ramp_to_target(lp["rn_cure_coverage_neonates"], base_idx, target_idx, tc.coverage)
    lp["rn_cure_effect_neonates"] = draw["effectiveness"]


def _apply_vmm(lp: LeapfrogParams, draw: _VMMDraw, base_year: int) -> None:
    base_idx = _base_year_idx(lp, base_year)
    target_idx = _maybe_target_year_idx(lp, draw)
    for tc in draw["target_coverages"]:
        if tc.risk_group == "Percent of women treated":
            lp["rn_vmm_coverage_type"] = _VMM_COV_ALLRISK
            _ramp_to_target(lp["rn_vmm_coverage_all"], base_idx, target_idx, tc.coverage)
        else:
            lp["rn_vmm_coverage_type"] = _VMM_COV_SINGLE
            _ramp_to_target(
                lp["rn_vmm_coverage_rg"][_VMM_RG_IDX[cast(str, tc.risk_group)]], base_idx, target_idx, tc.coverage
            )
    lp["rn_vmm_effect"] = draw["effectiveness"]


def _apply_ahd(lp: LeapfrogParams, draw: _AHDTreatmentDraw, base_year: int) -> None:
    base_idx = _base_year_idx(lp, base_year)
    target_idx = _maybe_target_year_idx(lp, draw)
    _ramp_to_target(lp["rn_ahd_treat_cov"], base_idx, target_idx, draw["target_coverage"])
    lp["rn_ahd_treat_reduc_mort"] = draw["reduction_in_mortality"]


def _apply_adult_art(lp: LeapfrogParams, draw: _AdultARTDraw, base_year: int) -> None:
    # Adult ART is applied as an annual initiation rate, which only has an effect
    # when the PJNZ was read in initiation-rate mode. For other modes there is no
    # rate to ramp, so skip it (the run continues; the runner warns once at import).
    if not uses_art_initiation_rate(lp):
        return
    base_idx = _base_year_idx(lp, base_year)
    target_idx = _maybe_target_year_idx(lp, draw)
    for tc in draw["target_coverages"]:
        if tc.sex == "Both":
            sex_indices = [0, 1]
        elif tc.sex == "Male":
            sex_indices = [0]
        else:
            sex_indices = [1]
        for sex_idx in sex_indices:
            # art_initiation_rate is (sex, year); ramp each sex from its base-year
            # rate up (or down) to the target rate, held at the target thereafter.
            _ramp_to_target(lp["art_initiation_rate"][sex_idx], base_idx, target_idx, tc.coverage)


def _apply_long_acting_treatment(lp: LeapfrogParams, draw: _LongActingTreatmentDraw, base_year: int) -> None:
    base_idx = _base_year_idx(lp, base_year)
    target_idx = _maybe_target_year_idx(lp, draw)

    _ramp_to_target(lp["long_act_treat_cov"], base_idx, target_idx, draw["target_coverage"])
    lp["long_act_treat_eff_vls"] = draw["viral_load_suppression_ratio"]
    lp["long_act_treat_eff_ltfu"] = draw["interruption_rate_reduction"]


def _apply_poc(lp: LeapfrogParams, poc_type: int, draw: _POCTestDraw, base_year: int) -> None:
    """Apply point-of-care test coverage. *poc_type* is ``RN_POC_CD4_Int`` or ``RN_POC_VL_Int``."""
    base_idx = _base_year_idx(lp, base_year)
    target_idx = _maybe_target_year_idx(lp, draw)
    rn_poc = RN_POC_CD4 if poc_type == RN_POC_CD4_Int else RN_POC_VL
    _ramp_to_target(lp["rn_poc_cov"][rn_poc], base_idx, target_idx, draw["target_coverage"])
    lp["rn_poc_effect"][rn_poc] = draw["effect"]


def _dispatch(lp: LeapfrogParams, iv: InterventionOut, draw: dict, base_year: int) -> None:
    match iv.id:
        case "vaccine":
            _apply_vaccine(lp, cast(_VaccineDraw, draw), base_year)
        case "cure_adults_and_children":
            _apply_cure(lp, cast(_CureDraw, draw), base_year)
        case "cure_neonates":
            _apply_cure_neonates(lp, cast(_CureNeonateDraw, draw), base_year)
        case "vaginal_microbiome_modification":
            _apply_vmm(lp, cast(_VMMDraw, draw), base_year)
        case "ahd_treatment":
            _apply_ahd(lp, cast(_AHDTreatmentDraw, draw), base_year)
        case "poc_vl_test":
            _apply_poc(lp, RN_POC_VL_Int, cast(_POCTestDraw, draw), base_year)
        case "poc_cd4_test":
            _apply_poc(lp, RN_POC_CD4_Int, cast(_POCTestDraw, draw), base_year)
        case "long_acting_treatment":
            _apply_long_acting_treatment(lp, cast(_LongActingTreatmentDraw, draw), base_year)
        case "adult_art":
            _apply_adult_art(lp, cast(_AdultARTDraw, draw), base_year)
        case _:
            msg = f"Unknown intervention: {iv.id!r}"
            raise ValueError(msg)


def apply_simulation(
    leapfrog_params: LeapfrogParams,
    interventions: list[InterventionOut],
    simulation: dict[str, InterventionSimulation],
    base_year: int,
) -> None:
    """Apply one sampled draw of intervention parameters to *leapfrog_params* in-place.

    Each intervention's coverage scales up linearly from its existing value in
    *base_year* to the sampled target coverage in its target year, and is held
    at the target for all subsequent years.

    Args:
        leapfrog_params: Goals model parameter dict from ``import_pjnz``. Modified in-place.
        interventions: Intervention metadata for the current scenario.
        simulation: Mapping of intervention ID → sampled parameter values for one draw.
        base_year: First year of the coverage scale-up (``base_year`` in the run config).
    """
    meta = {iv.id: iv for iv in interventions}
    prep_draws: list[tuple[str, dict]] = []
    for intervention_id, sim in simulation.items():
        iv = meta[intervention_id]
        if intervention_id in _PREP_IDS:
            prep_draws.append((intervention_id, sim.root))
        else:
            _dispatch(leapfrog_params, iv, sim.root, base_year)
    if prep_draws:
        _apply_all_prep(leapfrog_params, prep_draws, base_year)


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
    Intervention coverage scales up linearly from ``output_years.start`` (the
    run's base year) to each intervention's target year, then holds at the target.

    Args:
        leapfrog_params: Goals model parameter dict for one PJNZ. Modified in-place.
        interventions: Intervention metadata for the current scenario.
        simulation: Sampled parameter values for one draw.
        output_indicators: Indicator names to extract from Goals output.
        output_years: Year range passed to ``run_goals``; its start is also the
            base year the coverage scale-up starts from.

    Returns:
        Mapping of indicator name → NumPy array (last axis indexed by year).

    Raises:
        ValueError: If any indicator in *output_indicators* is absent from Goals output.
    """
    apply_simulation(leapfrog_params, interventions, simulation, base_year=output_years.start)
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
        elif k in RESOURCE_INDICATOR_ROWS:
            # Keep only the populated rows; full array is (nIntervnRN + 4, year).
            return goals_output[k][RESOURCE_INDICATOR_ROWS[k], :]
        else:
            return goals_output[k]

    return {k: get_indicator(k) for k in output_indicators}
