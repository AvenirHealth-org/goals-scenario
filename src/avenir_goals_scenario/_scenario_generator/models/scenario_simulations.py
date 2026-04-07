from __future__ import annotations

from pydantic import BaseModel, ConfigDict, RootModel


class InterventionOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    product: str
    target_population: list[str]
    sex: str


class InterventionSimulation(RootModel[dict[str, float | int]]):
    """Sampled parameter values for one intervention in one simulation."""


class ScenarioSimulation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scenario_id: int
    interventions: list[InterventionOut]
    simulations: list[dict[str, InterventionSimulation]]


class ScenarioSimulations(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scenarios: list[ScenarioSimulation]
