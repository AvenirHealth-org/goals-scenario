"""Unit tests for apply_simulation and its per-intervention dispatch."""

import numpy as np
import pytest
from SpectrumCommon.Const.RN import (
    RN_HRH,
    RN_HRH_F,
    RN_MSM,
    RN_POC_CD4,
    RN_POC_VL,
    RN_Adherence,
    RN_AllRisk,
    RN_Diff,
    RN_Duration,
    RN_Effectiveness,
    RN_Efficacy,
    RN_Infectiousness,
    RN_Progression,
    RN_Single,
    RN_Type,
)

from avenir_goals_scenario._runner.simulation import apply_simulation
from avenir_goals_scenario.models import InterventionOut, InterventionSimulation, TargetCoverage

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_START_YEAR = 2020
_TARGET_YEAR = 2025
_TARGET_YEAR_IDX = _TARGET_YEAR - _START_YEAR  # 5

# prep_effectiveness shape: (n_prep_products=10, n_effectiveness=4)
# see SpectrumEngine n_effectiveness constants are
# 0 - effectiveness, 1 - adherence, 2 - substitution, 3 - duration
_N_PREP = 10
_N_EFFECTIVENESS = 2

# prep_cov shape: (n_sexes=2, max_pop_idx+1=7, n_years)
_N_SEXES = 2
_N_POPS = 7
_N_YEARS = 20

# rn_vac/cure_coverage: pop indices go up to female MSM (17), give 18 rows
_N_VAC_POPS = 18

# ---------------------------------------------------------------------------
# Leapfrog param builders — each returns only the keys the intervention touches
# ---------------------------------------------------------------------------


def _prep_params() -> dict:
    return {
        "projection_start_year": _START_YEAR,
        "prep_effectiveness": np.zeros((_N_PREP, _N_EFFECTIVENESS)),
        "prep_cov": np.zeros((_N_SEXES, _N_POPS, _N_YEARS)),
        "prep_method_mix": np.zeros((_N_SEXES, _N_POPS, _N_PREP, _N_YEARS)),
    }


def _vaccine_params() -> dict:
    return {
        "projection_start_year": _START_YEAR,
        "rn_vac_cov_type": 0,
        "rn_vac_coverage_rg": np.zeros((_N_VAC_POPS, _N_YEARS)),
        "rn_vac_params": np.zeros(5),  # Efficacy=0, Infectiousness=1, Progression=2, Duration=3, Type=4
        "rn_vac_targetting": 0,
    }


def _cure_params() -> dict:
    return {
        "projection_start_year": _START_YEAR,
        "rn_cure_coverage_type": 0,
        "rn_cure_coverage_rg": np.zeros((_N_VAC_POPS, _N_YEARS)),
        "rn_cure_effect": np.zeros(4),  # Efficacy=0, Duration=3
    }


def _ahd_params() -> dict:
    return {
        "projection_start_year": _START_YEAR,
        "rn_adh_treat_cov": np.zeros(_N_YEARS),
        "rn_adh_treat_reduc_mort": 0.0,
    }


def _poc_params() -> dict:
    return {
        "projection_start_year": _START_YEAR,
        "rn_poc_cov": np.zeros((2, _N_YEARS)),  # [CD4=0, VL=1]
        "rn_poc_effect": np.zeros(2),
    }


# ---------------------------------------------------------------------------
# apply_simulation helpers
# ---------------------------------------------------------------------------


def _sim(intervention_id: str, **params) -> dict[str, InterventionSimulation]:
    """Build a single-intervention simulation dict."""
    return {intervention_id: InterventionSimulation({"target_year": _TARGET_YEAR, **params})}


def _iv(intervention_id: str, product: str) -> list[InterventionOut]:
    return [InterventionOut(id=intervention_id, product=product)]


# ---------------------------------------------------------------------------
# PrEP — all 9 products
# ---------------------------------------------------------------------------

_PREP_CASES = [
    ("daily_prep", "Daily PrEP", 0),
    ("one_month_pill_for_prep", "One month pill for PrEP", 1),
    ("oral_prep_plus_contraceptive", "Oral PrEP plus contraceptive", 2),
    ("one_month_injectable_prep", "One month injectable PrEP", 3),
    ("two_month_injectable_prep", "Two month injectable PrEP", 4),
    ("six_month_injectable_prep", "Six month injectable PrEP", 5),
    ("ring_prep", "Ring PrEP", 6),
    ("bnabs", "bNABs", 7),
    ("implantable_prep", "Implantable PrEP", 8),
    ("pep", "PEP", 9),
]


