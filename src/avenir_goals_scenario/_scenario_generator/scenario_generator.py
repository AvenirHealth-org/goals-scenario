from __future__ import annotations

import csv
import re
from pathlib import Path

import numpy as np
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


_COMBINED_PATTERN = re.compile(r"^\d+(\+\d+)+$")


def _parse_scenario_csv(path: Path) -> ScenarioInput:
    scenario_defs: list[dict] = []
    try:
        with path.open(newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)  # skip header
            for row in reader:
                if not row or not row[0].strip():
                    continue
                row_id = int(row[0].strip())
                product = row[1].strip()
                if _COMBINED_PATTERN.match(product):
                    combines = [int(x) for x in product.split("+")]
                    scenario_defs.append({"id": row_id, "combines": combines})
                else:
                    scenario_defs.append({
                        "id": row_id,
                        "interventions": [
                            {
                                "product": product,
                                "target_population": [row[10].strip()],
                                "sex": row[11].strip(),
                                "parameters": {
                                    "efficacy": {"mean": float(row[2]), "sd": float(row[3])},
                                    "adherence": {"mean": float(row[4]), "sd": float(row[5])},
                                    "target_coverage": {"mean": float(row[6]), "sd": float(row[7])},
                                    "target_year": {"mean": float(row[8]), "sd": float(row[9])},
                                },
                            }
                        ],
                    })
    except (ValueError, IndexError) as e:
        msg = f"Invalid scenario definition: {e}"
        raise ValueError(msg) from e

    try:
        return ScenarioInput.model_validate({"scenario_definitions": scenario_defs})
    except ValidationError as e:
        msg = f"Invalid scenario definition:\n{e}"
        raise ValueError(msg) from e


def load_scenario_definition(path: Path) -> ScenarioInput:
    """Load and validate a scenario definition CSV file.

    Args:
        path: Path to the CSV file.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file is not ``.csv`` or its contents fail schema validation.
    """
    if path.suffix.lower() != ".csv":
        msg = f"Input file must be a CSV file (.csv), got: {path.suffix or '(no extension)'}"
        raise ValueError(msg)
    if not path.exists():
        msg = f"Input file not found: {path}"
        raise FileNotFoundError(msg)

    return _parse_scenario_csv(path)
