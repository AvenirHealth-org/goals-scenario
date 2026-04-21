from pathlib import Path
from unittest.mock import MagicMock, patch

import orjson
import pytest
from pydantic import ValidationError
from typer.testing import CliRunner

from avenir_goals_scenario._runner.indicator_dims import DimSpec, list_indicators
from avenir_goals_scenario.cli import _fmt_dim, _load_config, app
from avenir_goals_scenario.models import RunConfig, ScenarioSimulations

runner = CliRunner()


def _make_pjnz_dir(tmp_path) -> Path:
    d = tmp_path / "pjnz"
    d.mkdir(exist_ok=True)
    return d


def _make_output_dir(tmp_path) -> Path:
    d = tmp_path / "output"
    d.mkdir(exist_ok=True)
    return d


def _make_scenario_file(tmp_path) -> Path:
    f = tmp_path / "scenarios.json"
    f.touch()
    return f


def _make_definition_file(tmp_path) -> Path:
    f = tmp_path / "scenarios.csv"
    f.touch()
    return f


def _base_config(tmp_path) -> dict:
    """Minimal valid config with required fields only (no scenario/definition path)."""
    return {
        "pjnz_dir": str(_make_pjnz_dir(tmp_path)),
        "output_dir": str(_make_output_dir(tmp_path)),
        "base_year": 2025,
        "output_indicators": ["PLHIV", "New Infections"],
    }


def _valid_config_scenario(tmp_path) -> dict:
    """Config with scenario_path (existing file)."""
    config = _base_config(tmp_path)
    config["scenario_path"] = str(_make_scenario_file(tmp_path))
    return config


def _valid_config_definition(tmp_path) -> dict:
    """Config with definition_path (existing csv)."""
    config = _base_config(tmp_path)
    config["definition_path"] = str(_make_definition_file(tmp_path))
    return config


def _valid_config_both(tmp_path) -> dict:
    """Config with both definition_path and scenario_path."""
    config = _base_config(tmp_path)
    config["definition_path"] = str(_make_definition_file(tmp_path))
    config["scenario_path"] = str(_make_scenario_file(tmp_path))
    return config


# --- _load_config ---


def test_load_config_parses_valid_json(tmp_path):
    config = _valid_config_scenario(tmp_path)
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(config))

    result = _load_config(config_file)

    assert result.pjnz_dir == Path(config["pjnz_dir"]).resolve()
    assert result.scenario_path == Path(config["scenario_path"]).resolve()
    assert result.output_dir == Path(config["output_dir"]).resolve()
    assert result.base_year == 2025
    assert result.output_indicators == ["PLHIV", "New Infections"]


def test_load_config_accepts_uppercase_keys(tmp_path):
    config = {k.upper(): v for k, v in _valid_config_scenario(tmp_path).items()}
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(config))

    assert isinstance(_load_config(config_file), RunConfig)


def test_load_config_accepts_lowercase_keys(tmp_path):
    config = _valid_config_scenario(tmp_path)
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
    config = _valid_config_scenario(tmp_path)
    config["pjnz_dir"] = str(tmp_path / "nonexistent")
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(config))

    with pytest.raises(ValidationError, match="does not exist"):
        _load_config(config_file)


def test_load_config_raises_when_pjnz_dir_is_a_file(tmp_path):
    config = _valid_config_scenario(tmp_path)
    f = tmp_path / "not_a_dir.txt"
    f.touch()
    config["pjnz_dir"] = str(f)
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(config))

    with pytest.raises(ValidationError, match="not a directory"):
        _load_config(config_file)


def test_load_config_scenario_path_optional(tmp_path):
    config = _base_config(tmp_path)  # no scenario_path
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(config))

    result = _load_config(config_file)

    assert result.scenario_path is None


def test_load_config_scenario_path_null_explicit(tmp_path):
    config = _base_config(tmp_path)
    config["scenario_path"] = None
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(config))

    result = _load_config(config_file)

    assert result.scenario_path is None


def test_load_config_scenario_path_nonexistent_is_allowed(tmp_path):
    config = _valid_config_scenario(tmp_path)
    config["scenario_path"] = str(tmp_path / "does_not_exist.json")
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(config))

    result = _load_config(config_file)

    assert result.scenario_path is not None


def test_load_config_raises_when_scenario_path_is_a_dir(tmp_path):
    config = _valid_config_scenario(tmp_path)
    d = tmp_path / "a_dir"
    d.mkdir()
    config["scenario_path"] = str(d)
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(config))

    with pytest.raises(ValidationError, match="not a file"):
        _load_config(config_file)


