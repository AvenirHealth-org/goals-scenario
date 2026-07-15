"""Unit tests for scenario_definition models and their validators."""

import pytest
from pydantic import ValidationError

from avenir_goals_scenario.models.scenario_definition import (
    AdultARTParameters,
    AdultARTTarget,
    CureNeonateParameters,
    CureNeonateTarget,
    CureParameters,
    LongActingTreatmentParameters,
    NormalDistParameters,
    POCTestParameters,
    PrepInterventionDef,
    PrepParameters,
    PrepTarget,
    ScenarioInput,
    SingleScenarioDef,
    VaccineCureTarget,
    VMMInterventionDef,
    VMMParameters,
    VMMTarget,
)

_PREP_BASE = {
    "adherence": NormalDistParameters(mean=0.85, sd=0.05),
    "target_year": NormalDistParameters(mean=2028, sd=2),
}

_ANY_COV = NormalDistParameters(mean=0.3, sd=0.05)


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
# Product-specific PrEP parameters: substitution and duration
# ---------------------------------------------------------------------------

_PREP_FULL = {"efficacy": NormalDistParameters(mean=0.9, sd=0.01), **_PREP_BASE}


def _prep_target() -> PrepTarget:
    return PrepTarget(risk_group="High risk heterosexual", sex="Female", target_coverage=_ANY_COV)


def test_substitution_applies_proportion_defaults():
    params = PrepParameters(substitution=NormalDistParameters(mean=0.4, sd=0.05), **_PREP_FULL)
    assert params.substitution is not None
    assert params.substitution.min_value == 0.0
    assert params.substitution.max_value == 1.0


def test_duration_applies_nonneg_default():
    params = PrepParameters(duration=NormalDistParameters(mean=12.0, sd=2.0), **_PREP_FULL)
    assert params.duration is not None
    assert params.duration.min_value == 0.0
    assert params.duration.max_value is None


def test_substitution_valid_on_oral_contraceptive():
    iv = PrepInterventionDef(
        product="Oral PrEP plus contraceptive",
        targets=[_prep_target()],
        parameters=PrepParameters(substitution=NormalDistParameters(mean=0.4, sd=0.05), **_PREP_FULL),
    )
    assert iv.parameters.substitution is not None


def test_duration_valid_on_implantable():
    iv = PrepInterventionDef(
        product="Implantable PrEP",
        targets=[_prep_target()],
        parameters=PrepParameters(duration=NormalDistParameters(mean=12.0, sd=2.0), **_PREP_FULL),
    )
    assert iv.parameters.duration is not None


def test_substitution_on_other_product_raises():
    with pytest.raises(ValidationError, match="'substitution' parameter is only valid"):
        PrepInterventionDef(
            product="Oral PrEP (daily)",
            targets=[_prep_target()],
            parameters=PrepParameters(substitution=NormalDistParameters(mean=0.4, sd=0.05), **_PREP_FULL),
        )


def test_duration_on_other_product_raises():
    with pytest.raises(ValidationError, match="'duration' parameter is only valid"):
        PrepInterventionDef(
            product="Oral PrEP (daily)",
            targets=[_prep_target()],
            parameters=PrepParameters(duration=NormalDistParameters(mean=12.0, sd=2.0), **_PREP_FULL),
        )


# ---------------------------------------------------------------------------
# PrepTarget MSM + Female validation
# ---------------------------------------------------------------------------


def test_risk_group_target_msm_female_raises():
    with pytest.raises(ValidationError, match="cannot have sex='Female'"):
        PrepTarget(risk_group="Men who have sex with men", sex="Female", target_coverage=_ANY_COV)


# ---------------------------------------------------------------------------
# VaccineCureTarget validation
# ---------------------------------------------------------------------------


def test_vaccine_cure_target_plhiv_both_is_valid():
    t = VaccineCureTarget(risk_group="PLHIV", sex="Both", target_coverage=_ANY_COV)
    assert t.risk_group == "PLHIV"
    assert t.sex == "Both"


def test_vaccine_cure_target_plhiv_none_is_valid():
    t = VaccineCureTarget(risk_group="PLHIV", target_coverage=_ANY_COV)
    assert t.sex is None


def test_vaccine_cure_target_plhiv_male_raises():
    with pytest.raises(ValidationError, match="PLHIV target must have sex='Both' or sex=None"):
        VaccineCureTarget(risk_group="PLHIV", sex="Male", target_coverage=_ANY_COV)


