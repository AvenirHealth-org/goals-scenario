from pathlib import Path
from unittest.mock import patch

import orjson
import pytest
from pydantic import ValidationError
from typer.testing import CliRunner

from avenir_goals_scenario.cli import _load_config, app
from avenir_goals_scenario.models import RunConfig

runner = CliRunner()


def _valid_config(tmp_path) -> dict:
    """Return a valid config dict with paths that actually exist."""
    pjnz_dir = tmp_path / "pjnz"
    pjnz_dir.mkdir()
    scenario_file = tmp_path / "scenarios.json"
    scenario_file.touch()
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return {
        "pjnz_dir": str(pjnz_dir),
        "scenario_path": str(scenario_file),
        "output_dir": str(output_dir),
        "base_year": 2025,
        "output_indicators": ["PLHIV", "New Infections"],
    }


# --- _load_config ---


def test_load_config_parses_valid_json(tmp_path):
    config = _valid_config(tmp_path)
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(config))

    result = _load_config(config_file)

    assert result.pjnz_dir == Path(config["pjnz_dir"]).resolve()
    assert result.scenario_path == Path(config["scenario_path"]).resolve()
    assert result.output_dir == Path(config["output_dir"]).resolve()
    assert result.base_year == 2025
    assert result.output_indicators == ["PLHIV", "New Infections"]


def test_load_config_accepts_uppercase_keys(tmp_path):
    config = {k.upper(): v for k, v in _valid_config(tmp_path).items()}
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(config))

    assert isinstance(_load_config(config_file), RunConfig)


def test_load_config_accepts_lowercase_keys(tmp_path):
    config = _valid_config(tmp_path)
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(config))

    assert isinstance(_load_config(config_file), RunConfig)


def test_load_config_non_dict_input_raises():
    with pytest.raises(ValidationError):
        RunConfig.model_validate(["not", "a", "dict"])


def test_load_config_raises_on_missing_fields(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps({"pjnz_dir": "/pjnz"}))

    with pytest.raises(ValidationError):
        _load_config(config_file)


def test_load_config_raises_when_pjnz_dir_missing(tmp_path):
    config = _valid_config(tmp_path)
    config["pjnz_dir"] = str(tmp_path / "nonexistent")
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(config))

    with pytest.raises(ValidationError, match="does not exist"):
        _load_config(config_file)


def test_load_config_raises_when_pjnz_dir_is_a_file(tmp_path):
    config = _valid_config(tmp_path)
    f = tmp_path / "not_a_dir.txt"
    f.touch()
    config["pjnz_dir"] = str(f)
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(config))

    with pytest.raises(ValidationError, match="not a directory"):
        _load_config(config_file)


def test_load_config_raises_when_scenario_path_missing(tmp_path):
    config = _valid_config(tmp_path)
    config["scenario_path"] = str(tmp_path / "nonexistent.json")
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(config))

    with pytest.raises(ValidationError, match="does not exist"):
        _load_config(config_file)


def test_load_config_raises_when_scenario_path_is_a_dir(tmp_path):
    config = _valid_config(tmp_path)
    d = tmp_path / "a_dir"
    d.mkdir()
    config["scenario_path"] = str(d)
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(config))

    with pytest.raises(ValidationError, match="not a file"):
        _load_config(config_file)


def test_load_config_accepts_nonexistent_output_dir_when_parent_exists(tmp_path):
    config = _valid_config(tmp_path)
    new_dir = tmp_path / "output" / "new_subdir"
    config["output_dir"] = str(new_dir)
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(config))

    result = _load_config(config_file)

    assert not new_dir.exists()
    assert result.output_dir == new_dir.resolve()


def test_load_config_n_workers_zero_raises(tmp_path):
    config = _valid_config(tmp_path)
    config["n_workers"] = 0
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(config))

    with pytest.raises(ValidationError, match="n_workers"):
        _load_config(config_file)


def test_load_config_n_workers_defaults_to_4_when_many_cpus(tmp_path):
    config = _valid_config(tmp_path)
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(config))

    with patch("avenir_goals_scenario.models.run_config.os.cpu_count", return_value=8):
        result = _load_config(config_file)

    assert result.n_workers == 4


def test_load_config_n_workers_defaults_to_cpu_count_when_fewer_than_4(tmp_path):
    config = _valid_config(tmp_path)
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(config))

    with patch("avenir_goals_scenario.models.run_config.os.cpu_count", return_value=2):
        result = _load_config(config_file)

    assert result.n_workers == 2


def test_load_config_raises_when_output_dir_is_a_file(tmp_path):
    config = _valid_config(tmp_path)
    f = tmp_path / "not_a_dir.txt"
    f.touch()
    config["output_dir"] = str(f)
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(config))

    with pytest.raises(ValidationError, match="not a directory"):
        _load_config(config_file)


def test_load_config_raises_when_output_dir_parent_missing(tmp_path):
    config = _valid_config(tmp_path)
    config["output_dir"] = str(tmp_path / "nonexistent" / "nested")
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(config))

    with pytest.raises(ValidationError, match="parent directory does not exist"):
        _load_config(config_file)


# --- CLI: --version ---


def test_cli_version_long():
    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert "goals-scenario" in result.output


