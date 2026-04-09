from pathlib import Path
from unittest.mock import patch

import h5py
import numpy as np
import pytest

from avenir_goals_scenario._runner.output import write_scenario_results
from avenir_goals_scenario._runner.pjnz import find_pjnz_files
from avenir_goals_scenario._runner.simulation import _extract_indicators
from avenir_goals_scenario.models import RunConfig, ScenarioSimulations
from avenir_goals_scenario.runner import run_scenario_analysis

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Tag constants from SpectrumCommon — matches what import_pjnz would populate.
_FIRST_YEAR_TAG = "<PJN_FirstYear_V1>"
_FINAL_YEAR_TAG = "<PJN_FinalYear_V1>"

_N_YEARS = 5  # short range for tests: 2020-2024


def _fake_modvars() -> dict:
    return {_FIRST_YEAR_TAG: 2020, _FINAL_YEAR_TAG: 2024}


def _make_simulations_json(tmp_path, scenario_id: int = 1, n_simulations: int = 2) -> Path:
    """Write a minimal ScenarioSimulations JSON and return the path."""
    from avenir_goals_scenario.models import (
        InterventionOut,
        InterventionSimulation,
        PopulationTarget,
        ScenarioSimulation,
    )

    target = PopulationTarget(population="General", sex="Both")
    intervention = InterventionOut(id="daily_prep", product="Daily PrEP", targets=[target])
    sim_params = InterventionSimulation({"efficacy": 0.9, "adherence": 0.8})
    simulation = {"daily_prep": sim_params}

    scenario = ScenarioSimulation(
        scenario_id=scenario_id,
        interventions=[intervention],
        simulations=[simulation] * n_simulations,
    )
    data = ScenarioSimulations(scenarios=[scenario])

    path = tmp_path / "simulations.json"
    path.write_text(data.model_dump_json(indent=2))
    return path


def _make_run_config(tmp_path, pjnz_dir, scenarios_path, indicators=None, base_year=2020) -> RunConfig:
    output_dir = tmp_path / "output"
    output_dir.mkdir(exist_ok=True)
    return RunConfig(
        pjnz_dir=pjnz_dir,
        scenario_path=scenarios_path,
        output_dir=output_dir,
        base_year=base_year,
        output_indicators=indicators or ["PLHIV"],
    )


def _fake_sim_result(indicators: list[str], shape: tuple = (_N_YEARS,)) -> dict[str, np.ndarray]:
    return {ind: np.ones(shape) * (i + 1) for i, ind in enumerate(indicators)}


# ---------------------------------------------------------------------------
# find_pjnz_files (re-exported from runner)
# ---------------------------------------------------------------------------


def test_find_pjnz_files_returns_files(tmp_path):
    (tmp_path / "a.PJNZ").touch()
    (tmp_path / "b.PJNZ").touch()

    result = find_pjnz_files(tmp_path)

    assert len(result) == 2
    assert result[0].name == "a.PJNZ"
    assert result[1].name == "b.PJNZ"


def test_find_pjnz_files_sorted(tmp_path):
    (tmp_path / "z.PJNZ").touch()
    (tmp_path / "a.PJNZ").touch()

    result = find_pjnz_files(tmp_path)

    assert [f.name for f in result] == ["a.PJNZ", "z.PJNZ"]


def test_find_pjnz_files_ignores_other_extensions(tmp_path):
    (tmp_path / "a.PJNZ").touch()
    (tmp_path / "b.csv").touch()
    (tmp_path / "c.zip").touch()

    result = find_pjnz_files(tmp_path)

    assert len(result) == 1


def test_find_pjnz_files_raises_when_empty(tmp_path):
    with pytest.raises(FileNotFoundError, match="No PJNZ files found"):
        find_pjnz_files(tmp_path)


# ---------------------------------------------------------------------------
# _extract_indicators
# ---------------------------------------------------------------------------


def test_extract_indicators_returns_requested_subset():
    output = {k: np.ones(5) for k in ["PLHIV", "New Infections", "Deaths"]}
    result = _extract_indicators(output, ["PLHIV", "Deaths"])
    assert set(result.keys()) == {"PLHIV", "Deaths"}


def test_extract_indicators_preserves_array_shape():
    arr = np.ones((2, 66, 5))  # e.g. sex x age x years
    output = {"p_totpop": arr}
    result = _extract_indicators(output, ["p_totpop"])
    assert result["p_totpop"].shape == (2, 66, 5)


def test_extract_indicators_raises_on_unknown():
    output = {"PLHIV": np.ones(5)}
    with pytest.raises(ValueError, match="not found in Goals output"):
        _extract_indicators(output, ["PLHIV", "Unknown Indicator"])


# ---------------------------------------------------------------------------
# write_scenario_results
# ---------------------------------------------------------------------------


def test_write_scenario_results_creates_h5(tmp_path):
    sim_arrays = {"PLHIV": [np.ones(5), np.ones(5) * 2]}
    path = write_scenario_results(1, "country", sim_arrays, tmp_path)

    assert path == tmp_path / "country" / "scenario_1.h5"
    assert path.exists()


def test_write_scenario_results_dataset_shape(tmp_path):
    n_sims = 3
    sim_arrays = {"PLHIV": [np.ones(5) * i for i in range(n_sims)]}
    path = write_scenario_results(2, "country", sim_arrays, tmp_path)

    with h5py.File(path, "r") as f:
        assert f["PLHIV"].shape == (n_sims, 5)


def test_write_scenario_results_preserves_multidim_shape(tmp_path):
    # Simulate a sex x age x years indicator shape (2, 66, 61)
    indicator_shape = (2, 66, 61)
    n_sims = 4
    sim_arrays = {"p_totpop": [np.ones(indicator_shape) for _ in range(n_sims)]}
    path = write_scenario_results(1, "country", sim_arrays, tmp_path)

    with h5py.File(path, "r") as f:
        assert f["p_totpop"].shape == (n_sims, 2, 66, 61)


