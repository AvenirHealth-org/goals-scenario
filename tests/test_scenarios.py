import orjson
import pytest
from scenario_csv import COMBINED_CSV, MINIMAL_CSV

from avenir_goals_scenario.scenarios import generate_simulations


def test_generate_simulations_writes_output(write_csv, tmp_path):
    definition_path = write_csv(COMBINED_CSV, "scenario_definition.csv")
    simulations_path = tmp_path / "scenario_simulations.json"

    generate_simulations(definition_path, simulations_path, n_simulations=3)

    assert simulations_path.exists()
    data = orjson.loads(simulations_path.read_bytes())
    assert "scenarios" in data
    assert len(data["scenarios"]) == 3


def test_generate_simulations_raises_when_output_dir_missing(write_csv, tmp_path):
    definition_path = write_csv(MINIMAL_CSV, "scenario_definition.csv")

    with pytest.raises(FileNotFoundError, match="Simulations destination directory does not exist"):
        generate_simulations(definition_path, tmp_path / "nonexistent_dir" / "scenario_simulations.json")


def test_generate_simulations_resolves_relative_paths(write_csv, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    write_csv(MINIMAL_CSV, "scenario_definition.csv")

    generate_simulations("scenario_definition.csv", "scenario_simulations.json", n_simulations=2)

    assert (tmp_path / "scenario_simulations.json").exists()