def test_cli_version_short_v_is_not_version():
    # -v is reserved for future verbose flag, not version
    result = runner.invoke(app, ["-v"])

    assert "goals-scenario" not in result.output


# --- CLI: -h / --help ---


def test_cli_help_long():
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0


def test_cli_help_short():
    result = runner.invoke(app, ["-h"])

    assert result.exit_code == 0


# --- CLI: simulations command ---


def test_cli_simulations_requires_args():
    result = runner.invoke(app, ["simulations"])

    assert result.exit_code != 0


def test_cli_simulations_positional_args(tmp_path):
    dest = tmp_path / "out.json"
    src = tmp_path / "input.json"

    with patch("avenir_goals_scenario.cli.generate_simulations") as mock_gen:
        result = runner.invoke(app, ["simulations", str(src), str(dest)])

    assert result.exit_code == 0
    mock_gen.assert_called_once_with(src, dest, 100)


def test_cli_simulations_n_simulations_long_flag(tmp_path):
    dest = tmp_path / "out.json"
    src = tmp_path / "input.json"

    with patch("avenir_goals_scenario.cli.generate_simulations") as mock_gen:
        result = runner.invoke(app, ["simulations", str(src), str(dest), "--n-simulations", "10"])

    assert result.exit_code == 0
    mock_gen.assert_called_once_with(src, dest, 10)


def test_cli_simulations_n_simulations_short_flag(tmp_path):
    dest = tmp_path / "out.json"
    src = tmp_path / "input.json"

    with patch("avenir_goals_scenario.cli.generate_simulations") as mock_gen:
        result = runner.invoke(app, ["simulations", str(src), str(dest), "-n", "5"])

    assert result.exit_code == 0
    mock_gen.assert_called_once_with(src, dest, 5)


def test_cli_simulations_prints_success_message(tmp_path):
    dest = tmp_path / "out.json"
    src = tmp_path / "input.json"

    with patch("avenir_goals_scenario.cli.generate_simulations"):
        result = runner.invoke(app, ["simulations", str(src), str(dest)])

    assert result.exit_code == 0
    assert "Done" in result.output
    assert "out.json" in result.output


def test_cli_simulations_handles_errors():
    with patch("avenir_goals_scenario.cli.generate_simulations", side_effect=RuntimeError("something went wrong")):
        result = runner.invoke(app, ["simulations", "/x/in.json", "/x/out.json"])

    assert result.exit_code == 1
    assert "ERROR" in result.output


def test_cli_simulations_handles_error_without_message():
    with patch("avenir_goals_scenario.cli.generate_simulations", side_effect=NotImplementedError()):
        result = runner.invoke(app, ["simulations", "/x/in.json", "/x/out.json"])

    assert result.exit_code == 1
    assert "NotImplementedError" in result.output


# --- CLI: run command ---


def test_cli_run_requires_config_path():
    result = runner.invoke(app, ["run"])

    assert result.exit_code != 0


def test_cli_run_calls_run_scenario_analysis_cli(tmp_path):
    config = _valid_config(tmp_path)
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(config))

    with patch("avenir_goals_scenario.cli.run_with_progress") as mock_run:
        result = runner.invoke(app, ["run", str(config_file)])

    assert result.exit_code == 0
    mock_run.assert_called_once()
    config_arg = mock_run.call_args.args[0]
    assert isinstance(config_arg, RunConfig)
    assert config_arg.pjnz_dir == Path(config["pjnz_dir"]).resolve()


def test_cli_run_errors_on_non_json_file(tmp_path):
    config_file = tmp_path / "config.csv"
    config_file.write_text("a,b,c")

    result = runner.invoke(app, ["run", str(config_file)])

    assert result.exit_code == 1
    assert ".json" in result.output


def test_cli_run_errors_on_invalid_json(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text("this is not json {{{")

    result = runner.invoke(app, ["run", str(config_file)])

    assert result.exit_code == 1
    assert "Invalid JSON" in result.output


def test_cli_run_errors_when_config_file_missing(tmp_path):
    result = runner.invoke(app, ["run", str(tmp_path / "nonexistent.json")])

    assert result.exit_code == 1
    assert "ERROR" in result.output


def test_cli_run_errors_on_invalid_config(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps({"pjnz_dir": "/pjnz"}))

    result = runner.invoke(app, ["run", str(config_file)])

    assert result.exit_code == 1
    assert "ERROR" in result.output


def test_cli_run_handles_errors(tmp_path):
    config = _valid_config(tmp_path)
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(config))

    with patch("avenir_goals_scenario.cli.run_with_progress", side_effect=RuntimeError("something went wrong")):
        result = runner.invoke(app, ["run", str(config_file)])

    assert result.exit_code == 1
    assert "ERROR" in result.output
    assert "something went wrong" in result.output
    assert "Traceback" not in result.output

    # Traceback raised in verbose mode
    with patch("avenir_goals_scenario.cli.run_with_progress", side_effect=RuntimeError("something went wrong")):
        result = runner.invoke(app, ["-v", "run", str(config_file)])

    assert result.exit_code == 1
    assert "ERROR" in result.output
    assert "something went wrong" in result.output
    assert "Traceback" in result.output
