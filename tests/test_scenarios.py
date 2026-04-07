from __future__ import annotations

import orjson
import pytest

from avenir_goals_scenario.scenarios import generate_simulations

MINIMAL_INPUT = {
    "scenario_definitions": [
        {
            "id": 1,
            "interventions": [
                {
                    "product": "Daily PrEP",
                    "target_population": "key_pops",
                    "sex": "both",
                    "parameters": {
                        "efficacy": {"mean": 0.95, "sd": 0.03},
                        "target_year": {"mean": 2027, "sd": 2},
                    },
                }
            ],
        }
    ]
}

COMBINED_INPUT = {
    "scenario_definitions": [
        {
            "id": 1,
            "interventions": [
                {
                    "product": "Daily PrEP",
                    "target_population": "key_pops",
                    "sex": "both",
                    "parameters": {
                        "efficacy": {"mean": 0.95, "sd": 0.03},
                        "target_year": {"mean": 2027, "sd": 2},
                    },
                }
            ],
        },
        {
            "id": 2,
            "interventions": [
                {
                    "product": "One month pill for PrEP",
                    "target_population": ["PWID", "MSM"],
                    "sex": "both",
                    "parameters": {
                        "efficacy": {"mean": 0.95, "sd": 0.03},
                        "target_year": {"mean": 2028, "sd": 2},
                    },
                }
            ],
        },
        {"id": 3, "combines": [1, 2]},
    ]
}


def test_generate_simulations_writes_output(write_json, tmp_path):
    definition_path = write_json(COMBINED_INPUT, "scenario_definition.json")
    simulations_path = tmp_path / "scenario_simulations.json"

    generate_simulations(definition_path, simulations_path, n_simulations=3)

    assert simulations_path.exists()
    data = orjson.loads(simulations_path.read_bytes())
    assert "scenarios" in data
    assert len(data["scenarios"]) == 3


def test_generate_simulations_raises_when_output_dir_missing(write_json, tmp_path):
    definition_path = write_json(MINIMAL_INPUT, "scenario_definition.json")

    with pytest.raises(FileNotFoundError, match="Simulations destination directory does not exist"):
        generate_simulations(definition_path, tmp_path / "nonexistent_dir" / "scenario_simulations.json")


def test_generate_simulations_resolves_relative_paths(write_json, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    write_json(MINIMAL_INPUT, "scenario_definition.json")

    generate_simulations("scenario_definition.json", "scenario_simulations.json", n_simulations=2)

    assert (tmp_path / "scenario_simulations.json").exists()
