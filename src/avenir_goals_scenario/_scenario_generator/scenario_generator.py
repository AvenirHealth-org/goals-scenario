import re
from pathlib import Path

import numpy as np
from pydantic import ValidationError

from avenir_goals_scenario.models.scenario_definition import NormalDistParameters, ScenarioInput
from avenir_goals_scenario.models.scenario_simulations import (
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


_TARGET_YEAR_PARAM = "target_year"


def _sample_param(
    name: str, dist: NormalDistParameters, rng: np.random.Generator, base_year: int | None
) -> float | int:
    """Sample one parameter, applying base_year floor to target_year draws."""
    if name == _TARGET_YEAR_PARAM and base_year is not None:
        current_min = dist.min_value
        effective_min = max(current_min, base_year) if current_min is not None else base_year
        dist = dist.model_copy(update={"min_value": effective_min})
    return dist.sample(rng)


def _sample_parameters(params_model, rng: np.random.Generator, base_year: int | None) -> dict:
    """Sample all parameters from a typed parameters model.

    NormalDistParameters fields are sampled; other fields (e.g. str categoricals) are
    passed through unchanged.
    """
    result = {}
    for field_name, field_value in params_model:
        if isinstance(field_value, NormalDistParameters):
            result[field_name] = _sample_param(field_name, field_value, rng, base_year)
        else:
            result[field_name] = field_value
    return result


def _sample_target_coverages(iv, rng: np.random.Generator) -> dict:
    """Sample per-target coverages, returning {"target_coverages": [...]}."""
    coverages = [
        {
            "sex": target.sex,
            "risk_group": getattr(target, "risk_group", None),
            "coverage": target.target_coverage.sample(rng),
        }
        for target in getattr(iv, "targets", [])
        if hasattr(target, "target_coverage")
    ]
    return {"target_coverages": coverages} if coverages else {}


def gen_simulations(
    definition: ScenarioInput,
    n_simulations: int = 100,
    rng: np.random.Generator | None = None,
    base_year: int | None = None,
) -> ScenarioSimulations:
    """Generate sampled simulations from a validated :class:`ScenarioInput`.

    Args:
        definition: Validated scenario definition.
        n_simulations: Number of simulations per scenario.
        rng: Optional seeded RNG for reproducibility; a fresh one is created if omitted.
            For parallel use, spawn independent child RNGs with ``rng.spawn(n)`` or
            ``np.random.SeedSequence(seed).spawn(n)`` before distributing work.
        base_year: If provided, used as the minimum value for ``target_year`` draws.
            Values below ``base_year`` are clamped up to it.

    Returns:
        A :class:`ScenarioSimulations` containing all scenarios and their simulations.
    """
    if rng is None:
        rng = np.random.default_rng()

    return ScenarioSimulations(
        scenarios=[
            ScenarioSimulation(
                id=scenario.id,
                pjnz_names=scenario.pjnz_names,
                interventions=[
                    InterventionOut(
                        id=_product_to_id(iv.product),
                        product=iv.product,
                    )
                    for iv in scenario.interventions
                ],
                simulations=[
                    {
                        _product_to_id(iv.product): InterventionSimulation(
                            _sample_parameters(iv.parameters, rng, base_year) | _sample_target_coverages(iv, rng)
                        )
                        for iv in scenario.interventions
                    }
                    for _ in range(n_simulations)
                ],
            )
            for scenario in definition.resolved_scenarios()
        ]
    )


_MAX_VALIDATION_ERRORS = 5


def _parse_scenario_json(path: Path) -> ScenarioInput:
    try:
        return ScenarioInput.model_validate_json(path.read_text())
    except ValidationError as e:
        errors = e.errors(include_url=False)
        shown = errors[:_MAX_VALIDATION_ERRORS]
        lines = [f"  {' -> '.join(str(loc) for loc in err['loc'])}: {err['msg']}" for err in shown]
        if len(errors) > _MAX_VALIDATION_ERRORS:
            lines.append(f"  ... and {len(errors) - _MAX_VALIDATION_ERRORS} more errors")
        msg = f"Invalid scenario definition ({len(errors)} errors):\n" + "\n".join(lines)
        raise ValueError(msg) from e


def load_scenario_definition(path: Path) -> ScenarioInput:
    """Load and validate a scenario definition JSON file.

    Args:
        path: Path to a ``.json`` scenario definition file.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file extension is not ``.json`` or the contents fail validation.
    """
    if not path.exists():
        msg = f"Input file not found: {path}"
        raise FileNotFoundError(msg)

    if path.suffix.lower() != ".json":
        msg = f"Input file must be a .json file, got: {path.suffix or '(no extension)'}"
        raise ValueError(msg)

    return _parse_scenario_json(path)
