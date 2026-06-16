"""Unit tests for scenario_definition models and their validators."""

import pytest
from pydantic import ValidationError

from avenir_goals_scenario.models.scenario_definition import (
    CureParameters,
    LongActingTreatmentParameters,
    NormalDistParameters,
    POCTestParameters,
    PrepParameters,
    PrepTarget,
    VaccineCureTarget,
)

_PREP_BASE = {
    "adherence": NormalDistParameters(mean=0.85, sd=0.05),
    "target_coverage": NormalDistParameters(mean=0.3, sd=0.05),
    "target_year": NormalDistParameters(mean=2028, sd=2),
}


# ---------------------------------------------------------------------------
# _apply_proportion_defaults branch coverage
# ---------------------------------------------------------------------------


def test_proportion_defaults_not_overwritten_when_min_value_already_set():
    params = PrepParameters(efficacy=NormalDistParameters(mean=0.9, sd=0.01, min_value=0.5), **_PREP_BASE)
    assert params.efficacy.min_value == 0.5
    assert params.efficacy.max_value == 1.0


def test_proportion_defaults_not_overwritten_when_max_value_already_set():
    params = PrepParameters(efficacy=NormalDistParameters(mean=0.9, sd=0.01, max_value=0.95), **_PREP_BASE)
    assert params.efficacy.max_value == 0.95
    assert params.efficacy.min_value == 0.0


def test_proportion_defaults_no_op_when_both_already_set():
    params = PrepParameters(
        efficacy=NormalDistParameters(mean=0.9, sd=0.01, min_value=0.2, max_value=0.99), **_PREP_BASE
    )
    assert params.efficacy.min_value == 0.2
    assert params.efficacy.max_value == 0.99


# ---------------------------------------------------------------------------
# PrepTarget MSM + Female validation
# ---------------------------------------------------------------------------


def test_risk_group_target_msm_female_raises():
    with pytest.raises(ValidationError, match="cannot have sex='Female'"):
        PrepTarget(risk_group="Men who have sex with men", sex="Female")


# ---------------------------------------------------------------------------
# VaccineCureTarget validation
# ---------------------------------------------------------------------------


def test_vaccine_cure_target_plhiv_both_is_valid():
    t = VaccineCureTarget(risk_group="PLHIV", sex="Both")
    assert t.risk_group == "PLHIV"
    assert t.sex == "Both"


def test_vaccine_cure_target_plhiv_none_is_valid():
    t = VaccineCureTarget(risk_group="PLHIV")
    assert t.sex is None


def test_vaccine_cure_target_plhiv_male_raises():
    with pytest.raises(ValidationError, match="PLHIV target must have sex='Both' or sex=None"):
        VaccineCureTarget(risk_group="PLHIV", sex="Male")


def test_vaccine_cure_target_plhiv_female_raises():
    with pytest.raises(ValidationError, match="PLHIV target must have sex='Both' or sex=None"):
        VaccineCureTarget(risk_group="PLHIV", sex="Female")


def test_vaccine_cure_target_risk_group_msm_female_raises():
    with pytest.raises(ValidationError, match="cannot have sex='Female'"):
        VaccineCureTarget(risk_group="Men who have sex with men", sex="Female")


def test_vaccine_cure_target_risk_group_both_is_valid():
    t = VaccineCureTarget(risk_group="High risk heterosexual", sex="Both")
    assert t.sex == "Both"


# ---------------------------------------------------------------------------
# CureParameters constraints
# ---------------------------------------------------------------------------


def test_cure_parameters_applies_constraints():
    params = CureParameters(
        target_year=NormalDistParameters(mean=2032, sd=3),
        target_coverage=NormalDistParameters(mean=0.5, sd=0.1),
        efficacy=NormalDistParameters(mean=0.8, sd=0.1),
        duration_of_cure=NormalDistParameters(mean=5.0, sd=1.0),
    )
    assert params.target_year.integer is True
    assert params.target_year.min_value == 1970
    assert params.target_coverage.min_value == 0.0
    assert params.target_coverage.max_value == 1.0
    assert params.efficacy.min_value == 0.0
    assert params.efficacy.max_value == 1.0


# ---------------------------------------------------------------------------
# POCTestParameters constraints
# ---------------------------------------------------------------------------


def test_poc_test_parameters_applies_constraints():
    params = POCTestParameters(
        target_year=NormalDistParameters(mean=2027, sd=2),
        target_coverage=NormalDistParameters(mean=0.1, sd=0.05),
        effect=NormalDistParameters(mean=0.8, sd=0.1),
    )
    assert params.target_year.integer is True
    assert params.target_year.min_value == 1970
    assert params.target_coverage.min_value == 0.0
    assert params.target_coverage.max_value == 1.0
    assert params.effect.min_value == 0.0
    assert params.effect.max_value == 1.0


# ---------------------------------------------------------------------------
# LongActingTreatmentParameters constraints
# ---------------------------------------------------------------------------


def test_lat_parameters_applies_proportion_defaults():
    params = LongActingTreatmentParameters(
        interruption_rate_reduction=NormalDistParameters(mean=0.95, sd=0.02),
        viral_load_suppression_ratio=NormalDistParameters(mean=0.99, sd=0.01),
    )
    assert params.interruption_rate_reduction.min_value == 0.0
    assert params.interruption_rate_reduction.max_value == 1.0
    assert params.viral_load_suppression_ratio.min_value == 0.0
    assert params.viral_load_suppression_ratio.max_value == 1.0