def test_load_config_definition_path_optional(tmp_path):
    config = _valid_config_scenario(tmp_path)
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(config))

    result = _load_config(config_file)

    assert result.definition_path is None


def test_load_config_definition_path_null_explicit(tmp_path):
    config = _valid_config_scenario(tmp_path)
    config["definition_path"] = None
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(config))

    result = _load_config(config_file)

    assert result.definition_path is None


def test_load_config_raises_when_definition_path_missing(tmp_path):
    config = _valid_config_scenario(tmp_path)
    config["definition_path"] = str(tmp_path / "nonexistent.csv")
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(config))

    with pytest.raises(ValidationError, match="does not exist"):
        _load_config(config_file)


def test_load_config_raises_when_definition_path_is_a_dir(tmp_path):
    config = _valid_config_scenario(tmp_path)
    d = tmp_path / "a_dir"
    d.mkdir()
    config["definition_path"] = str(d)
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(config))

    with pytest.raises(ValidationError, match="not a file"):
        _load_config(config_file)


def test_load_config_raises_when_definition_path_not_csv(tmp_path):
    config = _valid_config_scenario(tmp_path)
    f = tmp_path / "def.txt"
    f.touch()
    config["definition_path"] = str(f)
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(config))

    with pytest.raises(ValidationError, match="\\.csv"):
        _load_config(config_file)


def test_load_config_n_simulations_defaults_to_100(tmp_path):
    config = _valid_config_scenario(tmp_path)
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(config))

    result = _load_config(config_file)

    assert result.n_simulations == 100


def test_load_config_n_simulations_custom(tmp_path):
    config = _valid_config_scenario(tmp_path)
    config["n_simulations"] = 42
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(config))

    result = _load_config(config_file)

    assert result.n_simulations == 42


def test_load_config_n_simulations_zero_raises(tmp_path):
    config = _valid_config_scenario(tmp_path)
    config["n_simulations"] = 0
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(config))

    with pytest.raises(ValidationError, match="n_simulations"):
        _load_config(config_file)


def test_load_config_seed_defaults_to_none(tmp_path):
    config = _valid_config_scenario(tmp_path)
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(config))

    result = _load_config(config_file)

    assert result.seed is None


def test_load_config_seed_custom(tmp_path):
    config = _valid_config_scenario(tmp_path)
    config["seed"] = 42
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(config))

    result = _load_config(config_file)

    assert result.seed == 42


def test_load_config_accepts_nonexistent_output_dir_when_parent_exists(tmp_path):
    config = _valid_config_scenario(tmp_path)
    new_dir = tmp_path / "output" / "new_subdir"
    config["output_dir"] = str(new_dir)
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(config))

    result = _load_config(config_file)

    assert not new_dir.exists()
    assert result.output_dir == new_dir.resolve()


def test_load_config_n_workers_zero_raises(tmp_path):
    config = _valid_config_scenario(tmp_path)
    config["n_workers"] = 0
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(config))

    with pytest.raises(ValidationError, match="n_workers"):
        _load_config(config_file)


def test_load_config_n_workers_defaults_to_4_when_many_cpus(tmp_path):
    config = _valid_config_scenario(tmp_path)
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(config))

    with patch("avenir_goals_scenario.models.run_config.os.cpu_count", return_value=8):
        result = _load_config(config_file)

    assert result.n_workers == 4


def test_load_config_n_workers_defaults_to_cpu_count_when_fewer_than_4(tmp_path):
    config = _valid_config_scenario(tmp_path)
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(config))

    with patch("avenir_goals_scenario.models.run_config.os.cpu_count", return_value=2):
        result = _load_config(config_file)

    assert result.n_workers == 2


def test_load_config_raises_when_output_dir_is_a_file(tmp_path):
    config = _valid_config_scenario(tmp_path)
    f = tmp_path / "not_a_dir.txt"
    f.touch()
    config["output_dir"] = str(f)
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(config))

    with pytest.raises(ValidationError, match="not a directory"):
        _load_config(config_file)


def test_load_config_raises_when_output_dir_parent_missing(tmp_path):
    config = _valid_config_scenario(tmp_path)
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


# --- _fmt_dim ---


def test_fmt_dim_string_passthrough():
    assert _fmt_dim("year") == "year"


def test_fmt_dim_dimspec_with_labels():
    d = DimSpec("sex", labels=["male", "female"])
    assert _fmt_dim(d) == "sex [male, female]"


