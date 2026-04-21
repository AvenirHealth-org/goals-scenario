import orjson
import pytest
from scenario_csv import COMBINED_CSV, MINIMAL_CSV

from avenir_goals_scenario.models import ScenarioSimulations
from avenir_goals_scenario.scenarios import draw_simulations, read_simulations, write_simulations

# --- draw_simulations ---


def test_draw_simulations_returns_scenario_simulations(write_csv, tmp_path):
    definition_path = write_csv(COMBINED_CSV, "scenario_definition.csv")

    result = draw_simulations(definition_path, n_simulations=3)

    assert isinstance(result, ScenarioSimulations)
    assert len(result.scenarios[0].simulations) == 3


def test_draw_simulations_seed_is_deterministic(write_csv):
    definition_path = write_csv(MINIMAL_CSV, "scenario_definition.csv")

    a = draw_simulations(definition_path, n_simulations=5, seed=42)
    b = draw_simulations(definition_path, n_simulations=5, seed=42)

    assert a.model_dump_json() == b.model_dump_json()


def test_draw_simulations_different_seeds_differ(write_csv):
    definition_path = write_csv(MINIMAL_CSV, "scenario_definition.csv")

    a = draw_simulations(definition_path, n_simulations=5, seed=1)
    b = draw_simulations(definition_path, n_simulations=5, seed=2)

    assert a.model_dump_json() != b.model_dump_json()


def test_draw_simulations_base_year_clamps_target_year(write_csv):
    definition_path = write_csv(MINIMAL_CSV, "scenario_definition.csv")

    # Use a very late base_year so that all target_year draws must be >= it.
    base_year = 2050
    result = draw_simulations(definition_path, n_simulations=50, seed=0, base_year=base_year)

    for scenario in result.scenarios:
        for sim in scenario.simulations:
            for iv_sim in sim.values():
                assert iv_sim.root["target_year"] >= base_year


def test_draw_simulations_no_base_year_uses_default_floor(write_csv):
    definition_path = write_csv(MINIMAL_CSV, "scenario_definition.csv")

    # Without base_year the existing _YEAR_MIN (1970) floor should still apply.
    result = draw_simulations(definition_path, n_simulations=50, seed=0, base_year=None)

    for scenario in result.scenarios:
        for sim in scenario.simulations:
            for iv_sim in sim.values():
                assert iv_sim.root["target_year"] >= 1970


# --- write_simulations ---


def test_write_simulations_creates_file(write_csv, tmp_path):
    definition_path = write_csv(MINIMAL_CSV, "scenario_definition.csv")
    simulations = draw_simulations(definition_path, n_simulations=2)
    dest = tmp_path / "out.json"

    write_simulations(simulations, dest)

    assert dest.exists()
    data = orjson.loads(dest.read_bytes())
    assert "scenarios" in data


def test_write_simulations_raises_when_parent_missing(write_csv, tmp_path):
    definition_path = write_csv(MINIMAL_CSV, "scenario_definition.csv")
    simulations = draw_simulations(definition_path, n_simulations=1)

    with pytest.raises(FileNotFoundError, match="Destination directory does not exist"):
        write_simulations(simulations, tmp_path / "nonexistent" / "out.json")


def test_write_simulations_resolves_relative_paths(write_csv, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    definition_path = write_csv(MINIMAL_CSV, "scenario_definition.csv")
    simulations = draw_simulations(definition_path, n_simulations=2)

    write_simulations(simulations, "out.json")

    assert (tmp_path / "out.json").exists()


# --- read_simulations ---


def test_read_simulations_round_trips(write_csv, tmp_path):
    definition_path = write_csv(MINIMAL_CSV, "scenario_definition.csv")
    simulations = draw_simulations(definition_path, n_simulations=3, seed=7)
    dest = tmp_path / "out.json"
    write_simulations(simulations, dest)

    loaded = read_simulations(dest)

    assert loaded.model_dump_json() == simulations.model_dump_json()


def test_read_simulations_raises_when_file_missing(tmp_path):
    with pytest.raises(FileNotFoundError, match="does not exist"):
        read_simulations(tmp_path / "nonexistent.json")
