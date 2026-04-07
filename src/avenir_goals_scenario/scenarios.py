from pathlib import Path

import orjson

from avenir_goals_scenario._scenario_generator.scenario_generator import (
    gen_simulations,
    load_scenario_definition,
)


def generate_simulations(
    definition_path: Path | str,
    simulations_path: Path | str,
    n_simulations: int = 100,
) -> None:
    """Generate a scenario simulations file from a scenario definitions file.

    Reads ``definition_path``, draws ``n_simulations`` simulations for
    each scenario, and writes the result as JSON to ``simulations_path``.

    Args:
        definition_path: Path to the input CSV scenario definitions file.
        simulations_path: Path where the generated scenario simulations JSON will be written.
        n_simulations: Number of simulations drawn per scenario.

    Raises:
        FileNotFoundError: If ``definition_path`` does not exist, or the parent
            directory of ``simulations_path`` does not exist.
        ValueError: If ``definition_path`` is not a valid ``.csv`` file or its
            contents fail schema validation.
    """
    definition_path = Path(definition_path).resolve()
    simulations_path = Path(simulations_path).resolve()

    if not simulations_path.parent.exists():
        msg = f"Simulations destination directory does not exist: {simulations_path.parent}"
        raise FileNotFoundError(msg)

    definition = load_scenario_definition(definition_path)
    output = gen_simulations(definition, n_simulations=n_simulations)
    simulations_path.write_bytes(orjson.dumps(output.model_dump(), option=orjson.OPT_INDENT_2))
