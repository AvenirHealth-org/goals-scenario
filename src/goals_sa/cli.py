from __future__ import annotations

import json
from importlib.metadata import version as pkg_version
from pathlib import Path
from typing import Annotated, Any

import typer
from pydantic import BaseModel, ValidationError, model_validator

from goals_sa.runner import run_scenario_analysis
from goals_sa.scenarios import generate_scenarios

_CONTEXT = {"help_option_names": ["-h", "--help"]}

app = typer.Typer(help="Goals scenario analysis CLI.", context_settings=_CONTEXT)


class RunConfig(BaseModel):
    """Validated configuration for run_scenario_analysis.

    Field names are case-insensitive: Goals_path, goals_path, GOALS_PATH all work.
    """

    goals_path: str
    scenario_path: str
    scenario_file_name: str
    output_path: str
    output_file_name: str
    base_year: str
    output_indicators: list[str]

    @model_validator(mode="before")
    @classmethod
    def _lowercase_keys(cls, data: Any) -> Any:
        if isinstance(data, dict):
            return {k.lower(): v for k, v in data.items()}
        return data  # pragma: no cover


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"goals-sa {pkg_version('goals-sa')}")
        raise typer.Exit() from None


@app.callback()
def _app_callback(
    version: Annotated[
        bool | None,
        typer.Option("-v", "--version", help="Show version and exit.", callback=_version_callback, is_eager=True),
    ] = None,
) -> None:
    pass


# If the Exception has no message, return the type
def _fmt_error(e: Exception) -> str:
    return str(e) or type(e).__name__


@app.command()
def scenarios(
    dest_path: Annotated[Path, typer.Option("--dest-path", help="Path to write the generated scenarios file to.")],
) -> None:
    """Generate a scenarios file."""
    try:
        generate_scenarios(dest_path)
    except Exception as e:
        typer.echo(f"Error: {_fmt_error(e)}", err=True)
        raise typer.Exit(code=1) from None


@app.command()
def run(
    config_path: Annotated[Path, typer.Option("--config-path", help="Path to a JSON config file.")],
) -> None:
    """Run scenario analysis using a JSON config file."""
    try:
        config = _load_config(config_path)
    except ValidationError as e:
        typer.echo(f"Error: invalid config:\n{e}", err=True)
        raise typer.Exit(code=1) from None
    except Exception as e:
        typer.echo(f"Error: {_fmt_error(e)}", err=True)
        raise typer.Exit(code=1) from None

    try:
        run_scenario_analysis(
            pjnz_dir=Path(config.goals_path),
            scenarios_path=Path(config.scenario_path) / config.scenario_file_name,
            output_path=Path(config.output_path) / config.output_file_name,
        )
    except Exception as e:
        typer.echo(f"Error: {_fmt_error(e)}", err=True)
        raise typer.Exit(code=1) from None


def _load_config(path: Path) -> RunConfig:
    """Load and validate a JSON config file.

    Field names in the JSON are case-insensitive.

    Args:
        path: Path to the JSON config file.

    Returns:
        Validated RunConfig instance.

    Raises:
        ValueError: If the file is not a .json file or contains invalid JSON.
        pydantic.ValidationError: If the config is missing required fields or has invalid values.
    """
    if path.suffix.lower() != ".json":
        err_msg = f"Config file must be a JSON file (.json), got: {path.suffix or '(no extension)'}"
        raise ValueError(err_msg)
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        err_msg = f"Config file contains invalid JSON: {e}"
        raise ValueError(err_msg) from e
    return RunConfig.model_validate(data)


def main() -> None:
    app()  # pragma: no cover
