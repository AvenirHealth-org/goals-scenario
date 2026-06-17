import json
from typing import cast

import numpy as np
import pytest
from pydantic import ValidationError

from avenir_goals_scenario._scenario_generator.scenario_generator import (
    _product_to_id,
    gen_simulations,
    load_scenario_definition,
)
from avenir_goals_scenario.models import (
    CombinedScenarioDef,
    NormalDistParameters,
    PrepInterventionDef,
    ScenarioInput,
    ScenarioSimulations,
    SingleScenarioDef,
    TargetCoverage,
)

# ---------------------------------------------------------------------------
# Shared test data
# ---------------------------------------------------------------------------

PREP_PILL_INTERVENTION = {
    "product": "One month pill for PrEP",
    "targets": [
        {"risk_group": "High risk heterosexual", "sex": "Female", "target_coverage": {"mean": 0.20, "sd": 0.05}},
        {"risk_group": "Men who have sex with men", "sex": "Male", "target_coverage": {"mean": 0.15, "sd": 0.03}},
    ],
    "parameters": {
        "efficacy": {"mean": 0.95, "sd": 0.03},
        "adherence": {"mean": 0.95, "sd": 0.03},
        "target_year": {"mean": 2028, "sd": 2},
    },
}

DAILY_PREP_INTERVENTION = {
    "product": "Daily PrEP",
    "targets": [
        {"risk_group": "High risk heterosexual", "sex": "Female", "target_coverage": {"mean": 0.10, "sd": 0.05}}
    ],
    "parameters": {
        "efficacy": {"mean": 0.95, "sd": 0.03},
        "adherence": {"mean": 0.80, "sd": 0.20},
        "target_year": {"mean": 2027, "sd": 2},
    },
}

MINIMAL_INPUT = {
    "scenarios": [
        {"id": "1", "interventions": [PREP_PILL_INTERVENTION]},
        {"id": "2", "interventions": [DAILY_PREP_INTERVENTION]},
    ]
}

COMBINED_INPUT = {
    "scenarios": [
        {"id": "1", "interventions": [PREP_PILL_INTERVENTION]},
        {"id": "2", "interventions": [DAILY_PREP_INTERVENTION]},
        {"id": "3", "combines": ["1", "2"]},
    ]
}


def _seeded_rng() -> np.random.Generator:
    return np.random.default_rng(42)


# ---------------------------------------------------------------------------
# _product_to_id
# ---------------------------------------------------------------------------


def test_product_to_id_lowercases_and_slugifies():
    assert _product_to_id("Daily PrEP") == "daily_prep"


def test_product_to_id_collapses_special_chars():
    assert _product_to_id("One month pill for PrEP") == "one_month_pill_for_prep"


def test_product_to_id_strips_leading_trailing_underscores():
    assert _product_to_id("  hello world  ") == "hello_world"


# ---------------------------------------------------------------------------
# NormalDistParameters.sample
# ---------------------------------------------------------------------------


def test_sample_target_year_is_integer():
    dist = NormalDistParameters(mean=2028, sd=2, integer=True, min_value=1970)
    rng = _seeded_rng()
    value = dist.sample(rng)
    assert isinstance(value, int)


def test_sample_target_year_floor_at_1970():
    dist = NormalDistParameters(mean=1960, sd=1, integer=True, min_value=1970)
    rng = np.random.default_rng(0)
    for _ in range(50):
        assert dist.sample(rng) >= 1970


def test_sample_proportion_no_clamp():
    dist = NormalDistParameters(mean=0.0, sd=5.0)
    rng = np.random.default_rng(0)
    samples = [dist.sample(rng) for _ in range(100)]
    assert any(sample < 0.0 for sample in samples)


def test_sample_proportion_clamped_to_custom_values():
    dist = NormalDistParameters(mean=0.5, sd=5.0, min_value=1.0, max_value=2.0)
    rng = np.random.default_rng(0)
    for _ in range(100):
        v = dist.sample(rng)
        assert 1.0 <= v <= 2.0


def test_sample_returns_float_when_not_integer():
    dist = NormalDistParameters(mean=0.5, sd=0.1, min_value=0.0, max_value=1.0)
    value = dist.sample(_seeded_rng())
    assert isinstance(value, float)


# ---------------------------------------------------------------------------
# PrepInterventionDef - parameter constraints applied during parsing
# ---------------------------------------------------------------------------


