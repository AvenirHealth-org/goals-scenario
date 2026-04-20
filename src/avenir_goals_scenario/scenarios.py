from pathlib import Path

import numpy as np

from avenir_goals_scenario._scenario_generator.scenario_generator import (
    gen_simulations,
    load_scenario_definition,
)
from avenir_goals_scenario.models.scenario_simulations import ScenarioSimulations


def draw_simulations(
    definition_path: Path | str,
    n_simulations: int = 100,
    seed: int | None = None,
    base_year: int | None = None,
) -> ScenarioSimulations:
    """Draw scenario simulations in memory from a scenario definitions file.

    Args:
        definition_path: Path to the input CSV scenario definitions file.
        n_simulations: Number of simulations drawn per scenario.
        seed: Optional integer seed for reproducible draws.
        base_year: If provided, used as the minimum value for ``target_year``
            draws. Draws below ``base_year`` are clamped up to it.

    Returns:
        A ``avenir_goals_scenario.models.ScenarioSimulations`` containing
        all scenarios and their draws.

    Raises:
        FileNotFoundError: If ``definition_path`` does not exist.
        ValueError: If ``definition_path`` is not a valid ``.csv`` file or its
            contents fail schema validation.
    """
    definition_path = Path(definition_path).expanduser().resolve()
    rng = np.random.default_rng(seed)
    definition = load_scenario_definition(definition_path)
    return gen_simulations(definition, n_simulations=n_simulations, rng=rng, base_year=base_year)


def write_simulations(simulations: ScenarioSimulations, path: Path | str) -> Path:
    """Write scenario simulations to a JSON file.

    Args:
        simulations: The scenario simulations to write.
        path: Destination path for the JSON file.

    Returns:
        The resolved path that was written to.

    Raises:
        FileNotFoundError: If the parent directory of ``path`` does not exist.
    """
    path = Path(path).expanduser().resolve()
    if not path.parent.exists():
        msg = f"Destination directory does not exist: {path.parent}"
        raise FileNotFoundError(msg)
    path.write_text(simulations.model_dump_json(indent=2))
    return path


def read_simulations(path: Path | str) -> ScenarioSimulations:
    """Read scenario simulations from a JSON file.

    Args:
        path: Path to the scenario simulations JSON file.

    Returns:
        The loaded ``avenir_goals_scenario.models.ScenarioSimulations``.

    Raises:
        FileNotFoundError: If ``path`` does not exist.
        ValueError: If the file contents fail schema validation.
    """
    path = Path(path).expanduser().resolve()
    if not path.exists():
        msg = f"Simulations file does not exist: {path}"
        raise FileNotFoundError(msg)
    return ScenarioSimulations.model_validate_json(path.read_bytes())
