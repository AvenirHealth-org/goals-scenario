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
                        targets=iv.targets,
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

# Columns that must be identical across all rows sharing the same scenario ID.
_SHARED_ID_FIXED_COLUMNS = (
    "product",
    "efficacy mean",
    "efficacy std",
    "adherence mean",
    "adherence std",
    "target coverage mean",
    "target coverage std",
    "target year mean",
    "target year std",
)


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


def _validate_consistent_rows(scenario_id: int, rows: list[dict]) -> None:
    if len(rows) == 1:
        return
    reference = {col: rows[0][col] for col in _SHARED_ID_FIXED_COLUMNS}
    for i, row in enumerate(rows[1:], start=2):
        for col in _SHARED_ID_FIXED_COLUMNS:
            if row[col] != reference[col]:
                msg = (
                    f"Scenario {scenario_id}: row {i} has {col!r} = {row[col]!r} "
                    f"but row 1 has {reference[col]!r}. They must be identical."
                )
                raise ValueError(msg)


def _parse_scenario_csv(path: Path) -> ScenarioInput:
    groups: dict[int, list[dict]] = {}
    try:
        with path.open(mode="r", newline="") as f:
            reader = csv.DictReader(f)
            fieldnames = [field.strip().lower() for field in (reader.fieldnames or [])]
            reader.fieldnames = fieldnames
            _validate_csv_columns(fieldnames)
            for raw_row in reader:
                row = {k: v.strip() for k, v in raw_row.items()}
                scenario_id = int(row["number"])
                if scenario_id not in groups:
                    groups[scenario_id] = []
                groups[scenario_id].append(row)

        scenario_defs: list[dict] = []
        for scenario_id, rows in groups.items():
            first = rows[0]
            product = first["product"]
            if _COMBINED_PATTERN.match(product):
                combines = [int(x) for x in product.split("+")]
                scenario_defs.append({"id": scenario_id, "combines": combines})
            else:
                _validate_consistent_rows(scenario_id, rows)
                scenario_defs.append({
                    "id": scenario_id,
                    "interventions": [
                        {
                            "product": product,
                            "targets": [{"population": r["target population"], "sex": r["sex"]} for r in rows],
                            "parameters": {
                                "efficacy": {"mean": float(first["efficacy mean"]), "sd": float(first["efficacy std"])},
                                "adherence": {
                                    "mean": float(first["adherence mean"]),
                                    "sd": float(first["adherence std"]),
                                },
                                "target_coverage": {
                                    "mean": float(first["target coverage mean"]),
                                    "sd": float(first["target coverage std"]),
                                },
                                "target_year": {
                                    "mean": float(first["target year mean"]),
                                    "sd": float(first["target year std"]),
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
