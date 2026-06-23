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
    RN_Substitution,
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
_N_EFFECTIVENESS = 4

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


def _cure_neonate_params() -> dict:
    return {
        "projection_start_year": _START_YEAR,
        "rn_cure_coverage_neonates": np.zeros(_N_YEARS),
        "rn_cure_effect_neonates": 0.0,
    }


# rn_vmm_coverage_rg has one row per women's risk group (NONE, LRH, MRH, HRH).
_N_VMM_RG = 4


def _vmm_params() -> dict:
    return {
        "projection_start_year": _START_YEAR,
        "rn_vmm_coverage_type": 0,
        "rn_vmm_coverage_all": np.zeros(_N_YEARS),
        "rn_vmm_coverage_rg": np.zeros((_N_VMM_RG, _N_YEARS)),
        "rn_vmm_effect": 0.0,
    }


def _ahd_params() -> dict:
    return {
        "projection_start_year": _START_YEAR,
        "rn_ahd_treat_cov": np.zeros(_N_YEARS),
        "rn_ahd_treat_reduc_mort": 0.0,
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
    ("oral_prep_daily", "Oral PrEP (daily)", 0),
    ("oral_prep_monthly", "Oral PrEP (monthly)", 1),
    ("oral_prep_plus_contraceptive", "Oral PrEP plus contraceptive", 2),
    ("injectable_prep_1_month", "Injectable PrEP (1 month)", 3),
    ("injectable_prep_2_month", "Injectable PrEP (2 month)", 4),
    ("injectable_prep_6_month", "Injectable PrEP (6 month)", 5),
    ("prep_ring", "PrEP ring", 6),
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
    ivs = _iv("oral_prep_daily", "Oral PrEP (daily)")
    sim = _sim(
        "oral_prep_daily",
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
    ivs = _iv("oral_prep_daily", "Oral PrEP (daily)")
    sim = _sim(
        "oral_prep_daily",
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


def test_prep_substitution_maps_for_oral_contraceptive():
    lp = _prep_params()
    ivs = _iv("oral_prep_plus_contraceptive", "Oral PrEP plus contraceptive")
    offset = 2
    sim = _sim(
        "oral_prep_plus_contraceptive",
        efficacy=0.9,
        adherence=0.8,
        substitution=0.4,
        target_coverages=[{"sex": "Female", "risk_group": "High risk heterosexual", "coverage": 0.20}],
    )

    apply_simulation(lp, ivs, sim)

    assert lp["prep_effectiveness"][offset, RN_Substitution] == pytest.approx(0.4)


def test_prep_duration_maps_for_implantable():
    lp = _prep_params()
    ivs = _iv("implantable_prep", "Implantable PrEP")
    offset = 8
    sim = _sim(
        "implantable_prep",
        efficacy=0.9,
        adherence=0.8,
        duration=12.0,
        target_coverages=[{"sex": "Female", "risk_group": "High risk heterosexual", "coverage": 0.20}],
    )

    apply_simulation(lp, ivs, sim)

    assert lp["prep_effectiveness"][offset, RN_Duration] == pytest.approx(12.0)


def test_prep_leaves_substitution_and_duration_default_when_unset():
    lp = _prep_params()
    ivs = _iv("oral_prep_daily", "Oral PrEP (daily)")
    sim = _sim(
        "oral_prep_daily",
        efficacy=0.9,
        adherence=0.8,
        target_coverages=[{"sex": "Female", "risk_group": "High risk heterosexual", "coverage": 0.20}],
    )

    apply_simulation(lp, ivs, sim)

    assert lp["prep_effectiveness"][0, RN_Substitution] == 0.0
    assert lp["prep_effectiveness"][0, RN_Duration] == 0.0


def test_prep_multi_product_aggregates_cov_and_sets_method_mix():
    """Two products targeting the same (sex, risk_group): cov sums, method mix weights by share."""
    lp = _prep_params()
    ivs = [
        InterventionOut(id="oral_prep_daily", product="Oral PrEP (daily)"),
        InterventionOut(id="injectable_prep_2_month", product="Injectable PrEP (2 month)"),
    ]
    sim = {
        "oral_prep_daily": InterventionSimulation({
            "target_year": _TARGET_YEAR,
            "efficacy": 0.9,
            "adherence": 0.8,
            "target_coverages": [TargetCoverage(sex="Female", risk_group="High risk heterosexual", coverage=0.30)],
        }),
        "injectable_prep_2_month": InterventionSimulation({
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
        InterventionOut(id="oral_prep_daily", product="Oral PrEP (daily)"),
        InterventionOut(id="injectable_prep_2_month", product="Injectable PrEP (2 month)"),
    ]
    # 0.70 + 0.50 = 1.20 → clamped to 1.0; mix = 0.70/1.20, 0.50/1.20
    sim = {
        "oral_prep_daily": InterventionSimulation({
            "target_year": _TARGET_YEAR,
            "efficacy": 0.9,
            "adherence": 0.8,
            "target_coverages": [TargetCoverage(sex="Female", risk_group="High risk heterosexual", coverage=0.70)],
        }),
        "injectable_prep_2_month": InterventionSimulation({
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
    ivs = [InterventionOut(id="oral_prep_daily", product="Oral PrEP (daily)")]
    sim = {
        "oral_prep_daily": InterventionSimulation({
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
    ivs = _iv("cure_adults_and_children", "Cure (adults and children)")
    sim = _sim(
        "cure_adults_and_children",
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
    ivs = _iv("cure_adults_and_children", "Cure (adults and children)")
    sim = _sim(
        "cure_adults_and_children",
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
    ivs = _iv("cure_adults_and_children", "Cure (adults and children)")
    sim = _sim(
        "cure_adults_and_children",
        target_coverages=[{"sex": "Both", "risk_group": "High risk heterosexual", "coverage": 0.20}],
        efficacy=0.70,
        duration_of_cure=4.0,
    )

    apply_simulation(lp, ivs, sim)

    assert lp["rn_cure_coverage_type"] == RN_Diff
    assert lp["rn_cure_coverage_rg"][RN_HRH, _TARGET_YEAR_IDX] == pytest.approx(0.20)
    assert lp["rn_cure_coverage_rg"][RN_HRH_F, _TARGET_YEAR_IDX] == pytest.approx(0.20)


# ---------------------------------------------------------------------------
# Cure (neonates)
# ---------------------------------------------------------------------------


def test_cure_neonates_writes_coverage_and_effect():
    lp = _cure_neonate_params()
    ivs = _iv("cure_neonates", "Cure (neonates)")
    sim = _sim(
        "cure_neonates",
        target_coverages=[{"sex": None, "risk_group": "Neonates", "coverage": 0.40}],
        effectiveness=0.65,
    )

    apply_simulation(lp, ivs, sim)

    assert lp["rn_cure_coverage_neonates"][_TARGET_YEAR_IDX] == pytest.approx(0.40)
    assert lp["rn_cure_effect_neonates"] == pytest.approx(0.65)


# ---------------------------------------------------------------------------
# Vaginal microbiome modification (VMM)
# ---------------------------------------------------------------------------


def test_vmm_percent_of_women_writes_coverage_all():
    lp = _vmm_params()
    ivs = _iv("vaginal_microbiome_modification", "Vaginal microbiome modification")
    sim = _sim(
        "vaginal_microbiome_modification",
        target_coverages=[{"sex": None, "risk_group": "Percent of women treated", "coverage": 0.55}],
        effectiveness=0.30,
    )

    apply_simulation(lp, ivs, sim)

    assert lp["rn_vmm_coverage_type"] == 0  # _VMM_COV_ALLRISK
    assert lp["rn_vmm_coverage_all"][_TARGET_YEAR_IDX] == pytest.approx(0.55)
    assert lp["rn_vmm_effect"] == pytest.approx(0.30)


def test_vmm_risk_groups_write_coverage_rg():
    lp = _vmm_params()
    ivs = _iv("vaginal_microbiome_modification", "Vaginal microbiome modification")
    sim = _sim(
        "vaginal_microbiome_modification",
        target_coverages=[
            {"sex": None, "risk_group": "Not sexually active", "coverage": 0.10},
            {"sex": None, "risk_group": "Low risk heterosexual", "coverage": 0.20},
            {"sex": None, "risk_group": "Medium risk heterosexual", "coverage": 0.30},
            {"sex": None, "risk_group": "High risk heterosexual", "coverage": 0.40},
        ],
        effectiveness=0.50,
    )

    apply_simulation(lp, ivs, sim)

    assert lp["rn_vmm_coverage_type"] == 1  # _VMM_COV_SINGLE
    assert lp["rn_vmm_coverage_rg"][0, _TARGET_YEAR_IDX] == pytest.approx(0.10)
    assert lp["rn_vmm_coverage_rg"][1, _TARGET_YEAR_IDX] == pytest.approx(0.20)
    assert lp["rn_vmm_coverage_rg"][2, _TARGET_YEAR_IDX] == pytest.approx(0.30)
    assert lp["rn_vmm_coverage_rg"][3, _TARGET_YEAR_IDX] == pytest.approx(0.40)
    assert lp["rn_vmm_effect"] == pytest.approx(0.50)


# ---------------------------------------------------------------------------
# AHD treatment — not yet fully implemented
# ---------------------------------------------------------------------------


def test_ahd_treatment_writes_coverage_and_mortality_reduction():
    lp = _ahd_params()
    ivs = _iv("ahd_treatment", "AHD treatment")
    sim = _sim("ahd_treatment", target_coverage=0.80, reduction_in_mortality=0.60)

    apply_simulation(lp, ivs, sim)

    assert lp["rn_ahd_treat_cov"][_TARGET_YEAR_IDX] == pytest.approx(0.80)
    assert lp["rn_ahd_treat_reduc_mort"] == pytest.approx(0.60)


# ---------------------------------------------------------------------------
# POC tests — not yet fully implemented
# ---------------------------------------------------------------------------


def test_poc_viral_load_writes_coverage_and_effect():
    lp = _poc_params()
    ivs = _iv("poc_vl_test", "POC VL test")
    sim = _sim("poc_vl_test", target_coverage=0.70, effect=0.12)

    apply_simulation(lp, ivs, sim)

    assert lp["rn_poc_cov"][RN_POC_VL, _TARGET_YEAR_IDX] == pytest.approx(0.70)
    assert lp["rn_poc_effect"][RN_POC_VL] == pytest.approx(0.12)


def test_poc_cd4_writes_coverage_and_effect():
    lp = _poc_params()
    ivs = _iv("poc_cd4_test", "POC CD4 test")
    sim = _sim("poc_cd4_test", target_coverage=0.65, effect=0.25)

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
        "art15plus_num": np.zeros((_N_SEXES_ART, _N_YEARS_ART)),
        "art15plus_isperc": np.zeros((_N_SEXES_ART, _N_YEARS_ART)),
    }


def test_adult_art_male_writes_male_index():
    lp = _adult_art_params()
    ivs = _iv("adult_art", "Adult ART")
    sim = _sim("adult_art", target_coverages=[{"sex": "Male", "risk_group": None, "coverage": 0.75}])

    apply_simulation(lp, ivs, sim)

    assert lp["art15plus_num"][0, _TARGET_YEAR_IDX] == pytest.approx(0.75)
    assert lp["art15plus_num"][1, _TARGET_YEAR_IDX] == 0.0
    assert lp["art15plus_isperc"][0, _TARGET_YEAR_IDX] == 1
    assert lp["art15plus_isperc"][1, _TARGET_YEAR_IDX] == 0


def test_adult_art_female_writes_female_index():
    lp = _adult_art_params()
    ivs = _iv("adult_art", "Adult ART")
    sim = _sim("adult_art", target_coverages=[{"sex": "Female", "risk_group": None, "coverage": 0.60}])

    apply_simulation(lp, ivs, sim)

    assert lp["art15plus_num"][0, _TARGET_YEAR_IDX] == 0.0
    assert lp["art15plus_num"][1, _TARGET_YEAR_IDX] == pytest.approx(0.60)
    assert lp["art15plus_isperc"][0, _TARGET_YEAR_IDX] == 0
    assert lp["art15plus_isperc"][1, _TARGET_YEAR_IDX] == 1


def test_adult_art_both_writes_male_and_female():
    lp = _adult_art_params()
    ivs = _iv("adult_art", "Adult ART")
    sim = _sim("adult_art", target_coverages=[{"sex": "Both", "risk_group": None, "coverage": 0.80}])

    apply_simulation(lp, ivs, sim)

    assert lp["art15plus_num"][0, _TARGET_YEAR_IDX] == pytest.approx(0.80)
    assert lp["art15plus_num"][1, _TARGET_YEAR_IDX] == pytest.approx(0.80)
    assert lp["art15plus_isperc"][0, _TARGET_YEAR_IDX] == 1
    assert lp["art15plus_isperc"][1, _TARGET_YEAR_IDX] == 1


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

    assert lp["art15plus_num"][0, _TARGET_YEAR_IDX] == pytest.approx(0.75)
    assert lp["art15plus_num"][1, _TARGET_YEAR_IDX] == pytest.approx(0.60)
    assert lp["art15plus_isperc"][0, _TARGET_YEAR_IDX] == 1
    assert lp["art15plus_isperc"][1, _TARGET_YEAR_IDX] == 1


# ---------------------------------------------------------------------------
# Long-acting treatment — accepted but currently a no-op (not yet wired to the
# Goals model). It must not raise and must not modify params.
# ---------------------------------------------------------------------------


def test_long_acting_treatment_is_noop():
    lp = {"projection_start_year": _START_YEAR}
    ivs = [InterventionOut(id="long_acting_treatment", product="Long-acting treatment")]
    sim = {
        "long_acting_treatment": InterventionSimulation({
            "interruption_rate_reduction": 0.25,
            "viral_load_suppression_ratio": 0.80,
        })
    }

    # Should not raise; leaves params untouched (no effect on the model yet).
    apply_simulation(lp, ivs, sim)
    assert lp == {"projection_start_year": _START_YEAR}


# ---------------------------------------------------------------------------
# Unknown intervention
# ---------------------------------------------------------------------------


def test_unknown_intervention_raises_value_error():
    lp = {"projection_start_year": _START_YEAR}
    ivs = [InterventionOut(id="not_a_real_intervention", product="???")]
    sim = {"not_a_real_intervention": InterventionSimulation({"target_year": _TARGET_YEAR})}

    with pytest.raises(ValueError, match="Unknown intervention"):
        apply_simulation(lp, ivs, sim)
