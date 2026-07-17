from pydantic import BaseModel, ConfigDict, RootModel


class TargetCoverage(BaseModel):
    sex: str | None
    risk_group: str | None
    # A single sampled coverage, or an explicit per-year trajectory passed through
    # from the definition without drawing.
    coverage: float | list[float]


class InterventionOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    product: str


class InterventionSimulation(RootModel[dict[str, float | int | str | list[float] | list[TargetCoverage]]]):
    """Sampled parameter values for one intervention in one simulation.

    Values are scalars for most parameters; ``list[float]`` is a per-year coverage
    trajectory (target-less products), and ``list[TargetCoverage]`` carries the
    per-target coverages (which may themselves be scalar or per-year).
    """


class ScenarioSimulation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    pjnz_names: list[str] | None = None
    interventions: list[InterventionOut]
    simulations: list[dict[str, InterventionSimulation]]


class ScenarioSimulations(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scenarios: list[ScenarioSimulation]
