"""Output models for the scenario generator."""

from __future__ import annotations

from pydantic import BaseModel, RootModel


class InterventionOut(BaseModel):
    id: str
    product: str
    target_population: list[str]
    sex: str


class InterventionSimulation(RootModel[dict[str, float | int]]):
    """Sampled parameter values for one intervention in one simulation."""


class ScenarioSimulation(BaseModel):
    scenario_id: int
    interventions: list[InterventionOut]
    simulations: list[dict[str, InterventionSimulation]]


class ScenarioSimulations(BaseModel):
    scenarios: list[ScenarioSimulation]
