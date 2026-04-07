from __future__ import annotations

from typing import Any, Literal

import numpy as np
from pydantic import BaseModel, Field, field_validator, model_validator


class NormalDistParameters(BaseModel):
    """Parameters for a normal distribution.

    Sampling draws from N(mean, sd), optionally clamped and rounded to int.

    To add a new distribution type (e.g. Uniform):
      1. Define a new model with a ``distribution: Literal["uniform"]`` field and a ``sample()`` method.
      2. Update the ``ParameterDist`` type alias to a discriminated union:
         ``Annotated[NormalDistParameters | UniformDistParameters, Field(discriminator="distribution")]``
      3. Update ``InterventionDef._apply_parameter_constraints`` if new constraints are needed.
    """

    distribution: Literal["normal"] = "normal"
    mean: float
    sd: float = Field(ge=0)
    integer: bool = False
    min_value: float | None = None
    max_value: float | None = None

    def sample(self, rng: np.random.Generator) -> float | int:
        """Draw one sample from this distribution."""
        raw = rng.normal(self.mean, self.sd)
        if self.min_value is not None:
            raw = max(raw, float(self.min_value))
        if self.max_value is not None:
            raw = min(raw, float(self.max_value))
        if self.integer:
            return round(raw)
        return float(raw)


# Extend this union as more distribution types are added.
ParameterDist = NormalDistParameters

# Parameters that produce integer outputs.
_TARGET_YEAR_PARAM_NAME = "target_year"
# Floor applied to target_year samples.
_YEAR_MIN: int = 1970
# Default bounds for proportion parameters.
_PROPORTION_MIN: float = 0.0
_PROPORTION_MAX: float = 1.0


class InterventionDef(BaseModel):
    product: str
    target_population: list[str]
    sex: str
    parameters: dict[str, ParameterDist]

    @field_validator("target_population", mode="before")
    @classmethod
    def _convert_pop_to_array(cls, v: Any) -> list[str]:
        if isinstance(v, str):
            return [v]
        else:
            return v

    @model_validator(mode="after")
    def _apply_parameter_constraints(self) -> InterventionDef:
        """Set integer/bounds constraints based on parameter names."""
        updated: dict[str, ParameterDist] = {}
        for name, dist in self.parameters.items():
            if name is _TARGET_YEAR_PARAM_NAME:
                updated[name] = dist.model_copy(update={"integer": True, "min_value": _YEAR_MIN})
            else:
                changes: dict[str, float] = {}
                if dist.min_value is None:
                    changes["min_value"] = _PROPORTION_MIN
                if dist.max_value is None:
                    changes["max_value"] = _PROPORTION_MAX
                if changes:
                    updated[name] = dist.model_copy(update=changes)
        if updated:
            self.parameters = {**self.parameters, **updated}
        return self


class SingleScenarioDef(BaseModel):
    id: int
    interventions: list[InterventionDef] = Field(min_length=1)


class CombinedScenarioDef(BaseModel):
    id: int
    combines: list[int] = Field(min_length=2)


class ScenarioDefinition(BaseModel):
    """A scenario with all combined interventions already flattened."""

    id: int
    interventions: list[InterventionDef]


class ScenarioInput(BaseModel):
    scenario_definitions: list[CombinedScenarioDef | SingleScenarioDef]

    @model_validator(mode="after")
    def _validate_combines(self) -> ScenarioInput:
        all_ids = [s.id for s in self.scenario_definitions]

        if len(all_ids) != len(set(all_ids)):
            msg = "Scenario IDs must be unique."
            raise ValueError(msg)

        single_ids = {s.id for s in self.scenario_definitions if isinstance(s, SingleScenarioDef)}
        combined_ids = {s.id for s in self.scenario_definitions if isinstance(s, CombinedScenarioDef)}

        for s in self.scenario_definitions:
            if not isinstance(s, CombinedScenarioDef):
                continue
            for ref_id in s.combines:
                if ref_id in combined_ids:
                    msg = (
                        f"Scenario {s.id} combines scenario {ref_id}, which is itself a combined "
                        "scenario. Chained combines are not allowed."
                    )
                    raise ValueError(msg)
                if ref_id not in single_ids:
                    msg = f"Scenario {s.id} references unknown scenario id {ref_id} in 'combines'."
                    raise ValueError(msg)

        return self

    def resolved_scenarios(self) -> list[ScenarioDefinition]:
        """Return all scenarios with combined interventions fully expanded."""
        single: dict[int, SingleScenarioDef] = {
            s.id: s for s in self.scenario_definitions if isinstance(s, SingleScenarioDef)
        }
        return [
            ScenarioDefinition(
                id=s.id,
                interventions=[iv for ref_id in s.combines for iv in single[ref_id].interventions]
                if isinstance(s, CombinedScenarioDef)
                else list(s.interventions),
            )
            for s in self.scenario_definitions
        ]
