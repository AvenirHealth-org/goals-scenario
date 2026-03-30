from pathlib import Path
from unittest.mock import patch

import orjson
import pytest
from pydantic import ValidationError
from typer.testing import CliRunner

from avenir_goals_scenario.cli import RunConfig, _load_config, app

runner = CliRunner()

# A valid config dict matching the expected JSON shape.
VALID_CONFIG: dict[str, str | list[str]] = {
    "Goals_path": "/pjnz",
    "Scenario_path": "/scenarios",
    "Scenario_file_name": "scenarios.csv",
    "Output_path": "/output",
    "Output_file_name": "results.parquet",
    "Base_year": "2025",
    "Output_indicators": ["PLHIV", "New Infections"],
}


# --- _load_config ---


def test_load_config_parses_valid_json(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(VALID_CONFIG))

    result = _load_config(config_file)

    assert result.goals_path == "/pjnz"
    assert result.scenario_path == "/scenarios"
    assert result.scenario_file_name == "scenarios.csv"
    assert result.output_path == "/output"
    assert result.output_file_name == "results.parquet"
    assert result.base_year == "2025"
    assert result.output_indicators == ["PLHIV", "New Infections"]


def test_load_config_accepts_uppercase_keys(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(VALID_CONFIG))

    assert isinstance(_load_config(config_file), RunConfig)


def test_load_config_accepts_lowercase_keys(tmp_path):
    lowercase = {k.lower(): v for k, v in VALID_CONFIG.items()}
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(lowercase))

    assert _load_config(config_file).goals_path == "/pjnz"


def test_load_config_raises_on_missing_fields(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps({"Goals_path": "/pjnz"}))

    with pytest.raises(ValidationError):
        _load_config(config_file)


# --- CLI: --version / -v ---


def test_cli_version_long():
    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert "goals-scenario" in result.output


def test_cli_version_short():
    result = runner.invoke(app, ["-v"])

    assert result.exit_code == 0
    assert "goals-scenario" in result.output


# --- CLI: -h / --help ---


def test_cli_help_long():
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0


def test_cli_help_short():
    result = runner.invoke(app, ["-h"])

    assert result.exit_code == 0


# --- CLI: scenarios command ---


def test_cli_scenarios_requires_dest_path():
    result = runner.invoke(app, ["scenarios"])

    assert result.exit_code != 0


def test_cli_scenarios_calls_generate_scenarios(tmp_path):
    dest = tmp_path / "out.csv"

    with patch("avenir_goals_scenario.cli.generate_scenarios") as mock_gen:
        result = runner.invoke(app, ["scenarios", "--dest-path", str(dest)])

    assert result.exit_code == 0
    mock_gen.assert_called_once_with(dest)


def test_cli_scenarios_handles_errors():
    with patch("avenir_goals_scenario.cli.generate_scenarios", side_effect=RuntimeError("something went wrong")):
        result = runner.invoke(app, ["scenarios", "--dest-path", "/x/out.csv"])

    assert result.exit_code == 1
    assert "Error:" in result.output


def test_cli_scenarios_handles_error_without_message():
    with patch("avenir_goals_scenario.cli.generate_scenarios", side_effect=NotImplementedError()):
        result = runner.invoke(app, ["scenarios", "--dest-path", "/x/out.csv"])

    assert result.exit_code == 1
    assert "NotImplementedError" in result.output


# --- CLI: run command ---


def test_cli_run_requires_config_path():
    result = runner.invoke(app, ["run"])

    assert result.exit_code != 0


def test_cli_run_calls_run_scenario_analysis(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(VALID_CONFIG))

    with patch("avenir_goals_scenario.cli.run_scenario_analysis") as mock_run:
        result = runner.invoke(app, ["run", "--config-path", str(config_file)])

    assert result.exit_code == 0
    mock_run.assert_called_once_with(
        pjnz_dir=Path("/pjnz"),
        scenarios_path=Path("/scenarios") / "scenarios.csv",
        output_path=Path("/output") / "results.parquet",
    )


def test_cli_run_errors_on_non_json_file(tmp_path):
    config_file = tmp_path / "config.csv"
    config_file.write_text("a,b,c")

    result = runner.invoke(app, ["run", "--config-path", str(config_file)])

    assert result.exit_code == 1
    assert ".json" in result.output


def test_cli_run_errors_on_invalid_json(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text("this is not json {{{")

    result = runner.invoke(app, ["run", "--config-path", str(config_file)])

    assert result.exit_code == 1
    assert "invalid JSON" in result.output


def test_cli_run_errors_when_config_file_missing(tmp_path):
    result = runner.invoke(app, ["run", "--config-path", str(tmp_path / "nonexistent.json")])

    assert result.exit_code == 1
    assert "Error:" in result.output


def test_cli_run_errors_on_invalid_config(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps({"Goals_path": "/pjnz"}))

    result = runner.invoke(app, ["run", "--config-path", str(config_file)])

    assert result.exit_code == 1
    assert "Error:" in result.output


def test_cli_run_handles_errors(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(VALID_CONFIG))

    with patch("avenir_goals_scenario.cli.run_scenario_analysis", side_effect=RuntimeError("something went wrong")):
        result = runner.invoke(app, ["run", "--config-path", str(config_file)])

    assert result.exit_code == 1
    assert "Error:" in result.output
