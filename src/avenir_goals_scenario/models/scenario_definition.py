from typing import Annotated, Any, Literal, Self

import numpy as np
from pydantic import AliasChoices, BaseModel, ConfigDict, Field, model_validator


class NormalDistParameters(BaseModel):
    """Parameters for a normal distribution.

    Sampling draws from N(mean, sd), optionally clamped and rounded to int.
    """

    model_config = ConfigDict(extra="forbid")

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


_YEAR_MIN: int = 1970
_PROPORTION_MIN: float = 0.0
_PROPORTION_MAX: float = 1.0


def _apply_year_constraint(dist: NormalDistParameters) -> NormalDistParameters:
    return dist.model_copy(update={"integer": True, "min_value": _YEAR_MIN})


def _apply_proportion_defaults(dist: NormalDistParameters) -> NormalDistParameters:
    changes: dict[str, float] = {}
    if dist.min_value is None:
        changes["min_value"] = _PROPORTION_MIN
    if dist.max_value is None:
        changes["max_value"] = _PROPORTION_MAX
    return dist.model_copy(update=changes) if changes else dist


# ---------------------------------------------------------------------------
# Target types
# ---------------------------------------------------------------------------

RiskGroupNames = Literal[
    "Low risk heterosexual",
    "Medium risk heterosexual",
    "High risk heterosexual",
    "People who inject drugs",
    "Men who have sex with men",
]
RiskGroupAndPlhivNames = Literal[RiskGroupNames, "PLHIV"]

SexName = Literal["Male", "Female", "Both"]


class PrepTarget(BaseModel):
    model_config = ConfigDict(extra="forbid")

    risk_group: RiskGroupNames
    sex: SexName

    @model_validator(mode="after")
    def _validate_msm_sex(self) -> Self:
        if self.risk_group == "Men who have sex with men" and self.sex == "Female":
            msg = "Risk group 'Men who have sex with men' cannot have sex='Female'."
            raise ValueError(msg)
        return self


class VaccineCureTarget(BaseModel):
    """Target population for vaccine or cure interventions.

    Either targets all PLHIV (risk_group="PLHIV", sex="Both" or None) or a
    specific risk group with the standard MSM sex restriction.
    """

    model_config = ConfigDict(extra="forbid")

    risk_group: RiskGroupAndPlhivNames
    sex: SexName | None = None

    @model_validator(mode="after")
    def _validate(self) -> Self:
        if self.risk_group == "PLHIV":
            if self.sex not in (None, "Both"):
                msg = "PLHIV target must have sex='Both' or sex=None (not 'Male' or 'Female')."
                raise ValueError(msg)
        else:
            if self.risk_group == "Men who have sex with men" and self.sex == "Female":
                msg = "Risk group 'Men who have sex with men' cannot have sex='Female'."
                raise ValueError(msg)
        return self


class LongActingTreatmentTarget(BaseModel):
    model_config = ConfigDict(extra="forbid")

    risk_group: Literal[
        "Key populations",
        "General population",
        "Medium risk populations",
        "Not sexually active",
    ]
    sex: SexName | None = None


