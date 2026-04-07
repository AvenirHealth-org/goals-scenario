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

_EXPECTED_COLUMNS = frozenset({
    "number",
    "product",
    "efficacy mean",
    "efficacy std",
    "adherence mean",
    "adherence std",
    "target coverage mean",
    "target coverage std",
    "target year mean",
    "target year std",
    "target population",
    "sex",
})


def _validate_csv_columns(fieldnames: list[str]) -> None:
    actual = frozenset(fieldnames)
    unknown = actual - _EXPECTED_COLUMNS
    missing = _EXPECTED_COLUMNS - actual
    errors: list[str] = []
    if unknown:
        errors.append(f"Unknown column(s): {sorted(unknown)}. Expected columns: {sorted(_EXPECTED_COLUMNS)}")
    if missing:
        errors.append(f"Missing column(s): {sorted(missing)}")
    if errors:
        raise ValueError("\n".join(errors))


def _parse_scenario_csv(path: Path) -> ScenarioInput:
    scenario_defs: list[dict] = []
    try:
        with path.open(mode="r", newline="") as f:
            reader = csv.DictReader(f)
            fieldnames = [field.strip().lower() for field in (reader.fieldnames or [])]
            reader.fieldnames = fieldnames
            _validate_csv_columns(fieldnames)
            for row in reader:
                row_id = int(row["number"])
                product = row["product"]
                if _COMBINED_PATTERN.match(product):
                    combines = [int(x) for x in product.split("+")]
                    scenario_defs.append({"id": row_id, "combines": combines})
                else:
                    scenario_defs.append({
                        "id": row_id,
                        "interventions": [
                            {
                                "product": product,
                                "target_population": [row["target population"]],
                                "sex": row["sex"],
                                "parameters": {
                                    "efficacy": {"mean": float(row["efficacy mean"]), "sd": float(row["efficacy std"])},
                                    "adherence": {
                                        "mean": float(row["adherence mean"]),
                                        "sd": float(row["adherence std"]),
                                    },
                                    "target_coverage": {
                                        "mean": float(row["target coverage mean"]),
                                        "sd": float(row["target coverage std"]),
                                    },
                                    "target_year": {
                                        "mean": float(row["target year mean"]),
                                        "sd": float(row["target year std"]),
                                    },
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
