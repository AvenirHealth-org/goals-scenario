from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import orjson
from pydantic import ValidationError

from avenir_goals_scenario._scenario_generator.models.scenario_definition import ScenarioInput
from avenir_goals_scenario._scenario_generator.models.scenario_simulations import (
    InterventionOut,
    InterventionSimulation,
    ScenarioSimulation,
    ScenarioSimulations,
)


def _product_to_id(product: str) -> str:
    """Convert a product name to a slug suitable for use as a dict key."""
    slug = product.lower()
    slug = re.sub(r"[^a-z0-9]+", "_", slug)
    return slug.strip("_")


def gen_simulations(
    definition: ScenarioInput,
    n_simulations: int = 100,
    rng: np.random.Generator | None = None,
) -> ScenarioSimulations:
    """Generate sampled simulations from a validated :class:`ScenarioInput`.

    Args:
        definition: Validated scenario definition.
        n_simulations: Number of simulations per scenario.
        rng: Optional seeded RNG for reproducibility; a fresh one is created if omitted.
            For parallel use, spawn independent child RNGs with ``rng.spawn(n)`` or
            ``np.random.SeedSequence(seed).spawn(n)`` before distributing work.

    Returns:
        A :class:`ScenarioSimulations` containing all scenarios and their simulations.
    """
    if rng is None:
        rng = np.random.default_rng()

    return ScenarioSimulations(
        scenarios=[
            ScenarioSimulation(
                scenario_id=scenario.id,
                interventions=[
                    InterventionOut(
                        id=_product_to_id(iv.product),
                        product=iv.product,
                        target_population=iv.target_population,
                        sex=iv.sex,
                    )
                    for iv in scenario.interventions
                ],
                simulations=[
                    {
                        _product_to_id(iv.product): InterventionSimulation({
                            name: dist.sample(rng) for name, dist in iv.parameters.items()
                        })
                        for iv in scenario.interventions
                    }
                    for _ in range(n_simulations)
                ],
            )
            for scenario in definition.resolved_scenarios()
        ]
    )


def load_scenario_definition(path: Path) -> ScenarioInput:
    """Load and validate a scenario definition JSON file.

    Args:
        path: Path to the JSON file.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file is not ``.json``, contains invalid JSON, or fails schema validation.
    """
    if path.suffix.lower() != ".json":
        msg = f"Input file must be a JSON file (.json), got: {path.suffix or '(no extension)'}"
        raise ValueError(msg)
    if not path.exists():
        msg = f"Input file not found: {path}"
        raise FileNotFoundError(msg)

    try:
        data = orjson.loads(path.read_bytes())
    except orjson.JSONDecodeError as e:
        msg = f"Input file contains invalid JSON: {e}"
        raise ValueError(msg) from e

    try:
        return ScenarioInput.model_validate(data)
    except ValidationError as e:
        msg = f"Invalid scenario definition:\n{e}"
        raise ValueError(msg) from e