def test_write_scenario_results_values(tmp_path):
    sim_arrays = {"PLHIV": [np.array([1.0, 2.0]), np.array([3.0, 4.0])]}
    path = write_scenario_results(1, "country", sim_arrays, tmp_path)

    with h5py.File(path, "r") as f:
        np.testing.assert_array_equal(f["PLHIV"][0], [1.0, 2.0])
        np.testing.assert_array_equal(f["PLHIV"][1], [3.0, 4.0])


def test_write_scenario_results_creates_pjnz_subdir(tmp_path):
    sim_arrays = {"PLHIV": [np.ones(3)]}
    write_scenario_results(1, "my_country", sim_arrays, tmp_path)

    assert (tmp_path / "my_country").is_dir()


# ---------------------------------------------------------------------------
# run_scenario_analysis — integration (external calls mocked)
# ---------------------------------------------------------------------------


def test_run_scenario_analysis_creates_h5_per_pjnz_per_scenario(tmp_path):
    pjnz_dir = tmp_path / "pjnz"
    pjnz_dir.mkdir()
    (pjnz_dir / "country.PJNZ").touch()

    scenarios_path = _make_simulations_json(tmp_path, scenario_id=1, n_simulations=2)
    config = _make_run_config(tmp_path, pjnz_dir, scenarios_path, indicators=["PLHIV"])

    with (
        patch("avenir_goals_scenario.runner.import_pjnz", return_value=_fake_modvars()),
        patch("avenir_goals_scenario.runner.run_simulation", return_value={"PLHIV": np.ones(_N_YEARS)}),
    ):
        run_scenario_analysis(config)

    assert (Path(config.output_dir) / "country" / "scenario_1.h5").exists()


def test_run_scenario_analysis_h5_dataset_shape(tmp_path):
    pjnz_dir = tmp_path / "pjnz"
    pjnz_dir.mkdir()
    (pjnz_dir / "country.PJNZ").touch()

    n_sims = 3
    scenarios_path = _make_simulations_json(tmp_path, scenario_id=1, n_simulations=n_sims)
    config = _make_run_config(tmp_path, pjnz_dir, scenarios_path, indicators=["PLHIV"])

    with (
        patch("avenir_goals_scenario.runner.import_pjnz", return_value=_fake_modvars()),
        patch("avenir_goals_scenario.runner.run_simulation", return_value={"PLHIV": np.ones(_N_YEARS)}),
    ):
        run_scenario_analysis(config)

    with h5py.File(Path(config.output_dir) / "country" / "scenario_1.h5", "r") as f:
        assert f["PLHIV"].shape == (n_sims, _N_YEARS)


def test_run_scenario_analysis_multidim_indicator_preserved(tmp_path):
    pjnz_dir = tmp_path / "pjnz"
    pjnz_dir.mkdir()
    (pjnz_dir / "country.PJNZ").touch()

    scenarios_path = _make_simulations_json(tmp_path, n_simulations=2)
    config = _make_run_config(tmp_path, pjnz_dir, scenarios_path, indicators=["p_totpop"])
    indicator_shape = (2, 66, _N_YEARS)

    with (
        patch("avenir_goals_scenario.runner.import_pjnz", return_value=_fake_modvars()),
        patch("avenir_goals_scenario.runner.run_simulation", return_value={"p_totpop": np.ones(indicator_shape)}),
    ):
        run_scenario_analysis(config)

    with h5py.File(Path(config.output_dir) / "country" / "scenario_1.h5", "r") as f:
        assert f["p_totpop"].shape == (2, 2, 66, _N_YEARS)


def test_run_scenario_analysis_year_range_from_modvars(tmp_path):
    pjnz_dir = tmp_path / "pjnz"
    pjnz_dir.mkdir()
    (pjnz_dir / "country.PJNZ").touch()

    modvars = {_FIRST_YEAR_TAG: 2010, _FINAL_YEAR_TAG: 2012}
    scenarios_path = _make_simulations_json(tmp_path, n_simulations=1)
    config = _make_run_config(tmp_path, pjnz_dir, scenarios_path, indicators=["PLHIV"], base_year=2015)

    with (
        patch("avenir_goals_scenario.runner.import_pjnz", return_value=modvars),
        patch("avenir_goals_scenario.runner.run_simulation", return_value={"PLHIV": np.ones(3)}) as mock_sim,
    ):
        run_scenario_analysis(config)

    # run_simulation(modvars_base, simulation, output_indicators, output_years, ss)
    assert mock_sim.call_args.args[3] == range(2015, 2013)


def test_run_scenario_analysis_multiple_pjnz_creates_separate_dirs(tmp_path):
    pjnz_dir = tmp_path / "pjnz"
    pjnz_dir.mkdir()
    (pjnz_dir / "alpha.PJNZ").touch()
    (pjnz_dir / "beta.PJNZ").touch()

    scenarios_path = _make_simulations_json(tmp_path, n_simulations=1)
    config = _make_run_config(tmp_path, pjnz_dir, scenarios_path, indicators=["PLHIV"])

    with (
        patch("avenir_goals_scenario.runner.import_pjnz", return_value=_fake_modvars()),
        patch("avenir_goals_scenario.runner.run_simulation", return_value={"PLHIV": np.ones(_N_YEARS)}),
    ):
        run_scenario_analysis(config)

    assert (Path(config.output_dir) / "alpha" / "scenario_1.h5").exists()
    assert (Path(config.output_dir) / "beta" / "scenario_1.h5").exists()