def test_fmt_dim_dimspec_without_labels():
    d = DimSpec("age")
    assert _fmt_dim(d) == "age"


# --- CLI: indicators command ---


def test_cli_indicators_lists_all_indicators():
    result = runner.invoke(app, ["indicators"])

    assert result.exit_code == 0
    for name in list_indicators():
        assert name in result.output


def test_cli_indicators_shows_descriptions():
    result = runner.invoke(app, ["indicators"])

    assert result.exit_code == 0
    assert "Total births" in result.output


def test_cli_indicators_shows_dimension_labels():
    result = runner.invoke(app, ["indicators"])

    assert result.exit_code == 0
    assert "male" in result.output
    assert "female" in result.output


# --- CLI: draw command ---


def test_cli_draw_requires_config_path():
    result = runner.invoke(app, ["draw"])

    assert result.exit_code != 0


def test_cli_draw_calls_draw_and_write(tmp_path):
    config = _valid_config_both(tmp_path)
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(config))

    mock_simulations = MagicMock(spec=ScenarioSimulations)
    mock_simulations.model_dump_json.return_value = '{"scenarios": []}'

    with (
        patch("avenir_goals_scenario.cli.draw_simulations", return_value=mock_simulations) as mock_draw,
        patch("avenir_goals_scenario.cli.write_simulations") as mock_write,
    ):
        result = runner.invoke(app, ["draw", str(config_file)])

    assert result.exit_code == 0
    mock_draw.assert_called_once_with(
        Path(config["definition_path"]).resolve(),
        100,
        None,
        2025,  # base_year
    )
    mock_write.assert_called_once_with(mock_simulations, Path(config["scenario_path"]).resolve())


def test_cli_draw_passes_n_simulations_from_config(tmp_path):
    config = _valid_config_both(tmp_path)
    config["n_simulations"] = 50
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(config))

    mock_simulations = MagicMock(spec=ScenarioSimulations)
    mock_simulations.model_dump_json.return_value = '{"scenarios": []}'

    with (
        patch("avenir_goals_scenario.cli.draw_simulations", return_value=mock_simulations) as mock_draw,
        patch("avenir_goals_scenario.cli.write_simulations"),
    ):
        result = runner.invoke(app, ["draw", str(config_file)])

    assert result.exit_code == 0
    assert mock_draw.call_args.args[1] == 50


def test_cli_draw_passes_seed_from_config(tmp_path):
    config = _valid_config_both(tmp_path)
    config["seed"] = 99
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(config))

    mock_simulations = MagicMock(spec=ScenarioSimulations)
    mock_simulations.model_dump_json.return_value = '{"scenarios": []}'

    with (
        patch("avenir_goals_scenario.cli.draw_simulations", return_value=mock_simulations) as mock_draw,
        patch("avenir_goals_scenario.cli.write_simulations"),
    ):
        result = runner.invoke(app, ["draw", str(config_file)])

    assert result.exit_code == 0
    assert mock_draw.call_args.args[2] == 99


def test_cli_draw_passes_base_year_from_config(tmp_path):
    config = _valid_config_both(tmp_path)
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(config))

    mock_simulations = MagicMock(spec=ScenarioSimulations)
    mock_simulations.model_dump_json.return_value = '{"scenarios": []}'

    with (
        patch("avenir_goals_scenario.cli.draw_simulations", return_value=mock_simulations) as mock_draw,
        patch("avenir_goals_scenario.cli.write_simulations"),
    ):
        runner.invoke(app, ["draw", str(config_file)])

    assert mock_draw.call_args.args[3] == config["base_year"]


def test_cli_draw_prints_success_message(tmp_path):
    config = _valid_config_both(tmp_path)
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(config))

    mock_simulations = MagicMock(spec=ScenarioSimulations)
    mock_simulations.model_dump_json.return_value = '{"scenarios": []}'

    with (
        patch("avenir_goals_scenario.cli.draw_simulations", return_value=mock_simulations),
        patch("avenir_goals_scenario.cli.write_simulations"),
    ):
        result = runner.invoke(app, ["draw", str(config_file)])

    assert result.exit_code == 0
    assert "Done" in result.output


def test_cli_draw_errors_on_invalid_config(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps({"pjnz_dir": "/pjnz"}))

    result = runner.invoke(app, ["draw", str(config_file)])

    assert result.exit_code == 1
    assert "Invalid config" in result.output


