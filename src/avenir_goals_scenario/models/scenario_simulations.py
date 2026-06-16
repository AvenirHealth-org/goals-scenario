from pydantic import BaseModel, ConfigDict, RootModel

from avenir_goals_scenario.models.scenario_definition import (
    AdultARTTarget,
    LongActingTreatmentTarget,
    PrepTarget,
    VaccineCureTarget,
)

AnyTarget = PrepTarget | VaccineCureTarget | LongActingTreatmentTarget | AdultARTTarget


class InterventionOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    product: str
    targets: list[AnyTarget] = []


class InterventionSimulation(RootModel[dict[str, float | int | str]]):
    """Sampled parameter values for one intervention in one simulation."""


class ScenarioSimulation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    pjnz_names: list[str] | None = None
    interventions: list[InterventionOut]
    simulations: list[dict[str, InterventionSimulation]]


class ScenarioSimulations(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scenarios: list[ScenarioSimulation]
