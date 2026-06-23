import json
import multiprocessing
import os
from importlib.metadata import version as pkg_version
from pathlib import Path
from typing import Annotated

import typer
from loguru import logger
from pydantic import ValidationError
from rich.console import Console
from rich.table import Table

from avenir_goals_scenario._cli.cli_utils import configure_cli_logging, run_with_progress
from avenir_goals_scenario._runner.indicator_dims import list_indicators
from avenir_goals_scenario.models import RunConfig
from avenir_goals_scenario.models.scenario_simulations import ScenarioSimulations
from avenir_goals_scenario.scenarios import draw_simulations, read_simulations, write_simulations

_CONTEXT = {"help_option_names": ["-h", "--help"]}
_DOCS_URL = "[link=https://avenirhealth-org.github.io/goals-scenario/cli/]https://avenirhealth-org.github.io/goals-scenario/cli/[/link]"

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
def draw(
    config_path: Annotated[
        Path,
        typer.Argument(help=f"Path to a JSON config file. See {_DOCS_URL} for format."),
    ],
) -> None:
    """Draw scenario simulations and save to disk.

    Reads ``definition_path``, ``scenario_path``, ``n_simulations``,
    ``seed``, and ``base_year`` from the config file. Draws are written
    to ``scenario_path``. Both ``definition_path`` and ``scenario_path``
    must be present in the config.
    """
    try:
        config = _load_config(config_path)
    except ValidationError as e:
        logger.error("Invalid config: {}", _fmt_error(e))
        raise typer.Exit(code=1) from None
    except Exception as e:
        logger.error(_fmt_error(e))
        raise typer.Exit(code=1) from None

    if config.definition_path is None:
        logger.error("definition_path must be set in config for the draw command. See {}", _DOCS_URL)
        raise typer.Exit(code=1)
    if config.scenario_path is None:
        logger.error("scenario_path must be set in config for the draw command. See {}", _DOCS_URL)
        raise typer.Exit(code=1)

    try:
        simulations = draw_simulations(config.definition_path, config.base_year, config.n_simulations, config.seed)
        write_simulations(simulations, config.scenario_path)
    except Exception as e:
        logger.exception(_fmt_error(e))
        raise typer.Exit(code=1) from None
    logger.info("Done. Draws saved to {}", config.scenario_path.expanduser().resolve())


@app.command()
def run(
    config_path: Annotated[
        Path,
        typer.Argument(help=f"Path to a JSON config file. See {_DOCS_URL} for format."),
    ],
    retry: Annotated[
        Path | None,
        typer.Option(
            "--retry",
            help="Re-run only the (PJNZ, scenario) units listed in a failures.json from a previous run.",
        ),
    ] = None,
) -> None:
    """Run scenario analysis using a JSON config file.

    Behaviour depends on which of ``definition_path`` and ``scenario_path``
    are set in the config:

    \b
    - definition_path only  : draws in memory, saves to <output_dir>/draws.json, runs.
    - scenario_path only    : loads draws from the file and runs.
    - both (file exists)    : uses existing draws, runs.
    - both (file missing)   : redraws, saves to scenario_path, runs.

    Individual (PJNZ, scenario) units that fail are logged and skipped rather
    than aborting the run; failures are written to <output_dir>/failures.json.
    Pass ``--retry <output_dir>/failures.json`` to re-run only those units.

    \b
    Exit codes: 0 success, 1 fatal error (bad config or PJNZ import failure),
    2 partial (some scenario units failed but output was produced).
    """
    try:
        config = _load_config(config_path)
    except ValidationError as e:
        logger.exception("Invalid config {}", _fmt_error(e))
        raise typer.Exit(code=1) from None
    except Exception as e:
        logger.exception(_fmt_error(e))
        raise typer.Exit(code=1) from None

    if config.definition_path is None and config.scenario_path is None:
        logger.error("Config must include definition_path, scenario_path, or both. See {}", _DOCS_URL)
        raise typer.Exit(code=1)

    selected_units = None
    if retry is not None:
        try:
            selected_units = _load_retry_units(retry)
        except Exception as e:
            logger.error("Could not read --retry file: {}", _fmt_error(e))
            raise typer.Exit(code=1) from None
        logger.info("Retrying {} failed unit(s) from {}", len(selected_units), retry)

    try:
        simulations = _prepare_simulations(config)
        result = run_with_progress(config, simulations, selected_units=selected_units)
    except Exception as e:
        logger.exception(_fmt_error(e))
        raise typer.Exit(code=1) from None

    if result.failures:
        raise typer.Exit(code=2)