def test_cli_draw_errors_on_non_json_file(tmp_path):
    config_file = tmp_path / "config.csv"
    config_file.write_text("a,b,c")

    result = runner.invoke(app, ["draw", str(config_file)])

    assert result.exit_code == 1
    assert ".json" in result.output


def test_cli_draw_errors_when_definition_path_missing(tmp_path):
    config = _valid_config_scenario(tmp_path)  # no definition_path
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(config))

    result = runner.invoke(app, ["draw", str(config_file)])

    assert result.exit_code == 1
    assert "definition_path" in result.output


def test_cli_draw_errors_when_scenario_path_missing(tmp_path):
    config = _valid_config_definition(tmp_path)  # no scenario_path
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(config))

    result = runner.invoke(app, ["draw", str(config_file)])

    assert result.exit_code == 1
    assert "scenario_path" in result.output


def test_cli_draw_handles_errors(tmp_path):
    config = _valid_config_both(tmp_path)
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(config))

    with patch("avenir_goals_scenario.cli.draw_simulations", side_effect=RuntimeError("boom")):
        result = runner.invoke(app, ["draw", str(config_file)])

    assert result.exit_code == 1
    assert "boom" in result.output


def test_cli_draw_handles_error_without_message(tmp_path):
    config = _valid_config_both(tmp_path)
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(config))

    with patch("avenir_goals_scenario.cli.draw_simulations", side_effect=NotImplementedError()):
        result = runner.invoke(app, ["draw", str(config_file)])

    assert result.exit_code == 1
    assert "NotImplementedError" in result.output


# --- CLI: run command ---


def test_cli_run_requires_config_path():
    result = runner.invoke(app, ["run"])

    assert result.exit_code != 0


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


def test_cli_run_errors_when_neither_definition_nor_scenario_set(tmp_path):
    config = _base_config(tmp_path)  # no definition_path or scenario_path
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(config))

    result = runner.invoke(app, ["run", str(config_file)])

    assert result.exit_code == 1
    assert "definition_path" in result.output or "scenario_path" in result.output


# --- run: scenario_path only (case 2) ---


def test_cli_run_with_scenario_only_calls_run_with_progress(tmp_path):
    config = _valid_config_scenario(tmp_path)
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(config))

    mock_simulations = MagicMock(spec=ScenarioSimulations)
    with (
        patch("avenir_goals_scenario.cli.read_simulations", return_value=mock_simulations) as mock_read,
        patch("avenir_goals_scenario.cli.run_with_progress") as mock_run,
    ):
        result = runner.invoke(app, ["run", str(config_file)])

    assert result.exit_code == 0
    mock_read.assert_called_once_with(Path(config["scenario_path"]).resolve())
    mock_run.assert_called_once_with(mock_run.call_args.args[0], mock_simulations)


def test_cli_run_with_scenario_only_errors_when_file_missing(tmp_path):
    config = _base_config(tmp_path)
    config["scenario_path"] = str(tmp_path / "missing.json")
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(config))

    result = runner.invoke(app, ["run", str(config_file)])

    assert result.exit_code == 1
    assert "does not exist" in result.output


# --- run: definition_path only (case 1) ---


def test_cli_run_with_definition_only_draws_and_runs(tmp_path):
    config = _valid_config_definition(tmp_path)
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(config))

    mock_simulations = MagicMock(spec=ScenarioSimulations)
    mock_simulations.model_dump_json.return_value = '{"scenarios": []}'

    with (
        patch("avenir_goals_scenario.cli.draw_simulations", return_value=mock_simulations) as mock_draw,
        patch("avenir_goals_scenario.cli.write_simulations") as mock_write,
        patch("avenir_goals_scenario.cli.run_with_progress") as mock_run,
    ):
        result = runner.invoke(app, ["run", str(config_file)])

    assert result.exit_code == 0
    mock_draw.assert_called_once_with(Path(config["definition_path"]).resolve(), 100, None, config["base_year"])
    mock_write.assert_called_once()
    mock_run.assert_called_once()


def test_cli_run_with_definition_only_saves_to_output_dir(tmp_path):
    config = _valid_config_definition(tmp_path)
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(config))

    mock_simulations = MagicMock(spec=ScenarioSimulations)
    mock_simulations.model_dump_json.return_value = '{"scenarios": []}'

    with (
        patch("avenir_goals_scenario.cli.draw_simulations", return_value=mock_simulations),
        patch("avenir_goals_scenario.cli.write_simulations") as mock_write,
        patch("avenir_goals_scenario.cli.run_with_progress"),
    ):
        result = runner.invoke(app, ["run", str(config_file)])

    assert result.exit_code == 0
    written_path = mock_write.call_args.args[1]
    assert written_path == Path(config["output_dir"]).resolve() / "draws.json"


