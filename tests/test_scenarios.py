from __future__ import annotations

import orjson
import pytest

from avenir_goals_scenario.scenarios import generate_simulations

_CSV_HEADER = "Number,Product,Efficacy,STD,Adherence,STD,Target Coverage,STD,Target Year,STD,Target Population,Sex\n"

MINIMAL_CSV = _CSV_HEADER + "1,Daily PrEP,0.95,0.03,0.80,0.20,0.10,0.05,2027,2,key_pops,both\n"

COMBINED_CSV = _CSV_HEADER + (
    "1,Daily PrEP,0.95,0.03,0.80,0.20,0.10,0.05,2027,2,key_pops,both\n"
    "2,One month pill for PrEP,0.95,0.03,0.95,0.03,0.20,0.05,2028,2,key_pops,both\n"
    "3,1+2,,,,,,,,,,\n"
)


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
