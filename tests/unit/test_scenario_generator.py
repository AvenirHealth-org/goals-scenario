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
    InterventionDef,
    NormalDistParameters,
    ScenarioInput,
    ScenarioSimulations,
    SingleScenarioDef,
)

# ---------------------------------------------------------------------------
# Shared test data
# ---------------------------------------------------------------------------

PREP_PILL_INTERVENTION = {
    "product": "One month pill for PrEP",
    "targets": [
        {"population": "High risk heterosexual", "sex": "Female"},
        {"population": "Men who have sex with men", "sex": "Male"},
    ],
    "parameters": {
        "efficacy": {"mean": 0.95, "sd": 0.03},
        "adherence": {"mean": 0.95, "sd": 0.03},
        "target_coverage": {"mean": 0.20, "sd": 0.05},
        "target_year": {"mean": 2028, "sd": 2},
    },
}

DAILY_PREP_INTERVENTION = {
    "product": "Daily PrEP",
    "targets": [{"population": "High risk heterosexual", "sex": "Female"}],
    "parameters": {
        "efficacy": {"mean": 0.95, "sd": 0.03},
        "adherence": {"mean": 0.80, "sd": 0.20},
        "target_coverage": {"mean": 0.10, "sd": 0.05},
        "target_year": {"mean": 2027, "sd": 2},
    },
}

MINIMAL_INPUT = {
    "scenario_definitions": [
        {"id": 1, "interventions": [PREP_PILL_INTERVENTION]},
        {"id": 2, "interventions": [DAILY_PREP_INTERVENTION]},
    ]
}