def test_target_year_gets_integer_flag():
    iv = PrepInterventionDef.model_validate(PREP_PILL_INTERVENTION)
    assert iv.parameters.target_year.integer is True


def test_target_year_gets_min_value():
    iv = PrepInterventionDef.model_validate(PREP_PILL_INTERVENTION)
    assert iv.parameters.target_year.min_value == 1970.0


def test_proportion_params_get_bounds():
    iv = PrepInterventionDef.model_validate(PREP_PILL_INTERVENTION)
    assert iv.parameters.efficacy.min_value == 0.0
    assert iv.parameters.efficacy.max_value == 1.0


def test_target_coverage_in_target_gets_bounds():
    iv = PrepInterventionDef.model_validate(PREP_PILL_INTERVENTION)
    for target in iv.targets:
        assert target.target_coverage.min_value == 0.0
        assert target.target_coverage.max_value == 1.0


def test_extra_fields_rejected_on_parameter_dist():
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        NormalDistParameters(mean=0.9, sd=0.01, typo_field=True)  # ty: ignore


def test_extra_fields_rejected_on_prep_intervention_def():
    bad = {**PREP_PILL_INTERVENTION, "unexpected_key": "oops"}
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        PrepInterventionDef.model_validate(bad)


def test_extra_fields_rejected_on_scenario_input():
    bad = {**MINIMAL_INPUT, "unexpected_key": "oops"}
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        ScenarioInput.model_validate(bad)


def test_extra_fields_on_scenario_are_ignored():
    data = {
        "scenarios": [
            {
                "id": "1",
                "branch_probability": 0.5,
                "market_outcome": "Product A",
                "interventions": [PREP_PILL_INTERVENTION],
            },
        ]
    }
    definition = ScenarioInput.model_validate(data)
    assert len(definition.scenarios) == 1


# ---------------------------------------------------------------------------
# ScenarioInput validation
# ---------------------------------------------------------------------------


def test_parse_valid_single_scenarios():
    definition = ScenarioInput.model_validate(MINIMAL_INPUT)
    assert len(definition.scenarios) == 2
    assert isinstance(definition.scenarios[0], SingleScenarioDef)


def test_parse_valid_combined_scenario():
    definition = ScenarioInput.model_validate(COMBINED_INPUT)
    combined = definition.scenarios[2]
    assert isinstance(combined, CombinedScenarioDef)
    assert combined.combines == ["1", "2"]


def test_duplicate_ids_raise():
    data = {
        "scenarios": [
            {"id": "1", "interventions": [PREP_PILL_INTERVENTION]},
            {"id": "1", "interventions": [DAILY_PREP_INTERVENTION]},
        ]
    }
    with pytest.raises(ValidationError, match="unique"):
        ScenarioInput.model_validate(data)


def test_combines_unknown_id_raises():
    data = {
        "scenarios": [
            {"id": "1", "interventions": [PREP_PILL_INTERVENTION]},
            {"id": "99", "combines": ["1", "42"]},
        ]
    }
    with pytest.raises(ValidationError, match="unknown scenario id 42"):
        ScenarioInput.model_validate(data)


def test_chained_combines_raises():
    data = {
        "scenarios": [
            {"id": "1", "interventions": [PREP_PILL_INTERVENTION]},
            {"id": "2", "interventions": [DAILY_PREP_INTERVENTION]},
            {"id": "3", "combines": ["1", "2"]},
            {"id": "4", "combines": ["1", "3"]},
        ]
    }
    with pytest.raises(ValidationError, match="Chained combines are not allowed"):
        ScenarioInput.model_validate(data)


def test_combines_requires_at_least_two():
    data = {
        "scenarios": [
            {"id": "1", "interventions": [PREP_PILL_INTERVENTION]},
            {"id": "2", "combines": ["1"]},
        ]
    }
    with pytest.raises(ValidationError):
        ScenarioInput.model_validate(data)


def test_duplicate_product_population_within_single_scenario_raises():
    data = {
        "scenarios": [
            {"id": "1", "interventions": [PREP_PILL_INTERVENTION, PREP_PILL_INTERVENTION]},
        ]
    }
    with pytest.raises(ValidationError, match="duplicate"):
        ScenarioInput.model_validate(data)