def test_vaccine_cure_target_plhiv_female_raises():
    with pytest.raises(ValidationError, match="PLHIV target must have sex='Both' or sex=None"):
        VaccineCureTarget(risk_group="PLHIV", sex="Female", target_coverage=_ANY_COV)


def test_vaccine_cure_target_risk_group_msm_female_raises():
    with pytest.raises(ValidationError, match="cannot have sex='Female'"):
        VaccineCureTarget(risk_group="Men who have sex with men", sex="Female", target_coverage=_ANY_COV)


def test_vaccine_cure_target_risk_group_both_is_valid():
    t = VaccineCureTarget(risk_group="High risk heterosexual", sex="Both", target_coverage=_ANY_COV)
    assert t.sex == "Both"


def test_vaccine_cure_target_coverage_gets_proportion_bounds():
    t = VaccineCureTarget(risk_group="PLHIV", sex="Both", target_coverage=NormalDistParameters(mean=0.5, sd=0.1))
    assert t.target_coverage.min_value == 0.0
    assert t.target_coverage.max_value == 1.0


# ---------------------------------------------------------------------------
# CureParameters constraints
# ---------------------------------------------------------------------------


def test_cure_parameters_applies_constraints():
    params = CureParameters(
        target_year=NormalDistParameters(mean=2032, sd=3),
        efficacy=NormalDistParameters(mean=0.8, sd=0.1),
        duration_of_cure=NormalDistParameters(mean=5.0, sd=1.0),
    )
    assert params.target_year.integer is True
    assert params.target_year.min_value == 1970
    assert params.efficacy.min_value == 0.0
    assert params.efficacy.max_value == 1.0


# ---------------------------------------------------------------------------
# Cure (neonates) and VMM
# ---------------------------------------------------------------------------


def test_cure_neonate_parameters_applies_constraints():
    params = CureNeonateParameters(
        target_year=NormalDistParameters(mean=2032, sd=3),
        effectiveness=NormalDistParameters(mean=0.6, sd=0.1),
    )
    assert params.target_year.integer is True
    assert params.target_year.min_value == 1970
    assert params.effectiveness.min_value == 0.0
    assert params.effectiveness.max_value == 1.0


def test_cure_neonate_target_coverage_gets_proportion_bounds():
    target = CureNeonateTarget(risk_group="Neonates", target_coverage=NormalDistParameters(mean=0.4, sd=0.05))
    assert target.target_coverage.min_value == 0.0
    assert target.target_coverage.max_value == 1.0


def test_vmm_parameters_applies_constraints():
    params = VMMParameters(
        target_year=NormalDistParameters(mean=2030, sd=2),
        effectiveness=NormalDistParameters(mean=0.3, sd=0.05),
    )
    assert params.target_year.integer is True
    assert params.target_year.min_value == 1970
    assert params.effectiveness.min_value == 0.0
    assert params.effectiveness.max_value == 1.0


def _vmm_def(targets: list[VMMTarget]) -> VMMInterventionDef:
    return VMMInterventionDef(
        product="Vaginal microbiome modification",
        targets=targets,
        parameters=VMMParameters(
            target_year=NormalDistParameters(mean=2030, sd=2),
            effectiveness=NormalDistParameters(mean=0.3, sd=0.05),
        ),
    )


def test_vmm_risk_group_targets_valid():
    iv = _vmm_def([
        VMMTarget(risk_group="Not sexually active", target_coverage=_ANY_COV),
        VMMTarget(risk_group="High risk heterosexual", target_coverage=_ANY_COV),
    ])
    assert len(iv.targets) == 2


def test_vmm_percent_of_women_alone_is_valid():
    iv = _vmm_def([VMMTarget(risk_group="Percent of women treated", target_coverage=_ANY_COV)])
    assert iv.targets[0].risk_group == "Percent of women treated"


def test_vmm_percent_of_women_mixed_with_risk_group_raises():
    with pytest.raises(ValidationError, match="only target"):
        _vmm_def([
            VMMTarget(risk_group="Percent of women treated", target_coverage=_ANY_COV),
            VMMTarget(risk_group="Low risk heterosexual", target_coverage=_ANY_COV),
        ])


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
        target_year=NormalDistParameters(mean=2030, sd=0.0),
        target_coverage=NormalDistParameters(mean=0.7, sd=0.0),
        interruption_rate_reduction=NormalDistParameters(mean=0.95, sd=0.02),
        viral_load_suppression_ratio=NormalDistParameters(mean=0.99, sd=0.01),
    )
    assert params.target_year.integer is True
    assert params.target_year.min_value == 1970
    assert params.target_coverage.min_value == 0.0
    assert params.target_coverage.max_value == 1.0
    assert params.interruption_rate_reduction.min_value == 0.0
    assert params.interruption_rate_reduction.max_value == 1.0
    assert params.viral_load_suppression_ratio.min_value == 0.0
    assert params.viral_load_suppression_ratio.max_value == 1.0