class AdultARTTarget(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sex: SexName


# ---------------------------------------------------------------------------
# Parameter models
# ---------------------------------------------------------------------------


class PrepParameters(BaseModel):
    model_config = ConfigDict(extra="forbid")

    efficacy: NormalDistParameters
    adherence: NormalDistParameters
    target_coverage: NormalDistParameters
    target_year: NormalDistParameters

    @model_validator(mode="after")
    def _apply_constraints(self) -> Self:
        self.efficacy = _apply_proportion_defaults(self.efficacy)
        self.adherence = _apply_proportion_defaults(self.adherence)
        self.target_coverage = _apply_proportion_defaults(self.target_coverage)
        self.target_year = _apply_year_constraint(self.target_year)
        return self


class VaccineParameters(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target_year: NormalDistParameters
    target_coverage: NormalDistParameters
    reduction_in_susceptibility: NormalDistParameters
    reduction_in_infectiousness: NormalDistParameters
    increase_in_progression_time_to_aids: NormalDistParameters
    vaccine_duration_years: NormalDistParameters
    vaccine_action_type: Literal["Take", "Degree"]
    targeting: Literal["Vaccinate without HIV testing", "Vaccinate only HIV-negative individuals"]

    @model_validator(mode="after")
    def _apply_constraints(self) -> Self:
        self.target_year = _apply_year_constraint(self.target_year)
        self.target_coverage = _apply_proportion_defaults(self.target_coverage)
        self.reduction_in_susceptibility = _apply_proportion_defaults(self.reduction_in_susceptibility)
        self.reduction_in_infectiousness = _apply_proportion_defaults(self.reduction_in_infectiousness)
        self.increase_in_progression_time_to_aids = _apply_proportion_defaults(
            self.increase_in_progression_time_to_aids
        )
        return self


class CureParameters(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target_year: NormalDistParameters
    target_coverage: NormalDistParameters
    efficacy: NormalDistParameters
    duration_of_cure: NormalDistParameters

    @model_validator(mode="after")
    def _apply_constraints(self) -> Self:
        self.target_year = _apply_year_constraint(self.target_year)
        self.target_coverage = _apply_proportion_defaults(self.target_coverage)
        self.efficacy = _apply_proportion_defaults(self.efficacy)
        return self


class AHDTreatmentParameters(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target_year: NormalDistParameters
    target_coverage: NormalDistParameters
    reduction_in_mortality: NormalDistParameters

    @model_validator(mode="after")
    def _apply_constraints(self) -> Self:
        self.target_year = _apply_year_constraint(self.target_year)
        self.target_coverage = _apply_proportion_defaults(self.target_coverage)
        self.reduction_in_mortality = _apply_proportion_defaults(self.reduction_in_mortality)
        return self


class POCTestParameters(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target_year: NormalDistParameters
    target_coverage: NormalDistParameters
    effect: NormalDistParameters

    @model_validator(mode="after")
    def _apply_constraints(self) -> Self:
        self.target_year = _apply_year_constraint(self.target_year)
        self.target_coverage = _apply_proportion_defaults(self.target_coverage)
        self.effect = _apply_proportion_defaults(self.effect)
        return self


class LongActingTreatmentParameters(BaseModel):
    model_config = ConfigDict(extra="forbid")

    interruption_rate_reduction: NormalDistParameters
    viral_load_suppression_ratio: NormalDistParameters

    @model_validator(mode="after")
    def _apply_constraints(self) -> Self:
        self.interruption_rate_reduction = _apply_proportion_defaults(self.interruption_rate_reduction)
        self.viral_load_suppression_ratio = _apply_proportion_defaults(self.viral_load_suppression_ratio)
        return self


class AdultARTParameters(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target_coverage: NormalDistParameters
    target_year: NormalDistParameters

    @model_validator(mode="after")
    def _apply_constraints(self) -> Self:
        self.target_coverage = _apply_proportion_defaults(self.target_coverage)
        self.target_year = _apply_year_constraint(self.target_year)
        return self


# ---------------------------------------------------------------------------
# Intervention definition models (discriminated on product)
# ---------------------------------------------------------------------------

PrepProduct = Literal[
    "Daily PrEP",
    "One month pill for PrEP",
    "One month injectable PrEP",
    "Two month injectable PrEP",
    "Six month injectable PrEP",
    "Oral PrEP plus contraceptive",
    "Ring PrEP",
    "Implantable PrEP",
    "bNABs",
    "PEP",
]


class PrepInterventionDef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    product: PrepProduct
    targets: list[PrepTarget] = Field(min_length=1)
    parameters: PrepParameters


class VaccineInterventionDef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    product: Literal["Vaccine"]
    targets: list[VaccineCureTarget] = Field(min_length=1)
    parameters: VaccineParameters


class CureInterventionDef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    product: Literal["Cure"]
    targets: list[VaccineCureTarget] = Field(min_length=1)
    parameters: CureParameters


class AHDTreatmentDef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    product: Literal["AHD treatment"]
    parameters: AHDTreatmentParameters


class POCViralLoadTestDef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    product: Literal["Point of care viral load test"]
    parameters: POCTestParameters


class POCCD4TestDef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    product: Literal["Point of care CD4 test"]
    parameters: POCTestParameters


class LongActingTreatmentDef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    product: Literal["Long-acting treatment"]
    targets: list[LongActingTreatmentTarget] = Field(min_length=1)
    parameters: LongActingTreatmentParameters


class AdultARTInterventionDef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    product: Literal["Adult ART"]
    targets: list[AdultARTTarget] = Field(min_length=1)
    parameters: AdultARTParameters


AnyInterventionDef = Annotated[
    PrepInterventionDef
    | VaccineInterventionDef
    | CureInterventionDef
    | AHDTreatmentDef
    | POCViralLoadTestDef
    | POCCD4TestDef
    | LongActingTreatmentDef
    | AdultARTInterventionDef,
    Field(discriminator="product"),
]


# ---------------------------------------------------------------------------
# Scenario definition models
# ---------------------------------------------------------------------------


def _intervention_keys(iv: "AnyInterventionDef") -> list[tuple]:
    """Return the uniqueness keys for *iv* used to detect duplicate interventions."""
    if isinstance(iv, (PrepInterventionDef, VaccineInterventionDef, CureInterventionDef, LongActingTreatmentDef)):
        return [(iv.product, t.risk_group, t.sex) for t in iv.targets]
    if isinstance(iv, AdultARTInterventionDef):
        return [(iv.product, t.sex) for t in iv.targets]
    return [(iv.product,)]


class SingleScenarioDef(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: str
    pjnz_names: list[str] | None = Field(default=None, validation_alias=AliasChoices("pjnz_names", "pjnz"))
    interventions: list[AnyInterventionDef] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def _reject_combines(cls, data: Any) -> Any:
        if isinstance(data, dict) and "combines" in data:
            msg = "SingleScenarioDef does not accept 'combines'"
            raise ValueError(msg)
        return data

    @model_validator(mode="after")
    def _validate_unique_products(self) -> Self:
        seen: set[tuple] = set()
        for iv in self.interventions:
            for key in _intervention_keys(iv):
                if key in seen:
                    if len(key) == 1:
                        msg = f"Interventions within a scenario contain duplicate product {key[0]!r}."
                    elif len(key) == 2:
                        msg = f"Interventions within a scenario contain duplicate (product, sex): {key[0]!r} / {key[1]!r}."
                    else:
                        msg = f"Interventions within a scenario contain duplicate (product, risk_group, sex): {key[0]!r} / {key[1]!r} / {key[2]!r}."
                    raise ValueError(msg)
                seen.add(key)
        return self


class CombinedScenarioDef(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: str
    pjnz_names: list[str] | None = Field(default=None, validation_alias=AliasChoices("pjnz_names", "pjnz"))
    combines: list[str] = Field(min_length=2)


class ScenarioDefinition(BaseModel):
    """A scenario with all combined interventions already flattened."""

    id: str
    pjnz_names: list[str] | None = None
    interventions: list[AnyInterventionDef]


class ScenarioInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scenarios: list[CombinedScenarioDef | SingleScenarioDef]

    @staticmethod
    def _check_no_duplicate_keys(scenario_id: str, interventions: list[AnyInterventionDef]) -> None:
        seen: set[tuple] = set()
        for iv in interventions:
            for key in _intervention_keys(iv):
                if key in seen:
                    if len(key) == 1:
                        msg = (
                            f"Scenario {scenario_id} combines scenarios that share product {key[0]!r}. "
                            "Products must be unique within a combined scenario."
                        )
                    elif len(key) == 2:
                        msg = (
                            f"Scenario {scenario_id} combines scenarios with duplicate "
                            f"(product, sex) {key[0]!r} / {key[1]!r}."
                        )
                    else:
                        msg = (
                            f"Scenario {scenario_id} combines scenarios with duplicate "
                            f"(product, population, sex) {key[0]!r} / {key[1]!r} / {key[2]!r}."
                        )
                    raise ValueError(msg)
                seen.add(key)

    @model_validator(mode="after")
    def _validate_combines(self) -> Self:
        all_ids = [s.id for s in self.scenarios]

        if len(all_ids) != len(set(all_ids)):
            msg = "Scenario IDs must be unique."
            raise ValueError(msg)

        single: dict[str, SingleScenarioDef] = {s.id: s for s in self.scenarios if isinstance(s, SingleScenarioDef)}
        combined_ids = {s.id for s in self.scenarios if isinstance(s, CombinedScenarioDef)}

        for s in self.scenarios:
            if not isinstance(s, CombinedScenarioDef):
                continue
            for ref_id in s.combines:
                if ref_id in combined_ids:
                    msg = (
                        f"Scenario {s.id} combines scenario {ref_id}, which is itself a combined "
                        "scenario. Chained combines are not allowed."
                    )
                    raise ValueError(msg)
                if ref_id not in single:
                    msg = f"Scenario {s.id} references unknown scenario id {ref_id} in 'combines'."
                    raise ValueError(msg)
            combined_ivs = [iv for ref_id in s.combines for iv in single[ref_id].interventions]
            self._check_no_duplicate_keys(s.id, combined_ivs)

        return self

    def resolved_scenarios(self) -> list[ScenarioDefinition]:
        """Return all scenarios with combined interventions fully expanded."""
        single: dict[str, SingleScenarioDef] = {s.id: s for s in self.scenarios if isinstance(s, SingleScenarioDef)}
        return [
            ScenarioDefinition(
                id=s.id,
                pjnz_names=s.pjnz_names,
                interventions=[iv for ref_id in s.combines for iv in single[ref_id].interventions]
                if isinstance(s, CombinedScenarioDef)
                else list(s.interventions),
            )
            for s in self.scenarios
        ]
