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
)

from avenir_goals_scenario._runner.simulation import apply_simulation
from avenir_goals_scenario.models import InterventionOut, InterventionSimulation, PrepTarget, VaccineCureTarget
from avenir_goals_scenario.models.scenario_definition import LongActingTreatmentTarget

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


def _iv(intervention_id: str, product: str, targets: list) -> list[InterventionOut]:
    return [InterventionOut(id=intervention_id, product=product, targets=targets)]


def _hrh_f() -> PrepTarget:
    return PrepTarget(risk_group="High risk heterosexual", sex="Female")


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
    target = _hrh_f()  # Female → sex_idx=1, HRH → pop_idx=RN_HRH=4
    ivs = _iv(pid, product, [target])
    sim = _sim(pid, efficacy=0.95, adherence=0.85, target_coverage=0.30)

    apply_simulation(lp, ivs, sim)

    eff = lp["prep_effectiveness"]
    assert eff[offset, RN_Effectiveness] == pytest.approx(0.95)
    assert eff[offset, RN_Adherence] == pytest.approx(0.85)
    assert lp["prep_cov"][1, RN_HRH, _TARGET_YEAR_IDX] == pytest.approx(0.30)


def test_prep_multiple_targets_writes_each_population():
    lp = _prep_params()
    targets = [
        PrepTarget(risk_group="High risk heterosexual", sex="Female"),
        PrepTarget(risk_group="Men who have sex with men", sex="Male"),
    ]
    ivs = _iv("daily_prep", "Daily PrEP", targets)
    sim = _sim("daily_prep", efficacy=0.9, adherence=0.8, target_coverage=0.20)

    apply_simulation(lp, ivs, sim)

    # Female HRH (sex=1, pop=RN_HRH)
    assert lp["prep_cov"][1, RN_HRH, _TARGET_YEAR_IDX] == pytest.approx(0.20)
    # Male MSM (sex=0, pop=RN_MSM)
    assert lp["prep_cov"][0, RN_MSM, _TARGET_YEAR_IDX] == pytest.approx(0.20)


def test_prep_does_not_write_other_products():
    lp = _prep_params()
    ivs = _iv("daily_prep", "Daily PrEP", [_hrh_f()])
    sim = _sim("daily_prep", efficacy=0.9, adherence=0.8, target_coverage=0.20)

    apply_simulation(lp, ivs, sim)

    daily_offset = 0  # RN_PrEPOralDaily - RN_PrEPOralDaily
    for i in range(_N_PREP):
        if i != daily_offset:
            assert lp["prep_effectiveness"][i, RN_Effectiveness] == 0.0
            assert lp["prep_effectiveness"][i, RN_Adherence] == 0.0


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
    target = VaccineCureTarget(risk_group="PLHIV", sex="Both")
    ivs = _iv("vaccine", "Vaccine", [target])
    sim = _sim("vaccine", target_coverage=0.50, **_VAC_SIM_BASE)

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
    target = VaccineCureTarget(risk_group="PLHIV")  # sex defaults to None
    ivs = _iv("vaccine", "Vaccine", [target])
    sim = _sim("vaccine", target_coverage=0.45, **_VAC_SIM_BASE)

    apply_simulation(lp, ivs, sim)

    assert lp["rn_vac_cov_type"] == RN_Single
    assert lp["rn_vac_coverage_rg"][RN_AllRisk, _TARGET_YEAR_IDX] == pytest.approx(0.45)


def test_vaccine_risk_group_female_writes_female_index():
    lp = _vaccine_params()
    target = VaccineCureTarget(risk_group="High risk heterosexual", sex="Female")
    ivs = _iv("vaccine", "Vaccine", [target])
    sim = _sim(
        "vaccine",
        target_coverage=0.40,
        **{**_VAC_SIM_BASE, "vaccine_action_type": "Degree", "targeting": "Vaccinate only HIV-negative individuals"},
    )

    apply_simulation(lp, ivs, sim)

    assert lp["rn_vac_cov_type"] == RN_Diff
    assert lp["rn_vac_coverage_rg"][RN_HRH_F, _TARGET_YEAR_IDX] == pytest.approx(0.40)
    assert lp["rn_vac_targetting"] == 1


def test_vaccine_risk_group_both_writes_male_and_female():
    lp = _vaccine_params()
    target = VaccineCureTarget(risk_group="High risk heterosexual", sex="Both")
    ivs = _iv("vaccine", "Vaccine", [target])
    sim = _sim("vaccine", target_coverage=0.35, **_VAC_SIM_BASE)

    apply_simulation(lp, ivs, sim)

    assert lp["rn_vac_cov_type"] == RN_Diff
    assert lp["rn_vac_coverage_rg"][RN_HRH, _TARGET_YEAR_IDX] == pytest.approx(0.35)
    assert lp["rn_vac_coverage_rg"][RN_HRH_F, _TARGET_YEAR_IDX] == pytest.approx(0.35)


def test_vaccine_invalid_action_type_raises():
    lp = _vaccine_params()
    ivs = _iv("vaccine", "Vaccine", [VaccineCureTarget(risk_group="PLHIV")])
    sim = _sim("vaccine", target_coverage=0.50, **{**_VAC_SIM_BASE, "vaccine_action_type": "Invalid"})

    with pytest.raises(ValueError, match="vaccine_action_type"):
        apply_simulation(lp, ivs, sim)