@pytest.mark.parametrize("pid,product,offset", _PREP_CASES)
def test_prep_sets_effectiveness_and_coverage(pid, product, offset):
    lp = _prep_params()
    ivs = _iv(pid, product)
    sim = _sim(
        pid,
        efficacy=0.95,
        adherence=0.85,
        target_coverages=[{"sex": "Female", "risk_group": "High risk heterosexual", "coverage": 0.30}],
    )

    apply_simulation(lp, ivs, sim)

    eff = lp["prep_effectiveness"]
    assert eff[offset, RN_Effectiveness] == pytest.approx(0.95)
    assert eff[offset, RN_Adherence] == pytest.approx(0.85)
    assert lp["prep_cov"][1, RN_HRH, _TARGET_YEAR_IDX] == pytest.approx(0.30)
    # Single product → 100% method mix weight
    assert lp["prep_method_mix"][1, RN_HRH, offset, _TARGET_YEAR_IDX] == pytest.approx(1.0)


def test_prep_multiple_targets_writes_each_population():
    lp = _prep_params()
    ivs = _iv("daily_prep", "Daily PrEP")
    sim = _sim(
        "daily_prep",
        efficacy=0.9,
        adherence=0.8,
        target_coverages=[
            {"sex": "Female", "risk_group": "High risk heterosexual", "coverage": 0.20},
            {"sex": "Male", "risk_group": "Men who have sex with men", "coverage": 0.15},
        ],
    )

    apply_simulation(lp, ivs, sim)

    assert lp["prep_cov"][1, RN_HRH, _TARGET_YEAR_IDX] == pytest.approx(0.20)
    assert lp["prep_cov"][0, RN_MSM, _TARGET_YEAR_IDX] == pytest.approx(0.15)
    assert lp["prep_method_mix"][1, RN_HRH, 0, _TARGET_YEAR_IDX] == pytest.approx(1.0)
    assert lp["prep_method_mix"][0, RN_MSM, 0, _TARGET_YEAR_IDX] == pytest.approx(1.0)


def test_prep_does_not_write_other_products():
    lp = _prep_params()
    ivs = _iv("daily_prep", "Daily PrEP")
    sim = _sim(
        "daily_prep",
        efficacy=0.9,
        adherence=0.8,
        target_coverages=[{"sex": "Female", "risk_group": "High risk heterosexual", "coverage": 0.20}],
    )

    apply_simulation(lp, ivs, sim)

    daily_offset = 0  # RN_PrEPOralDaily - RN_PrEPOralDaily
    for i in range(_N_PREP):
        if i != daily_offset:
            assert lp["prep_effectiveness"][i, RN_Effectiveness] == 0.0
            assert lp["prep_effectiveness"][i, RN_Adherence] == 0.0


def test_prep_multi_product_aggregates_cov_and_sets_method_mix():
    """Two products targeting the same (sex, risk_group): cov sums, method mix weights by share."""
    lp = _prep_params()
    ivs = [
        InterventionOut(id="daily_prep", product="Daily PrEP"),
        InterventionOut(id="two_month_injectable_prep", product="Two month injectable PrEP"),
    ]
    sim = {
        "daily_prep": InterventionSimulation({
            "target_year": _TARGET_YEAR,
            "efficacy": 0.9,
            "adherence": 0.8,
            "target_coverages": [TargetCoverage(sex="Female", risk_group="High risk heterosexual", coverage=0.30)],
        }),
        "two_month_injectable_prep": InterventionSimulation({
            "target_year": _TARGET_YEAR,
            "efficacy": 0.85,
            "adherence": 0.75,
            "target_coverages": [TargetCoverage(sex="Female", risk_group="High risk heterosexual", coverage=0.20)],
        }),
    }

    apply_simulation(lp, ivs, sim)

    assert lp["prep_cov"][1, RN_HRH, _TARGET_YEAR_IDX] == pytest.approx(0.50)
    # daily (offset 0): 0.30 / 0.50 = 0.6
    assert lp["prep_method_mix"][1, RN_HRH, 0, _TARGET_YEAR_IDX] == pytest.approx(0.6)
    # two-month injectable (offset 4): 0.20 / 0.50 = 0.4
    assert lp["prep_method_mix"][1, RN_HRH, 4, _TARGET_YEAR_IDX] == pytest.approx(0.4)
    # all other method slots zeroed
    for m in range(_N_PREP):
        if m not in (0, 4):
            assert lp["prep_method_mix"][1, RN_HRH, m, _TARGET_YEAR_IDX] == 0.0