def _load_retry_units(retry_path: Path) -> set[tuple[str, str]]:
    """Parse a failures.json manifest into a set of (pjnz, scenario_id) pairs.

    Raises:
        ValueError: If the file is not JSON or is malformed.
    """
    if retry_path.suffix.lower() != ".json":
        err_msg = f"--retry file must be a JSON file (.json), got: {retry_path.suffix or '(no extension)'}"
        raise ValueError(err_msg)

    with open(retry_path) as f:
        data = json.load(f)

    failures = data.get("failures") if isinstance(data, dict) else None
    if not isinstance(failures, list):
        err_msg = f"--retry file {retry_path} is not a valid failures manifest (missing 'failures' list)."
        raise ValueError(err_msg)  # noqa: TRY004 - malformed manifest content, not a programmer type error

    return {(f["pjnz"], f["scenario_id"]) for f in failures}


def _prepare_simulations(config: RunConfig):
    """Resolve scenario simulations from config, drawing and/or saving as needed.

    Behaviour:
    - definition_path only  : draws, saves to <output_dir>/draws.json.
    - scenario_path only    : loads from file (must exist).
    - both (file exists)    : loads from file.
    - both (file missing)   : draws, saves to scenario_path.
    """

    def _draw(definition_path: Path) -> ScenarioSimulations:
        return draw_simulations(definition_path, config.base_year, config.n_simulations, config.seed)

    if config.definition_path is None:
        # We can ignore invalid argument error, we've validated this previously
        return read_simulations(config.scenario_path)  # ty: ignore[invalid-argument-type]

    if config.scenario_path is None:
        config.output_dir.mkdir(exist_ok=True)
        simulations = _draw(config.definition_path)
        auto_path = config.output_dir / "draws.json"
        write_simulations(simulations, auto_path)
        logger.info("Draws saved to {}", auto_path)
        return simulations

    # Both provided — load if file exists, otherwise redraw.
    if config.scenario_path.exists():
        logger.info("Using existing draws from {}", config.scenario_path)
        return read_simulations(config.scenario_path)

    simulations = _draw(config.definition_path)
    write_simulations(simulations, config.scenario_path)
    logger.info("Draws saved to {}", config.scenario_path)
    return simulations


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


def _fmt_dim(d) -> str:
    """Format a single dim spec as 'name [label1, label2, ...]' or just 'name'."""
    if isinstance(d, str):
        return d
    if d.labels:
        return f"{d.name} [{', '.join(d.labels)}]"
    return d.name


@app.command()
def indicators() -> None:
    """List all supported output indicators with descriptions and dimensions."""
    table = Table(show_header=True, header_style="bold cyan", show_lines=True)
    table.add_column("Indicator", style="bold", no_wrap=True)
    table.add_column("Description")
    table.add_column("Columns")

    from rich.markup import escape

    for name, spec in list_indicators().items():
        dim_lines = [_fmt_dim(d) for d in spec.dims] + ["year"]
        table.add_row(name, escape(spec.description), escape("\n".join(dim_lines)))

    Console().print(table)


def main() -> None:
    app()  # pragma: no cover


# no cover: start
# Block used only when running exe created by Pyinstaller
if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
# no cover: stop