def test_vaccine_invalid_targeting_raises():
    lp = _vaccine_params()
    ivs = _iv("vaccine", "Vaccine", [VaccineCureTarget(risk_group="PLHIV")])
    sim = _sim("vaccine", target_coverage=0.50, **{**_VAC_SIM_BASE, "targeting": "Invalid"})

    with pytest.raises(ValueError, match="targeting"):
        apply_simulation(lp, ivs, sim)


# ---------------------------------------------------------------------------
# Cure
# ---------------------------------------------------------------------------


def test_cure_plhiv_target_writes_all_risk():
    lp = _cure_params()
    target = VaccineCureTarget(risk_group="PLHIV", sex="Both")
    ivs = _iv("cure", "Cure", [target])
    sim = _sim("cure", target_coverage=0.30, efficacy=0.80, duration_of_cure=5.0)

    apply_simulation(lp, ivs, sim)

    assert lp["rn_cure_coverage_type"] == RN_Single
    assert lp["rn_cure_coverage_rg"][RN_AllRisk, _TARGET_YEAR_IDX] == pytest.approx(0.30)
    assert lp["rn_cure_effect"][RN_Efficacy] == pytest.approx(0.80)
    assert lp["rn_cure_effect"][RN_Duration] == pytest.approx(5.0)


def test_cure_risk_group_female_writes_female_index():
    lp = _cure_params()
    target = VaccineCureTarget(risk_group="High risk heterosexual", sex="Female")
    ivs = _iv("cure", "Cure", [target])
    sim = _sim("cure", target_coverage=0.25, efficacy=0.75, duration_of_cure=3.0)

    apply_simulation(lp, ivs, sim)

    assert lp["rn_cure_coverage_type"] == RN_Diff
    assert lp["rn_cure_coverage_rg"][RN_HRH_F, _TARGET_YEAR_IDX] == pytest.approx(0.25)
    assert lp["rn_cure_effect"][RN_Efficacy] == pytest.approx(0.75)
    assert lp["rn_cure_effect"][RN_Duration] == pytest.approx(3.0)


def test_cure_risk_group_both_writes_male_and_female():
    lp = _cure_params()
    target = VaccineCureTarget(risk_group="High risk heterosexual", sex="Both")
    ivs = _iv("cure", "Cure", [target])
    sim = _sim("cure", target_coverage=0.20, efficacy=0.70, duration_of_cure=4.0)

    apply_simulation(lp, ivs, sim)

    assert lp["rn_cure_coverage_type"] == RN_Diff
    assert lp["rn_cure_coverage_rg"][RN_HRH, _TARGET_YEAR_IDX] == pytest.approx(0.20)
    assert lp["rn_cure_coverage_rg"][RN_HRH_F, _TARGET_YEAR_IDX] == pytest.approx(0.20)


# ---------------------------------------------------------------------------
# AHD treatment — not yet fully implemented
# ---------------------------------------------------------------------------


def test_ahd_treatment_writes_coverage_and_mortality_reduction():
    lp = _ahd_params()
    ivs = _iv("ahd_treatment", "AHD treatment", [])
    sim = _sim("ahd_treatment", target_coverage=0.80, reduction_in_mortality=0.60)

    apply_simulation(lp, ivs, sim)

    assert lp["rn_adh_treat_cov"][_TARGET_YEAR_IDX] == pytest.approx(0.80)
    assert lp["rn_adh_treat_reduc_mort"] == pytest.approx(0.60)


# ---------------------------------------------------------------------------
# POC tests — not yet fully implemented
# ---------------------------------------------------------------------------


def test_poc_viral_load_writes_coverage_and_effect():
    lp = _poc_params()
    ivs = _iv("point_of_care_viral_load_test", "Point of care viral load test", [])
    sim = _sim("point_of_care_viral_load_test", target_coverage=0.70, effect=0.12)

    apply_simulation(lp, ivs, sim)

    assert lp["rn_poc_cov"][RN_POC_VL, _TARGET_YEAR_IDX] == pytest.approx(0.70)
    assert lp["rn_poc_effect"][RN_POC_VL] == pytest.approx(0.12)


def test_poc_cd4_writes_coverage_and_effect():
    lp = _poc_params()
    ivs = _iv("point_of_care_cd4_test", "Point of care CD4 test", [])
    sim = _sim("point_of_care_cd4_test", target_coverage=0.65, effect=0.25)

    apply_simulation(lp, ivs, sim)

    assert lp["rn_poc_cov"][RN_POC_CD4, _TARGET_YEAR_IDX] == pytest.approx(0.65)
    assert lp["rn_poc_effect"][RN_POC_CD4] == pytest.approx(0.25)


# ---------------------------------------------------------------------------
# Long-acting treatment — target_year absent from params (known limitation)
# ---------------------------------------------------------------------------


def test_long_acting_treatment_raises_not_implemented():
    lp = {"projection_start_year": _START_YEAR}
    target = LongActingTreatmentTarget(risk_group="Key populations", sex="Both")
    ivs = [InterventionOut(id="long_acting_treatment", product="Long-acting treatment", targets=[target])]
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
    ivs = [InterventionOut(id="not_a_real_intervention", product="???", targets=[])]
    sim = {"not_a_real_intervention": InterventionSimulation({"target_year": _TARGET_YEAR})}

    with pytest.raises(ValueError, match="Unknown intervention"):
        apply_simulation(lp, ivs, sim)