def test_prep_coverage_over_1_clamps_to_1():
    """Total coverage > 1.0 is clamped: prep_cov = 1.0, method mix still normalised by actual sum."""
    lp = _prep_params()
    ivs = [
        InterventionOut(id="daily_prep", product="Daily PrEP"),
        InterventionOut(id="two_month_injectable_prep", product="Two month injectable PrEP"),
    ]
    # 0.70 + 0.50 = 1.20 → clamped to 1.0; mix = 0.70/1.20, 0.50/1.20
    sim = {
        "daily_prep": InterventionSimulation({
            "target_year": _TARGET_YEAR,
            "efficacy": 0.9,
            "adherence": 0.8,
            "target_coverages": [TargetCoverage(sex="Female", risk_group="High risk heterosexual", coverage=0.70)],
        }),
        "two_month_injectable_prep": InterventionSimulation({
            "target_year": _TARGET_YEAR,
            "efficacy": 0.85,
            "adherence": 0.75,
            "target_coverages": [TargetCoverage(sex="Female", risk_group="High risk heterosexual", coverage=0.50)],
        }),
    }

    apply_simulation(lp, ivs, sim)

    assert lp["prep_cov"][1, RN_HRH, _TARGET_YEAR_IDX] == pytest.approx(1.0)
    assert lp["prep_method_mix"][1, RN_HRH, 0, _TARGET_YEAR_IDX] == pytest.approx(0.70 / 1.20)
    assert lp["prep_method_mix"][1, RN_HRH, 4, _TARGET_YEAR_IDX] == pytest.approx(0.50 / 1.20)


def test_prep_zero_coverage_does_not_raise():
    """Zero sampled coverage (e.g. clamped draw) must not cause ZeroDivisionError."""
    lp = _prep_params()
    ivs = [InterventionOut(id="daily_prep", product="Daily PrEP")]
    sim = {
        "daily_prep": InterventionSimulation({
            "target_year": _TARGET_YEAR,
            "efficacy": 0.9,
            "adherence": 0.8,
            "target_coverages": [TargetCoverage(sex="Female", risk_group="High risk heterosexual", coverage=0.0)],
        }),
    }
    apply_simulation(lp, ivs, sim)
    assert lp["prep_cov"][1, RN_HRH, _TARGET_YEAR_IDX] == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# Vaccine — not yet fully implemented; partial coverage write is expected
# ---------------------------------------------------------------------------


_VAC_SIM_BASE = {
    "reduction_in_susceptibility": 0.6,
    "reduction_in_infectiousness": 0.4,
    "increase_in_progression_time_to_aids": 0.2,
    "vaccine_duration_years": 10.0,
    "vaccine_action_type": "Take",
    "targeting": "Vaccinate without HIV testing",
}


def test_vaccine_plhiv_target_writes_all_risk():
    lp = _vaccine_params()
    ivs = _iv("vaccine", "Vaccine")
    sim = _sim("vaccine", target_coverages=[{"sex": "Both", "risk_group": "PLHIV", "coverage": 0.50}], **_VAC_SIM_BASE)

    apply_simulation(lp, ivs, sim)

    assert lp["rn_vac_cov_type"] == RN_Single
    assert lp["rn_vac_coverage_rg"][RN_AllRisk, _TARGET_YEAR_IDX] == pytest.approx(0.50)
    assert lp["rn_vac_params"][RN_Efficacy] == pytest.approx(0.6)
    assert lp["rn_vac_params"][RN_Infectiousness] == pytest.approx(0.4)
    assert lp["rn_vac_params"][RN_Progression] == pytest.approx(0.2)
    assert lp["rn_vac_params"][RN_Duration] == pytest.approx(10.0)
    assert lp["rn_vac_targetting"] == 0


