import orjson
import pytest

from avenir_goals_scenario.models import ScenarioSimulations
from avenir_goals_scenario.scenarios import draw_simulations, read_simulations, write_simulations

_PREP_PILL = {
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

_DAILY_PREP = {
    "product": "Daily PrEP",
    "targets": [{"population": "High risk heterosexual", "sex": "Female"}],
    "parameters": {
        "efficacy": {"mean": 0.95, "sd": 0.03},
        "adherence": {"mean": 0.80, "sd": 0.20},
        "target_coverage": {"mean": 0.10, "sd": 0.05},
        "target_year": {"mean": 2027, "sd": 2},
    },
}

MINIMAL_JSON = {
    "scenarios": [
        {"id": "1", "interventions": [_PREP_PILL]},
    ]
}

COMBINED_JSON = {
    "scenarios": [
        {"id": "1", "interventions": [_PREP_PILL]},
        {"id": "2", "interventions": [_DAILY_PREP]},
        {"id": "3", "combines": ["1", "2"]},
    ]
}

# --- draw_simulations ---


def test_draw_simulations_returns_scenario_simulations(write_json, tmp_path):
    definition_path = write_json(COMBINED_JSON, "scenario_definition.json")

    result = draw_simulations(definition_path, 2000, n_simulations=3)

    assert isinstance(result, ScenarioSimulations)
    assert len(result.scenarios[0].simulations) == 3


def test_draw_simulations_seed_is_deterministic(write_json):
    definition_path = write_json(MINIMAL_JSON, "scenario_definition.json")

    a = draw_simulations(definition_path, 2000, n_simulations=5, seed=42)
    b = draw_simulations(definition_path, 2000, n_simulations=5, seed=42)

    assert a.model_dump_json() == b.model_dump_json()


def test_draw_simulations_different_seeds_differ(write_json):
    definition_path = write_json(MINIMAL_JSON, "scenario_definition.json")

    a = draw_simulations(definition_path, 2000, n_simulations=5, seed=1)
    b = draw_simulations(definition_path, 2000, n_simulations=5, seed=2)

    assert a.model_dump_json() != b.model_dump_json()


def test_draw_simulations_base_year_clamps_target_year(write_json):
    definition_path = write_json(MINIMAL_JSON, "scenario_definition.json")

    base_year = 2050
    result = draw_simulations(definition_path, base_year=base_year, n_simulations=50, seed=0)

    for scenario in result.scenarios:
        for sim in scenario.simulations:
            for iv_sim in sim.values():
                assert iv_sim.root["target_year"] >= base_year  # ty: ignore[unsupported-operator]


# --- write_simulations ---


def test_write_simulations_creates_file(write_json, tmp_path):
    definition_path = write_json(MINIMAL_JSON, "scenario_definition.json")
    simulations = draw_simulations(definition_path, 2000, n_simulations=2)
    dest = tmp_path / "out.json"

    write_simulations(simulations, dest)

    assert dest.exists()
    data = orjson.loads(dest.read_bytes())
    assert "scenarios" in data


def test_write_simulations_raises_when_parent_missing(write_json, tmp_path):
    definition_path = write_json(MINIMAL_JSON, "scenario_definition.json")
    simulations = draw_simulations(definition_path, 2000, n_simulations=1)

    with pytest.raises(FileNotFoundError, match="Destination directory does not exist"):
        write_simulations(simulations, tmp_path / "nonexistent" / "out.json")


def test_write_simulations_resolves_relative_paths(write_json, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    definition_path = write_json(MINIMAL_JSON, "scenario_definition.json")
    simulations = draw_simulations(definition_path, 2000, n_simulations=2)

    write_simulations(simulations, "out.json")

    assert (tmp_path / "out.json").exists()


# --- read_simulations ---


def test_read_simulations_round_trips(write_json, tmp_path):
    definition_path = write_json(MINIMAL_JSON, "scenario_definition.json")
    simulations = draw_simulations(definition_path, 2000, n_simulations=3, seed=7)
    dest = tmp_path / "out.json"
    write_simulations(simulations, dest)

    loaded = read_simulations(dest)

    assert loaded.model_dump_json() == simulations.model_dump_json()


def test_read_simulations_raises_when_file_missing(tmp_path):
    with pytest.raises(FileNotFoundError, match="does not exist"):
        read_simulations(tmp_path / "nonexistent.json")