# ---------------------------------------------------------------------------
# AdultARTTarget
# ---------------------------------------------------------------------------


def test_adult_art_target_male_is_valid():
    t = AdultARTTarget(sex="Male", target_initiation_rate=_ANY_COV)
    assert t.sex == "Male"


def test_adult_art_target_female_is_valid():
    t = AdultARTTarget(sex="Female", target_initiation_rate=_ANY_COV)
    assert t.sex == "Female"


def test_adult_art_target_both_is_valid():
    t = AdultARTTarget(sex="Both", target_initiation_rate=_ANY_COV)
    assert t.sex == "Both"


def test_adult_art_target_initiation_rate_gets_proportion_bounds():
    t = AdultARTTarget(sex="Male", target_initiation_rate=NormalDistParameters(mean=0.7, sd=0.05))
    assert t.target_initiation_rate.min_value == 0.0
    assert t.target_initiation_rate.max_value == 1.0


def test_adult_art_target_initiation_rate_preserves_custom_min():
    t = AdultARTTarget(sex="Male", target_initiation_rate=NormalDistParameters(mean=0.7, sd=0.05, min_value=0.3))
    assert t.target_initiation_rate.min_value == 0.3
    assert t.target_initiation_rate.max_value == 1.0


# ---------------------------------------------------------------------------
# AdultARTParameters constraints
# ---------------------------------------------------------------------------


def test_adult_art_parameters_applies_constraints():
    params = AdultARTParameters(
        target_year=NormalDistParameters(mean=2030, sd=2),
    )
    assert params.target_year.integer is True
    assert params.target_year.min_value == 1970


# ---------------------------------------------------------------------------
# SingleScenarioDef duplicate-product validation
# ---------------------------------------------------------------------------

_AHD_PARAMS = {
    "target_year": {"mean": 2026, "sd": 1},
    "target_coverage": {"mean": 0.7, "sd": 0.05},
    "reduction_in_mortality": {"mean": 0.4, "sd": 0.05},
}

_ADULT_ART_PARAMS = {
    "target_year": {"mean": 2028, "sd": 2},
}

_ADULT_ART_TARGET = {"sex": "Female", "target_initiation_rate": _ANY_COV}
_ADULT_ART_TARGET_M = {"sex": "Male", "target_initiation_rate": _ANY_COV}


def test_single_scenario_duplicate_no_target_product_raises():
    with pytest.raises(ValidationError, match="duplicate product 'AHD treatment'"):
        SingleScenarioDef.model_validate({
            "id": "s1",
            "interventions": [
                {"product": "AHD treatment", "parameters": _AHD_PARAMS},
                {"product": "AHD treatment", "parameters": _AHD_PARAMS},
            ],
        })


def test_single_scenario_duplicate_adult_art_sex_raises():
    with pytest.raises(ValidationError, match=r"duplicate \(product, sex\).*Adult ART.*Female"):
        SingleScenarioDef.model_validate({
            "id": "s1",
            "interventions": [
                {"product": "Adult ART", "targets": [_ADULT_ART_TARGET], "parameters": _ADULT_ART_PARAMS},
                {"product": "Adult ART", "targets": [_ADULT_ART_TARGET], "parameters": _ADULT_ART_PARAMS},
            ],
        })


def test_combined_scenario_duplicate_adult_art_sex_raises():
    with pytest.raises(ValidationError, match=r"duplicate \(product, sex\).*Adult ART.*Male"):
        ScenarioInput.model_validate({
            "scenarios": [
                {
                    "id": "a",
                    "interventions": [
                        {"product": "Adult ART", "targets": [_ADULT_ART_TARGET_M], "parameters": _ADULT_ART_PARAMS},
                    ],
                },
                {
                    "id": "b",
                    "interventions": [
                        {"product": "Adult ART", "targets": [_ADULT_ART_TARGET_M], "parameters": _ADULT_ART_PARAMS},
                    ],
                },
                {"id": "c", "combines": ["a", "b"]},
            ]
        })