def test_vaccine_plhiv_target_sex_none_writes_all_risk():
    lp = _vaccine_params()
    ivs = _iv("vaccine", "Vaccine")
    sim = _sim("vaccine", target_coverages=[{"sex": None, "risk_group": "PLHIV", "coverage": 0.45}], **_VAC_SIM_BASE)

    apply_simulation(lp, ivs, sim)

    assert lp["rn_vac_cov_type"] == RN_Single
    assert lp["rn_vac_coverage_rg"][RN_AllRisk, _TARGET_YEAR_IDX] == pytest.approx(0.45)


def test_vaccine_risk_group_female_writes_female_index():
    lp = _vaccine_params()
    ivs = _iv("vaccine", "Vaccine")
    sim = _sim(
        "vaccine",
        target_coverages=[{"sex": "Female", "risk_group": "High risk heterosexual", "coverage": 0.40}],
        **{**_VAC_SIM_BASE, "vaccine_action_type": "Degree", "targeting": "Vaccinate only HIV-negative individuals"},
    )

    apply_simulation(lp, ivs, sim)

    assert lp["rn_vac_cov_type"] == RN_Diff
    assert lp["rn_vac_coverage_rg"][RN_HRH_F, _TARGET_YEAR_IDX] == pytest.approx(0.40)
    assert lp["rn_vac_targetting"] == 1


def test_vaccine_risk_group_both_writes_male_and_female():
    lp = _vaccine_params()
    ivs = _iv("vaccine", "Vaccine")
    sim = _sim(
        "vaccine",
        target_coverages=[{"sex": "Both", "risk_group": "High risk heterosexual", "coverage": 0.35}],
        **_VAC_SIM_BASE,
    )

    apply_simulation(lp, ivs, sim)

    assert lp["rn_vac_cov_type"] == RN_Diff
    assert lp["rn_vac_coverage_rg"][RN_HRH, _TARGET_YEAR_IDX] == pytest.approx(0.35)
    assert lp["rn_vac_coverage_rg"][RN_HRH_F, _TARGET_YEAR_IDX] == pytest.approx(0.35)


def test_vaccine_action_type_is_mapped():
    lp = _vaccine_params()
    ivs = _iv("vaccine", "Vaccine")
    sim = _sim(
        "vaccine",
        target_coverages=[{"sex": None, "risk_group": "PLHIV", "coverage": 0.50}],
        **{**_VAC_SIM_BASE, "vaccine_action_type": "Take"},
    )

    apply_simulation(lp, ivs, sim)

    assert lp["rn_vac_params"][RN_Type] == 0

    sim = _sim(
        "vaccine",
        target_coverages=[{"sex": None, "risk_group": "PLHIV", "coverage": 0.50}],
        **{**_VAC_SIM_BASE, "vaccine_action_type": "Degree"},
    )

    apply_simulation(lp, ivs, sim)

    assert lp["rn_vac_params"][RN_Type] == 1


def test_vaccine_invalid_action_type_raises():
    lp = _vaccine_params()
    ivs = _iv("vaccine", "Vaccine")
    sim = _sim(
        "vaccine",
        target_coverages=[{"sex": None, "risk_group": "PLHIV", "coverage": 0.50}],
        **{**_VAC_SIM_BASE, "vaccine_action_type": "Invalid"},
    )

    with pytest.raises(ValueError, match="vaccine_action_type"):
        apply_simulation(lp, ivs, sim)


def test_vaccine_invalid_targeting_raises():
    lp = _vaccine_params()
    ivs = _iv("vaccine", "Vaccine")
    sim = _sim(
        "vaccine",
        target_coverages=[{"sex": None, "risk_group": "PLHIV", "coverage": 0.50}],
        **{**_VAC_SIM_BASE, "targeting": "Invalid"},
    )

    with pytest.raises(ValueError, match="targeting"):
        apply_simulation(lp, ivs, sim)


# ---------------------------------------------------------------------------
# Cure
# ---------------------------------------------------------------------------