def test_same_product_different_populations_within_single_scenario_ok():
    split_high_risk = {
        **PREP_PILL_INTERVENTION,
        "targets": [
            {"risk_group": "High risk heterosexual", "sex": "Female", "target_coverage": {"mean": 0.20, "sd": 0.05}}
        ],
    }
    split_medium_risk = {
        **PREP_PILL_INTERVENTION,
        "targets": [
            {"risk_group": "Medium risk heterosexual", "sex": "Female", "target_coverage": {"mean": 0.10, "sd": 0.03}}
        ],
    }
    data = {
        "scenarios": [
            {"id": "1", "interventions": [split_high_risk, split_medium_risk]},
        ]
    }
    ScenarioInput.model_validate(data)


def test_duplicate_products_across_combined_scenarios_raises():
    data = {
        "scenarios": [
            {"id": "1", "interventions": [PREP_PILL_INTERVENTION]},
            {"id": "2", "interventions": [PREP_PILL_INTERVENTION]},
            {"id": "3", "combines": ["1", "2"]},
        ]
    }
    with pytest.raises(ValidationError, match="duplicate"):
        ScenarioInput.model_validate(data)


def test_sd_must_be_non_negative():
    data = {
        "scenarios": [
            {
                "id": "1",
                "interventions": [
                    {
                        **PREP_PILL_INTERVENTION,
                        "parameters": {
                            "efficacy": {"mean": 0.9, "sd": -0.1},
                            "adherence": {"mean": 0.8, "sd": 0.1},
                            "target_year": {"mean": 2028, "sd": 2},
                        },
                    }
                ],
            }
        ]
    }
    with pytest.raises(ValidationError):
        ScenarioInput.model_validate(data)


# ---------------------------------------------------------------------------
# ScenarioInput.resolved_scenarios
# ---------------------------------------------------------------------------


def test_resolved_scenarios_count():
    definition = ScenarioInput.model_validate(COMBINED_INPUT)
    assert len(definition.resolved_scenarios()) == 3


def test_combined_resolved_has_merged_interventions():
    definition = ScenarioInput.model_validate(COMBINED_INPUT)
    resolved = definition.resolved_scenarios()
    combined = next(r for r in resolved if r.id == "3")
    assert len(combined.interventions) == 2


# ---------------------------------------------------------------------------
# gen_simulations
# ---------------------------------------------------------------------------


def test_output_has_correct_number_of_scenarios():
    definition = ScenarioInput.model_validate(COMBINED_INPUT)
    output = gen_simulations(definition, n_simulations=5, rng=_seeded_rng())
    assert len(output.scenarios) == 3


def test_output_has_correct_number_of_simulations():
    definition = ScenarioInput.model_validate(MINIMAL_INPUT)
    output = gen_simulations(definition, n_simulations=7, rng=_seeded_rng())
    for scenario in output.scenarios:
        assert len(scenario.simulations) == 7


def test_single_scenario_intervention_id():
    definition = ScenarioInput.model_validate(MINIMAL_INPUT)
    output = gen_simulations(definition, n_simulations=1, rng=_seeded_rng())
    assert output.scenarios[0].interventions[0].id == "one_month_pill_for_prep"


def test_intervention_out_has_id_and_product():
    definition = ScenarioInput.model_validate(MINIMAL_INPUT)
    output = gen_simulations(definition, n_simulations=1, rng=_seeded_rng())
    iv = output.scenarios[0].interventions[0]
    assert iv.id == "one_month_pill_for_prep"
    assert iv.product == "One month pill for PrEP"


def test_combined_scenario_merges_interventions():
    definition = ScenarioInput.model_validate(COMBINED_INPUT)
    output = gen_simulations(definition, n_simulations=1, rng=_seeded_rng())
    combined = output.scenarios[2]
    ids = {iv.id for iv in combined.interventions}
    assert ids == {"one_month_pill_for_prep", "daily_prep"}


def test_combined_scenario_simulation_has_both_keys():
    definition = ScenarioInput.model_validate(COMBINED_INPUT)
    output = gen_simulations(definition, n_simulations=3, rng=_seeded_rng())
    for sim in output.scenarios[2].simulations:
        assert "one_month_pill_for_prep" in sim
        assert "daily_prep" in sim


def test_simulation_parameters_present():
    definition = ScenarioInput.model_validate(MINIMAL_INPUT)
    output = gen_simulations(definition, n_simulations=1, rng=_seeded_rng())
    params = output.scenarios[0].simulations[0]["one_month_pill_for_prep"].root
    # 2 targets → target_coverage_0 and target_coverage_1
    assert set(params.keys()) == {"efficacy", "adherence", "target_year", "target_coverages"}