def test_cli_run_with_definition_passes_seed_and_n_simulations(tmp_path):
    config = _valid_config_definition(tmp_path)
    config["n_simulations"] = 50
    config["seed"] = 7
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(config))

    mock_simulations = MagicMock(spec=ScenarioSimulations)
    mock_simulations.model_dump_json.return_value = '{"scenarios": []}'

    with (
        patch("avenir_goals_scenario.cli.draw_simulations", return_value=mock_simulations) as mock_draw,
        patch("avenir_goals_scenario.cli.write_simulations"),
        patch("avenir_goals_scenario.cli.run_with_progress"),
    ):
        runner.invoke(app, ["run", str(config_file)])

    assert mock_draw.call_args.args[1] == 50
    assert mock_draw.call_args.args[2] == 7


def test_cli_run_with_definition_passes_base_year(tmp_path):
    config = _valid_config_definition(tmp_path)
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(config))

    mock_simulations = MagicMock(spec=ScenarioSimulations)
    mock_simulations.model_dump_json.return_value = '{"scenarios": []}'

    with (
        patch("avenir_goals_scenario.cli.draw_simulations", return_value=mock_simulations) as mock_draw,
        patch("avenir_goals_scenario.cli.write_simulations"),
        patch("avenir_goals_scenario.cli.run_with_progress"),
    ):
        runner.invoke(app, ["run", str(config_file)])

    assert mock_draw.call_args.args[3] == config["base_year"]


# --- run: both provided, file exists (case 3) ---


def test_cli_run_with_both_existing_scenario_uses_existing(tmp_path):
    config = _valid_config_both(tmp_path)
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(config))

    mock_simulations = MagicMock(spec=ScenarioSimulations)
    with (
        patch("avenir_goals_scenario.cli.read_simulations", return_value=mock_simulations),
        patch("avenir_goals_scenario.cli.run_with_progress") as mock_run,
    ):
        result = runner.invoke(app, ["run", str(config_file)])

    assert result.exit_code == 0
    assert "Using existing" in result.output
    mock_run.assert_called_once()


# --- run: both provided, file missing (case 4) ---


def test_cli_run_with_both_missing_scenario_redraws_and_saves(tmp_path):
    config = _valid_config_definition(tmp_path)
    scenario_path = tmp_path / "draws.json"
    config["scenario_path"] = str(scenario_path)
    assert not scenario_path.exists()
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(config))

    mock_simulations = MagicMock(spec=ScenarioSimulations)
    mock_simulations.model_dump_json.return_value = '{"scenarios": []}'

    with (
        patch("avenir_goals_scenario.cli.draw_simulations", return_value=mock_simulations) as mock_draw,
        patch("avenir_goals_scenario.cli.write_simulations") as mock_write,
        patch("avenir_goals_scenario.cli.run_with_progress") as mock_run,
    ):
        result = runner.invoke(app, ["run", str(config_file)])

    assert result.exit_code == 0
    mock_draw.assert_called_once()
    mock_write.assert_called_once_with(mock_simulations, scenario_path.resolve())
    mock_run.assert_called_once()


# --- run: error handling ---


def test_cli_run_handles_errors(tmp_path):
    config = _valid_config_scenario(tmp_path)
    config_file = tmp_path / "config.json"
    config_file.write_bytes(orjson.dumps(config))

    mock_simulations = MagicMock(spec=ScenarioSimulations)
    with (
        patch("avenir_goals_scenario.cli.read_simulations", return_value=mock_simulations),
        patch("avenir_goals_scenario.cli.run_with_progress", side_effect=RuntimeError("something went wrong")),
    ):
        result = runner.invoke(app, ["run", str(config_file)])

    assert result.exit_code == 1
    assert "ERROR" in result.output
    assert "something went wrong" in result.output
    assert "Traceback" not in result.output

    # Traceback raised in verbose mode
    with (
        patch("avenir_goals_scenario.cli.read_simulations", return_value=mock_simulations),
        patch("avenir_goals_scenario.cli.run_with_progress", side_effect=RuntimeError("something went wrong")),
    ):
        result = runner.invoke(app, ["-v", "run", str(config_file)])

    assert result.exit_code == 1
    assert "ERROR" in result.output
    # Rich may wrap long lines, so check parts independently
    assert "something" in result.output and "went wrong" in result.output
    assert "Traceback" in result.output
