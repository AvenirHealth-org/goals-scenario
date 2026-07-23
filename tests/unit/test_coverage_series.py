"""Tests for per-year coverage / initiation-rate arrays.

Covers the four layers the feature touches: schema validation, the pass-through
draw, the verbatim apply into leapfrog arrays, and the runner's pre-flight length
check against each PJNZ's projection end year.
"""

from pathlib import Path
from typing import cast

import numpy as np
import pytest
from pydantic import ValidationError
from SpectrumCommon.Const.RN import RN_HRH

from avenir_goals_scenario._runner.simulation import _apply_series, _ramp_to_target, apply_simulation
from avenir_goals_scenario._scenario_generator.scenario_generator import gen_simulations
from avenir_goals_scenario.models import InterventionOut, InterventionSimulation, TargetCoverage
from avenir_goals_scenario.models.scenario_definition import (
    AdultARTInterventionDef,
    AHDTreatmentDef,
    ScenarioInput,
    SingleScenarioDef,
)
from avenir_goals_scenario.models.scenario_simulations import (
    ScenarioSimulation,
    ScenarioSimulations,
)
from avenir_goals_scenario.runner import _validate_series_lengths


def _scenario(interventions: list[dict]) -> dict:
    return {"scenarios": [{"id": "1", "interventions": interventions}]}


def _adult_art(cov, parameters: dict | None = None) -> dict:
    return {
        "product": "Adult ART",
        "targets": [{"sex": "Both", "target_coverage": cov}],
        "parameters": parameters or {},
    }


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------


def test_array_coverage_accepted_without_target_year():
    si = ScenarioInput.model_validate(_scenario([_adult_art([0.1, 0.2, 0.3])]))
    scenario = cast(SingleScenarioDef, si.scenarios[0])
    iv = cast(AdultARTInterventionDef, scenario.interventions[0])
    assert iv.targets[0].target_coverage == [0.1, 0.2, 0.3]
    assert iv.parameters.target_year is None


def test_array_element_out_of_range_rejected():
    with pytest.raises(ValidationError):
        ScenarioInput.model_validate(_scenario([_adult_art([0.1, 1.5])]))


def test_empty_array_rejected():
    with pytest.raises(ValidationError):
        ScenarioInput.model_validate(_scenario([_adult_art([])]))


def test_distribution_without_target_year_rejected():
    with pytest.raises(ValidationError, match="target_year' is required"):
        ScenarioInput.model_validate(_scenario([_adult_art({"mean": 0.8, "sd": 0.05})]))


def test_target_year_with_all_array_intervention_accepted_and_ignored():
    si = ScenarioInput.model_validate(_scenario([_adult_art([0.1, 0.2], {"target_year": {"mean": 2030, "sd": 1}})]))
    # Accepted (no error) — target_year is retained on the model but ignored downstream.
    scenario = cast(SingleScenarioDef, si.scenarios[0])
    assert scenario.interventions[0].parameters.target_year is not None


def test_mixed_array_and_distribution_targets_accepted():
    mixed = {
        "product": "Oral PrEP (daily)",
        "targets": [
            {"risk_group": "High risk heterosexual", "sex": "Female", "target_coverage": [0.1, 0.2, 0.3]},
            {"risk_group": "Men who have sex with men", "sex": "Male", "target_coverage": {"mean": 0.3, "sd": 0.05}},
        ],
        "parameters": {
            "efficacy": {"mean": 0.9, "sd": 0.02},
            "adherence": {"mean": 0.85, "sd": 0.05},
            "target_year": {"mean": 2030, "sd": 1},
        },
    }
    ScenarioInput.model_validate(_scenario([mixed]))


def test_target_less_product_array_coverage_accepted():
    ahd = {
        "product": "AHD treatment",
        "parameters": {"target_coverage": [0.1, 0.2, 0.3], "reduction_in_mortality": {"mean": 0.4, "sd": 0.0}},
    }
    si = ScenarioInput.model_validate(_scenario([ahd]))
    scenario = cast(SingleScenarioDef, si.scenarios[0])
    iv = cast(AHDTreatmentDef, scenario.interventions[0])
    assert iv.parameters.target_coverage == [0.1, 0.2, 0.3]


# ---------------------------------------------------------------------------
# Draw pass-through
# ---------------------------------------------------------------------------


def test_draw_passes_array_through_and_samples_distribution():
    mixed = {
        "product": "Oral PrEP (daily)",
        "targets": [
            {"risk_group": "High risk heterosexual", "sex": "Female", "target_coverage": [0.1, 0.2, 0.3, 0.4]},
            {"risk_group": "Men who have sex with men", "sex": "Male", "target_coverage": {"mean": 0.3, "sd": 0.05}},
        ],
        "parameters": {
            "efficacy": {"mean": 0.9, "sd": 0.02},
            "adherence": {"mean": 0.85, "sd": 0.05},
            "target_year": {"mean": 2030, "sd": 1},
        },
    }
    si = ScenarioInput.model_validate(_scenario([mixed]))
    sims = gen_simulations(si, n_simulations=3, rng=np.random.default_rng(0), base_year=2025)

    for draw in sims.scenarios[0].simulations:
        target_coverages = cast(list[TargetCoverage], draw["oral_prep_daily"].root["target_coverages"])
        covs = {(tc.risk_group, tc.sex): tc.coverage for tc in target_coverages}
        # Array passed through unchanged for every simulation (no drawing).
        assert covs[("High risk heterosexual", "Female")] == [0.1, 0.2, 0.3, 0.4]
        # Distribution sampled to a scalar.
        assert isinstance(covs[("Men who have sex with men", "Male")], float)


