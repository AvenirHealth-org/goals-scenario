import os
from importlib.metadata import version as pkg_version
from pathlib import Path
from typing import Annotated

import typer
from pydantic import ValidationError

from avenir_goals_scenario._cli.cli_utils import configure_cli_logging
from avenir_goals_scenario.models import RunConfig
from avenir_goals_scenario.runner import _run_scenario_analysis_cli
from avenir_goals_scenario.scenarios import generate_simulations

_CONTEXT = {"help_option_names": ["-h", "--help"]}

app = typer.Typer(help="Goals scenario analysis CLI.", context_settings=_CONTEXT)

# Stop Pydantic from printing its URL in error messages
# That will just be confusing to users of the CLI.
os.environ["PYDANTIC_ERRORS_INCLUDE_URL"] = "0"


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"goals-scenario {pkg_version('avenir-goals-scenario')}")
        raise typer.Exit() from None


@app.callback()
def _app_callback(
    version: Annotated[
        bool | None,
        typer.Option("--version", help="Show version and exit.", callback=_version_callback, is_eager=True),
    ] = None,
    verbose: Annotated[bool, typer.Option("-v", "--verbose", help="Enable debug logging.")] = False,
) -> None:
    configure_cli_logging(verbose)


# If the Exception has no message, return the type name.
def _fmt_error(e: Exception) -> str:
    return str(e) or type(e).__name__


@app.command()
def simulations(
    definition_path: Annotated[Path, typer.Argument(help="Path to the input scenario definition file.")],
    simulations_path: Annotated[Path, typer.Argument(help="Path to write the scenario simulations file to.")],
    n_simulations: Annotated[
        int, typer.Option("-n", "--n-simulations", help="Number of simulations to generate for each scenario.")
    ] = 100,
) -> None:
    """Generate a scenario simulations file from a scenario definition."""
    try:
        generate_simulations(definition_path, simulations_path, n_simulations)
    except Exception as e:
        typer.echo(f"Error: {_fmt_error(e)}", err=True)
        raise typer.Exit(code=1) from None
    typer.echo(f"Done. Simulations saved to {simulations_path.expanduser().resolve()}")


@app.command()
def run(
    config_path: Annotated[Path, typer.Argument(help="Path to a JSON config file.")],
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
        _run_scenario_analysis_cli(config)
    except Exception as e:
        typer.echo(f"Error: {_fmt_error(e)}", err=True)
        raise typer.Exit(code=1) from None
    typer.echo(f"Done. Results written to {config.output_dir}")


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

    with open(path) as f:
        return RunConfig.model_validate_json(f.read())


def main() -> None:
    app()  # pragma: no cover