COMBINED_INPUT = {
    "scenario_definitions": [
        {"id": 1, "interventions": [PREP_PILL_INTERVENTION]},
        {"id": 2, "interventions": [DAILY_PREP_INTERVENTION]},
        {"id": 3, "combines": [1, 2]},
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
# InterventionDef — parameter constraints applied during parsing
# ---------------------------------------------------------------------------


def test_target_year_gets_integer_flag():
    iv = InterventionDef.model_validate(PREP_PILL_INTERVENTION)
    assert iv.parameters["target_year"].integer is True


def test_target_year_gets_min_value():
    iv = InterventionDef.model_validate(PREP_PILL_INTERVENTION)
    assert iv.parameters["target_year"].min_value == 1970.0


def test_proportion_params_get_bounds():
    iv = InterventionDef.model_validate(PREP_PILL_INTERVENTION)
    efficacy = iv.parameters["efficacy"]
    assert efficacy.min_value == 0.0
    assert efficacy.max_value == 1.0


def test_extra_fields_rejected_on_parameter_dist():
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        NormalDistParameters(mean=0.9, sd=0.01, typo_field=True)  # ty: ignore


def test_extra_fields_rejected_on_intervention_def():
    bad = {**PREP_PILL_INTERVENTION, "unexpected_key": "oops"}
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        InterventionDef.model_validate(bad)


def test_extra_fields_rejected_on_scenario_input():
    bad = {**MINIMAL_INPUT, "unexpected_key": "oops"}
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        ScenarioInput.model_validate(bad)


# ---------------------------------------------------------------------------
# ScenarioInput validation
# ---------------------------------------------------------------------------


def test_parse_valid_single_scenarios():
    definition = ScenarioInput.model_validate(MINIMAL_INPUT)
    assert len(definition.scenario_definitions) == 2
    assert isinstance(definition.scenario_definitions[0], SingleScenarioDef)


def test_parse_valid_combined_scenario():
    definition = ScenarioInput.model_validate(COMBINED_INPUT)
    combined = definition.scenario_definitions[2]
    assert isinstance(combined, CombinedScenarioDef)
    assert combined.combines == [1, 2]


def test_duplicate_ids_raise():
    data = {
        "scenario_definitions": [
            {"id": 1, "interventions": [PREP_PILL_INTERVENTION]},
            {"id": 1, "interventions": [DAILY_PREP_INTERVENTION]},
        ]
    }
    with pytest.raises(ValidationError, match="unique"):
        ScenarioInput.model_validate(data)


def test_combines_unknown_id_raises():
    data = {
        "scenario_definitions": [
            {"id": 1, "interventions": [PREP_PILL_INTERVENTION]},
            {"id": 99, "combines": [1, 42]},
        ]
    }
    with pytest.raises(ValidationError, match="unknown scenario id 42"):
        ScenarioInput.model_validate(data)


def test_chained_combines_raises():
    data = {
        "scenario_definitions": [
            {"id": 1, "interventions": [PREP_PILL_INTERVENTION]},
            {"id": 2, "interventions": [DAILY_PREP_INTERVENTION]},
            {"id": 3, "combines": [1, 2]},
            {"id": 4, "combines": [1, 3]},
        ]
    }
    with pytest.raises(ValidationError, match="Chained combines are not allowed"):
        ScenarioInput.model_validate(data)


def test_combines_requires_at_least_two():
    data = {
        "scenario_definitions": [
            {"id": 1, "interventions": [PREP_PILL_INTERVENTION]},
            {"id": 2, "combines": [1]},
        ]
    }
    with pytest.raises(ValidationError):
        ScenarioInput.model_validate(data)


def test_duplicate_products_within_single_scenario_raises():
    data = {
        "scenario_definitions": [
            {"id": 1, "interventions": [PREP_PILL_INTERVENTION, PREP_PILL_INTERVENTION]},
        ]
    }
    with pytest.raises(ValidationError, match="unique product names"):
        ScenarioInput.model_validate(data)


def test_duplicate_products_across_combined_scenarios_raises():
    data = {
        "scenario_definitions": [
            {"id": 1, "interventions": [PREP_PILL_INTERVENTION]},
            {"id": 2, "interventions": [PREP_PILL_INTERVENTION]},
            {"id": 3, "combines": [1, 2]},
        ]
    }
    with pytest.raises(ValidationError, match="share product"):
        ScenarioInput.model_validate(data)


def test_sd_must_be_non_negative():
    data = {
        "scenario_definitions": [
            {
                "id": 1,
                "interventions": [{**PREP_PILL_INTERVENTION, "parameters": {"efficacy": {"mean": 0.9, "sd": -0.1}}}],
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
    combined = next(r for r in resolved if r.id == 3)
    assert len(combined.interventions) == 2


# ---------------------------------------------------------------------------
# generate_simulations
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


def test_intervention_out_has_targets():
    definition = ScenarioInput.model_validate(MINIMAL_INPUT)
    output = gen_simulations(definition, n_simulations=1, rng=_seeded_rng())
    targets = output.scenarios[0].interventions[0].targets
    assert len(targets) == 2
    assert targets[0].population == "High risk heterosexual"
    assert targets[0].sex == "Female"
    assert targets[1].population == "Men who have sex with men"
    assert targets[1].sex == "Male"


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
    assert set(params.keys()) == {"efficacy", "adherence", "target_coverage", "target_year"}


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
    assert all(2020 <= y <= 2040 for y in years), f"Unexpected target_year values: {years}"


def test_output_is_scenario_output_instance():
    definition = ScenarioInput.model_validate(MINIMAL_INPUT)
    output = gen_simulations(definition, n_simulations=1, rng=_seeded_rng())
    assert isinstance(output, ScenarioSimulations)


def test_reproducible_with_same_seed():
    definition = ScenarioInput.model_validate(MINIMAL_INPUT)
    out1 = gen_simulations(definition, n_simulations=10, rng=np.random.default_rng(0))
    out2 = gen_simulations(definition, n_simulations=10, rng=np.random.default_rng(0))
    assert out1.model_dump() == out2.model_dump()


# ---------------------------------------------------------------------------
# load_scenario_definition
# ---------------------------------------------------------------------------

from scenario_csv import COMBINED_CSV, CSV_HEADER  # noqa: E402


def test_load_valid_file(write_csv):
    path = write_csv(COMBINED_CSV, "scenario_definition.csv")
    definition = load_scenario_definition(path)
    assert len(definition.scenario_definitions) == 3


def test_load_multi_row_scenario_collects_targets(write_csv):
    path = write_csv(COMBINED_CSV, "scenario_definition.csv")
    definition = load_scenario_definition(path)
    single = next(s for s in definition.scenario_definitions if isinstance(s, SingleScenarioDef) and s.id == 1)
    targets = single.interventions[0].targets
    assert len(targets) == 2
    assert targets[0].population == "High risk heterosexual"
    assert targets[1].population == "Men who have sex with men"


def test_load_inconsistent_rows_raises(write_csv):
    content = CSV_HEADER + (
        "1,Daily PrEP,0.95,0.03,0.80,0.20,0.10,0.05,2027,2,High risk heterosexual,Female\n"
        "1,Daily PrEP,0.99,0.03,0.80,0.20,0.10,0.05,2027,2,Men who have sex with men,Male\n"  # efficacy mean differs
    )
    path = write_csv(content)
    with pytest.raises(ValueError, match="efficacy mean"):
        load_scenario_definition(path)


def test_load_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError, match="not found"):
        load_scenario_definition(tmp_path / "missing.csv")


def test_load_non_csv_extension_raises(tmp_path):
    path = tmp_path / "input.json"
    path.write_text("{}")
    with pytest.raises(ValueError, match=r"\.csv"):
        load_scenario_definition(path)


def test_load_invalid_csv_raises(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text(CSV_HEADER + "1,Daily PrEP,not-a-number,0.03,0.80,0.20,0.10,0.05,2027,2,key_pops,both\n")
    with pytest.raises(ValueError, match="Invalid scenario definition"):
        load_scenario_definition(path)


def test_load_non_integer_number_raises(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text(CSV_HEADER + "1.5,Daily PrEP,0.95,0.03,0.80,0.20,0.10,0.05,2027,2,key_pops,both\n")
    with pytest.raises(ValueError, match="'Number' must be an integer"):
        load_scenario_definition(path)


def test_load_invalid_schema_raises(write_csv):
    # Combined row references a non-existent single scenario ID.
    content = CSV_HEADER + "1,Daily PrEP,0.95,0.03,0.80,0.20,0.10,0.05,2027,2,key_pops,both\n99,1+42,,,,,,,,,,\n"
    path = write_csv(content)
    with pytest.raises(ValueError, match="Invalid scenario definition"):
        load_scenario_definition(path)


# ---------------------------------------------------------------------------
# Column validation
# ---------------------------------------------------------------------------


def test_load_unknown_column_raises(write_csv):
    bad_header = CSV_HEADER.rstrip("\n") + ",Extra column\n"
    content = bad_header + "1,Daily PrEP,0.95,0.03,0.80,0.20,0.10,0.05,2027,2,key_pops,both,oops\n"
    path = write_csv(content)
    with pytest.raises(ValueError, match="Unknown column"):
        load_scenario_definition(path)


def test_load_unknown_column_error_includes_expected(write_csv):
    bad_header = CSV_HEADER.rstrip("\n") + ",Typo col\n"
    content = bad_header + "1,Daily PrEP,0.95,0.03,0.80,0.20,0.10,0.05,2027,2,key_pops,both,x\n"
    path = write_csv(content)
    with pytest.raises(ValueError, match="Expected columns"):
        load_scenario_definition(path)


def test_load_missing_column_raises(write_csv):
    bad_header = CSV_HEADER.replace(",Sex\n", "\n")
    content = bad_header + "1,Daily PrEP,0.95,0.03,0.80,0.20,0.10,0.05,2027,2,key_pops\n"
    path = write_csv(content)
    with pytest.raises(ValueError, match="Missing column"):
        load_scenario_definition(path)


def test_load_missing_column_error_names_missing(write_csv):
    bad_header = CSV_HEADER.replace(",Sex\n", "\n")
    content = bad_header + "1,Daily PrEP,0.95,0.03,0.80,0.20,0.10,0.05,2027,2,key_pops\n"
    path = write_csv(content)
    with pytest.raises(ValueError, match="sex"):
        load_scenario_definition(path)