def test_draw_omits_target_year_for_all_array_intervention():
    si = ScenarioInput.model_validate(_scenario([_adult_art([0.1, 0.2, 0.3])]))
    sims = gen_simulations(si, n_simulations=1, rng=np.random.default_rng(0), base_year=2025)
    root = sims.scenarios[0].simulations[0]["adult_art"].root
    assert "target_year" not in root


# ---------------------------------------------------------------------------
# Apply
# ---------------------------------------------------------------------------


def test_apply_series_writes_verbatim():
    series = np.zeros(10)
    _apply_series(series, 4, [0.1, 0.2, 0.3, 0.4, 0.5, 0.6])
    assert np.allclose(series[4:], [0.1, 0.2, 0.3, 0.4, 0.5, 0.6])
    assert np.allclose(series[:4], 0.0)


def test_apply_series_wrong_length_raises():
    with pytest.raises(ValueError, match="Per-year coverage array has 3 value"):
        _apply_series(np.zeros(10), 4, [0.1, 0.2, 0.3])


def test_ramp_to_target_list_ignores_target_idx():
    series = np.zeros(6)
    _ramp_to_target(series, 2, target_idx=-1, target=[0.7, 0.8, 0.9, 1.0])
    assert np.allclose(series[2:], [0.7, 0.8, 0.9, 1.0])


def test_ramp_to_target_scalar_still_linear():
    series = np.zeros(6)
    _ramp_to_target(series, 2, target_idx=5, target=1.0)
    # Linear from base_idx=2 to target_idx=5 (4 points), held at target after.
    assert np.allclose(series[2:], [0.0, 1 / 3, 2 / 3, 1.0])


def test_apply_adult_art_array_written_verbatim():
    start, end, base_year = 2020, 2029, 2025
    n = end - start + 1
    base_idx = base_year - start
    lp = {
        "projection_start_year": start,
        "projection_end_year": end,
        "art15plus_num": np.zeros((2, n)),
        "art15plus_isperc": np.zeros((2, n)),
    }
    ivs = [InterventionOut(id="adult_art", product="Adult ART")]
    sim = {
        "adult_art": InterventionSimulation({
            "target_coverages": [TargetCoverage(sex="Both", risk_group=None, coverage=[0.5, 0.6, 0.7, 0.8, 0.9])]
        })
    }
    apply_simulation(lp, ivs, sim, base_year)
    for sex_idx in (0, 1):
        assert np.allclose(lp["art15plus_num"][sex_idx, base_idx:], [0.5, 0.6, 0.7, 0.8, 0.9])
        assert np.allclose(lp["art15plus_num"][sex_idx, :base_idx], 0.0)
        assert np.allclose(lp["art15plus_isperc"][sex_idx, base_idx:], 1)


def test_apply_prep_mixes_array_and_ramp():
    start, end, base_year = 2020, 2029, 2025
    n = end - start + 1
    base_idx = base_year - start
    lp = {
        "projection_start_year": start,
        "projection_end_year": end,
        "prep_cov": np.zeros((2, 9, n)),
        "prep_method_mix": np.zeros((2, 9, 10, n)),
        "prep_effectiveness": np.zeros((10, 8)),
    }
    ivs = [InterventionOut(id="oral_prep_daily", product="Oral PrEP (daily)")]
    arr = [0.1, 0.2, 0.3, 0.4, 0.5]
    sim = {
        "oral_prep_daily": InterventionSimulation({
            "efficacy": 0.9,
            "adherence": 0.85,
            "target_year": 2029,
            "target_coverages": [
                TargetCoverage(sex="Female", risk_group="High risk heterosexual", coverage=arr),
                TargetCoverage(sex="Male", risk_group="Men who have sex with men", coverage=1.0),
            ],
        })
    }
    apply_simulation(lp, ivs, sim, base_year)
    assert np.allclose(lp["prep_cov"][1, RN_HRH, base_idx:], arr)


# ---------------------------------------------------------------------------
# Runner pre-flight length validation
# ---------------------------------------------------------------------------


def _ahd_simulations(coverage) -> ScenarioSimulations:
    return ScenarioSimulations(
        scenarios=[
            ScenarioSimulation(
                id="1",
                interventions=[InterventionOut(id="ahd_treatment", product="AHD treatment")],
                simulations=[
                    {
                        "ahd_treatment": InterventionSimulation({
                            "target_coverage": coverage,
                            "reduction_in_mortality": 0.4,
                        })
                    }
                ],
            )
        ]
    )


def test_validate_series_lengths_passes_on_correct_length():
    pjnz = Path("Zimbabwe.PJNZ")
    # base_year 2045, end 2050 -> expected length 6.
    _validate_series_lengths([pjnz], {pjnz: 2050}, _ahd_simulations([0.1, 0.2, 0.3, 0.4, 0.5, 0.6]), 2045, None)


def test_validate_series_lengths_raises_on_wrong_length():
    pjnz = Path("Zimbabwe.PJNZ")
    with pytest.raises(ValueError, match=r"has 5 value.*needs 6"):
        _validate_series_lengths([pjnz], {pjnz: 2050}, _ahd_simulations([0.1, 0.2, 0.3, 0.4, 0.5]), 2045, None)


def test_validate_series_lengths_targeted_coverage_array():
    pjnz = Path("Zimbabwe.PJNZ")
    sims = ScenarioSimulations(
        scenarios=[
            ScenarioSimulation(
                id="1",
                interventions=[InterventionOut(id="adult_art", product="Adult ART")],
                simulations=[
                    {
                        "adult_art": InterventionSimulation({
                            "target_coverages": [TargetCoverage(sex="Both", risk_group=None, coverage=[0.1, 0.2])]
                        })
                    }
                ],
            )
        ]
    )
    with pytest.raises(ValueError, match="needs 6"):
        _validate_series_lengths([pjnz], {pjnz: 2050}, sims, 2045, None)
