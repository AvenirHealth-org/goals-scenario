from pydantic import BaseModel, ConfigDict, RootModel


class TargetCoverage(BaseModel):
    sex: str | None
    risk_group: str | None
    coverage: float


class InterventionOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    product: str


class InterventionSimulation(RootModel[dict[str, float | int | str | list[TargetCoverage]]]):
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