def test_cure_plhiv_target_writes_all_risk():
    lp = _cure_params()
    ivs = _iv("cure", "Cure")
    sim = _sim(
        "cure",
        target_coverages=[{"sex": "Both", "risk_group": "PLHIV", "coverage": 0.30}],
        efficacy=0.80,
        duration_of_cure=5.0,
    )

    apply_simulation(lp, ivs, sim)

    assert lp["rn_cure_coverage_type"] == RN_Single
    assert lp["rn_cure_coverage_rg"][RN_AllRisk, _TARGET_YEAR_IDX] == pytest.approx(0.30)
    assert lp["rn_cure_effect"][RN_Efficacy] == pytest.approx(0.80)
    assert lp["rn_cure_effect"][RN_Duration] == pytest.approx(5.0)


def test_cure_risk_group_female_writes_female_index():
    lp = _cure_params()
    ivs = _iv("cure", "Cure")
    sim = _sim(
        "cure",
        target_coverages=[{"sex": "Female", "risk_group": "High risk heterosexual", "coverage": 0.25}],
        efficacy=0.75,
        duration_of_cure=3.0,
    )

    apply_simulation(lp, ivs, sim)

    assert lp["rn_cure_coverage_type"] == RN_Diff
    assert lp["rn_cure_coverage_rg"][RN_HRH_F, _TARGET_YEAR_IDX] == pytest.approx(0.25)
    assert lp["rn_cure_effect"][RN_Efficacy] == pytest.approx(0.75)
    assert lp["rn_cure_effect"][RN_Duration] == pytest.approx(3.0)


def test_cure_risk_group_both_writes_male_and_female():
    lp = _cure_params()
    ivs = _iv("cure", "Cure")
    sim = _sim(
        "cure",
        target_coverages=[{"sex": "Both", "risk_group": "High risk heterosexual", "coverage": 0.20}],
        efficacy=0.70,
        duration_of_cure=4.0,
    )

    apply_simulation(lp, ivs, sim)

    assert lp["rn_cure_coverage_type"] == RN_Diff
    assert lp["rn_cure_coverage_rg"][RN_HRH, _TARGET_YEAR_IDX] == pytest.approx(0.20)
    assert lp["rn_cure_coverage_rg"][RN_HRH_F, _TARGET_YEAR_IDX] == pytest.approx(0.20)


# ---------------------------------------------------------------------------
# AHD treatment — not yet fully implemented
# ---------------------------------------------------------------------------


def test_ahd_treatment_writes_coverage_and_mortality_reduction():
    lp = _ahd_params()
    ivs = _iv("ahd_treatment", "AHD treatment")
    sim = _sim("ahd_treatment", target_coverage=0.80, reduction_in_mortality=0.60)

    apply_simulation(lp, ivs, sim)

    assert lp["rn_adh_treat_cov"][_TARGET_YEAR_IDX] == pytest.approx(0.80)
    assert lp["rn_adh_treat_reduc_mort"] == pytest.approx(0.60)


# ---------------------------------------------------------------------------
# POC tests — not yet fully implemented
# ---------------------------------------------------------------------------


def test_poc_viral_load_writes_coverage_and_effect():
    lp = _poc_params()
    ivs = _iv("point_of_care_viral_load_test", "Point of care viral load test")
    sim = _sim("point_of_care_viral_load_test", target_coverage=0.70, effect=0.12)

    apply_simulation(lp, ivs, sim)

    assert lp["rn_poc_cov"][RN_POC_VL, _TARGET_YEAR_IDX] == pytest.approx(0.70)
    assert lp["rn_poc_effect"][RN_POC_VL] == pytest.approx(0.12)


def test_poc_cd4_writes_coverage_and_effect():
    lp = _poc_params()
    ivs = _iv("point_of_care_cd4_test", "Point of care CD4 test")
    sim = _sim("point_of_care_cd4_test", target_coverage=0.65, effect=0.25)

    apply_simulation(lp, ivs, sim)

    assert lp["rn_poc_cov"][RN_POC_CD4, _TARGET_YEAR_IDX] == pytest.approx(0.65)
    assert lp["rn_poc_effect"][RN_POC_CD4] == pytest.approx(0.25)


# ---------------------------------------------------------------------------
# Adult ART
# ---------------------------------------------------------------------------

_N_SEXES_ART = 2
_N_YEARS_ART = 20


def _adult_art_params() -> dict:
    return {
        "projection_start_year": _START_YEAR,
        "adults_on_art": np.zeros((_N_SEXES_ART, _N_YEARS_ART)),
        "adults_on_art_is_percent": np.zeros((_N_SEXES_ART, _N_YEARS_ART)),
    }