def test_per_target_coverages_are_sampled_independently():
    definition = ScenarioInput.model_validate(MINIMAL_INPUT)
    output = gen_simulations(definition, n_simulations=50, rng=np.random.default_rng(0))
    cov_0s = [
        cast(list[TargetCoverage], sim["one_month_pill_for_prep"].root["target_coverages"])[0].coverage
        for sim in output.scenarios[0].simulations
    ]
    cov_1s = [
        cast(list[TargetCoverage], sim["one_month_pill_for_prep"].root["target_coverages"])[1].coverage
        for sim in output.scenarios[0].simulations
    ]
    # Different distributions (mean 0.20 vs 0.15) should produce different mean values
    assert abs(float(np.mean(cov_0s)) - float(np.mean(cov_1s))) > 0.01


def test_target_year_is_int_in_output():
    definition = ScenarioInput.model_validate(MINIMAL_INPUT)
    output = gen_simulations(definition, n_simulations=1, rng=_seeded_rng())
    year = output.scenarios[0].simulations[0]["one_month_pill_for_prep"].root["target_year"]
    assert isinstance(year, int)


def test_target_year_value_is_near_mean():
    # Regression: target_year was clamped to 1.0 due to `is` instead of `==` in constraint logic.
    definition = ScenarioInput.model_validate(MINIMAL_INPUT)
    output = gen_simulations(definition, n_simulations=50, rng=np.random.default_rng(0))
    years = [sim["one_month_pill_for_prep"].root["target_year"] for sim in output.scenarios[0].simulations]
    assert all(2020 <= y <= 2040 for y in years), f"Unexpected target_year values: {years}"  # ty: ignore[unsupported-operator]


def test_output_is_scenario_output_instance():
    definition = ScenarioInput.model_validate(MINIMAL_INPUT)
    output = gen_simulations(definition, n_simulations=1, rng=_seeded_rng())
    assert isinstance(output, ScenarioSimulations)


def test_reproducible_with_same_seed():
    definition = ScenarioInput.model_validate(MINIMAL_INPUT)
    out1 = gen_simulations(definition, n_simulations=10, rng=np.random.default_rng(0))
    out2 = gen_simulations(definition, n_simulations=10, rng=np.random.default_rng(0))
    assert out1.model_dump() == out2.model_dump()


def test_gen_simulations_without_rng_creates_default_rng():
    definition = ScenarioInput.model_validate(MINIMAL_INPUT)
    output = gen_simulations(definition, n_simulations=1)
    assert isinstance(output, ScenarioSimulations)


def test_ahd_treatment_has_no_target_coverages_in_draw():
    """AHD treatment has no targets; its draw should have no target_coverages key."""
    data = {
        "scenarios": [
            {
                "id": "1",
                "interventions": [
                    {
                        "product": "AHD treatment",
                        "parameters": {
                            "target_year": {"mean": 2028, "sd": 2},
                            "target_coverage": {"mean": 0.5, "sd": 0.1},
                            "reduction_in_mortality": {"mean": 0.3, "sd": 0.05},
                        },
                    }
                ],
            }
        ]
    }
    definition = ScenarioInput.model_validate(data)
    output = gen_simulations(definition, n_simulations=1, rng=_seeded_rng())
    draw = output.scenarios[0].simulations[0]["ahd_treatment"].root
    assert "target_coverages" not in draw


def test_categorical_params_passed_through_unchanged():
    """Vaccine categorical params (vaccine_action_type, targeting) survive in the simulation draw."""
    data = {
        "scenarios": [
            {
                "id": "1",
                "interventions": [
                    {
                        "product": "Vaccine",
                        "targets": [
                            {
                                "risk_group": "High risk heterosexual",
                                "sex": "Female",
                                "target_coverage": {"mean": 0.5, "sd": 0.1},
                            }
                        ],
                        "parameters": {
                            "target_year": {"mean": 2030, "sd": 2},
                            "reduction_in_susceptibility": {"mean": 0.6, "sd": 0.05},
                            "reduction_in_infectiousness": {"mean": 0.4, "sd": 0.05},
                            "increase_in_progression_time_to_aids": {"mean": 0.2, "sd": 0.02},
                            "vaccine_duration_years": {"mean": 5, "sd": 1},
                            "vaccine_action_type": "Take",
                            "targeting": "Vaccinate only HIV-negative individuals",
                        },
                    }
                ],
            }
        ]
    }
    definition = ScenarioInput.model_validate(data)
    output = gen_simulations(definition, n_simulations=1, rng=_seeded_rng())
    params = output.scenarios[0].simulations[0]["vaccine"].root
    assert params["vaccine_action_type"] == "Take"
    assert params["targeting"] == "Vaccinate only HIV-negative individuals"