def test_adult_art_male_writes_male_index():
    lp = _adult_art_params()
    ivs = _iv("adult_art", "Adult ART")
    sim = _sim("adult_art", target_coverages=[{"sex": "Male", "risk_group": None, "coverage": 0.75}])

    apply_simulation(lp, ivs, sim)

    assert lp["adults_on_art"][0, _TARGET_YEAR_IDX] == pytest.approx(0.75)
    assert lp["adults_on_art"][1, _TARGET_YEAR_IDX] == 0.0
    assert lp["adults_on_art_is_percent"][0, _TARGET_YEAR_IDX] == 1
    assert lp["adults_on_art_is_percent"][1, _TARGET_YEAR_IDX] == 0


def test_adult_art_female_writes_female_index():
    lp = _adult_art_params()
    ivs = _iv("adult_art", "Adult ART")
    sim = _sim("adult_art", target_coverages=[{"sex": "Female", "risk_group": None, "coverage": 0.60}])

    apply_simulation(lp, ivs, sim)

    assert lp["adults_on_art"][0, _TARGET_YEAR_IDX] == 0.0
    assert lp["adults_on_art"][1, _TARGET_YEAR_IDX] == pytest.approx(0.60)
    assert lp["adults_on_art_is_percent"][0, _TARGET_YEAR_IDX] == 0
    assert lp["adults_on_art_is_percent"][1, _TARGET_YEAR_IDX] == 1


def test_adult_art_both_writes_male_and_female():
    lp = _adult_art_params()
    ivs = _iv("adult_art", "Adult ART")
    sim = _sim("adult_art", target_coverages=[{"sex": "Both", "risk_group": None, "coverage": 0.80}])

    apply_simulation(lp, ivs, sim)

    assert lp["adults_on_art"][0, _TARGET_YEAR_IDX] == pytest.approx(0.80)
    assert lp["adults_on_art"][1, _TARGET_YEAR_IDX] == pytest.approx(0.80)
    assert lp["adults_on_art_is_percent"][0, _TARGET_YEAR_IDX] == 1
    assert lp["adults_on_art_is_percent"][1, _TARGET_YEAR_IDX] == 1


def test_adult_art_multiple_targets_can_have_different_coverages():
    lp = _adult_art_params()
    ivs = _iv("adult_art", "Adult ART")
    sim = _sim(
        "adult_art",
        target_coverages=[
            {"sex": "Male", "risk_group": None, "coverage": 0.75},
            {"sex": "Female", "risk_group": None, "coverage": 0.60},
        ],
    )

    apply_simulation(lp, ivs, sim)

    assert lp["adults_on_art"][0, _TARGET_YEAR_IDX] == pytest.approx(0.75)
    assert lp["adults_on_art"][1, _TARGET_YEAR_IDX] == pytest.approx(0.60)
    assert lp["adults_on_art_is_percent"][0, _TARGET_YEAR_IDX] == 1
    assert lp["adults_on_art_is_percent"][1, _TARGET_YEAR_IDX] == 1


# ---------------------------------------------------------------------------
# Long-acting treatment — target_year absent from params (known limitation)
# ---------------------------------------------------------------------------


def test_long_acting_treatment_raises_not_implemented():
    lp = {"projection_start_year": _START_YEAR}
    ivs = [InterventionOut(id="long_acting_treatment", product="Long-acting treatment")]
    sim = {
        "long_acting_treatment": InterventionSimulation({
            "interruption_rate_reduction": 0.25,
            "viral_load_suppression_ratio": 0.80,
        })
    }

    with pytest.raises(NotImplementedError, match="Long-acting treatment"):
        apply_simulation(lp, ivs, sim)


# ---------------------------------------------------------------------------
# Unknown intervention
# ---------------------------------------------------------------------------


def test_unknown_intervention_raises_value_error():
    lp = {"projection_start_year": _START_YEAR}
    ivs = [InterventionOut(id="not_a_real_intervention", product="???")]
    sim = {"not_a_real_intervention": InterventionSimulation({"target_year": _TARGET_YEAR})}

    with pytest.raises(ValueError, match="Unknown intervention"):
        apply_simulation(lp, ivs, sim)