# ---------------------------------------------------------------------------
# load_scenario_definition
# ---------------------------------------------------------------------------


def test_load_valid_json_file(tmp_path):
    path = tmp_path / "scenarios.json"
    path.write_text(
        json.dumps({
            "scenarios": [
                {"id": "1", "interventions": [PREP_PILL_INTERVENTION]},
                {"id": "2", "interventions": [DAILY_PREP_INTERVENTION]},
            ]
        })
    )
    definition = load_scenario_definition(path)
    assert len(definition.scenarios) == 2
    assert definition.scenarios[0].id == "1"


def test_load_json_with_pjnz_names(tmp_path):
    path = tmp_path / "scenarios.json"
    path.write_text(
        json.dumps({
            "scenarios": [
                {"id": "1", "pjnz_names": ["Zimbabwe", "Botswana"], "interventions": [PREP_PILL_INTERVENTION]},
            ]
        })
    )
    definition = load_scenario_definition(path)
    assert definition.scenarios[0].pjnz_names == ["Zimbabwe", "Botswana"]


def test_pjnz_alias_accepted_and_preserved_through_draw(tmp_path):
    path = tmp_path / "scenarios.json"
    path.write_text(
        json.dumps({
            "scenarios": [
                {"id": "0", "pjnz": ["Zimbabwe", "Botswana"], "interventions": []},
            ]
        })
    )
    definition = load_scenario_definition(path)
    assert definition.scenarios[0].pjnz_names == ["Zimbabwe", "Botswana"]

    simulations = gen_simulations(definition, n_simulations=1)
    assert simulations.scenarios[0].pjnz_names == ["Zimbabwe", "Botswana"]


def test_load_json_combined_scenario(tmp_path):
    path = tmp_path / "scenarios.json"
    path.write_text(
        json.dumps({
            "scenarios": [
                {"id": "1", "interventions": [PREP_PILL_INTERVENTION]},
                {"id": "2", "interventions": [DAILY_PREP_INTERVENTION]},
                {"id": "3", "combines": ["1", "2"]},
            ]
        })
    )
    definition = load_scenario_definition(path)
    assert len(definition.scenarios) == 3
    assert isinstance(definition.scenarios[2], CombinedScenarioDef)


def test_load_json_extra_fields_ignored(tmp_path):
    path = tmp_path / "scenarios.json"
    path.write_text(
        json.dumps({
            "scenarios": [
                {
                    "id": "1",
                    "branch_probability": 0.25,
                    "market_outcome": "Product A",
                    "interventions": [PREP_PILL_INTERVENTION],
                },
            ]
        })
    )
    definition = load_scenario_definition(path)
    assert len(definition.scenarios) == 1


def test_load_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError, match="not found"):
        load_scenario_definition(tmp_path / "missing.json")


def test_load_unsupported_extension_raises(tmp_path):
    path = tmp_path / "input.xlsx"
    path.write_text("data")
    with pytest.raises(ValueError, match=r"\.json"):
        load_scenario_definition(path)


def test_load_invalid_json_raises(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text(
        '{"scenarios": [{"id": "1", "interventions": [{"product": "Unknown product", "targets": [], "parameters": {}}]}]}'
    )
    with pytest.raises(ValueError, match="Invalid scenario definition"):
        load_scenario_definition(path)


def test_load_proportion_params_have_0_1_bounds(tmp_path):
    path = tmp_path / "scenarios.json"
    path.write_text(json.dumps({"scenarios": [{"id": "1", "interventions": [PREP_PILL_INTERVENTION]}]}))
    definition = load_scenario_definition(path)
    single = cast(SingleScenarioDef, definition.scenarios[0])
    iv = cast(PrepInterventionDef, single.interventions[0])
    for param_name in ("efficacy", "adherence"):
        dist = getattr(iv.parameters, param_name)
        assert dist.min_value == 0.0, f"{param_name}.min_value"
        assert dist.max_value == 1.0, f"{param_name}.max_value"
    for target in iv.targets:
        assert target.target_coverage.min_value == 0.0
        assert target.target_coverage.max_value == 1.0
