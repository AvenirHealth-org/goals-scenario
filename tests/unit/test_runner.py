import pickle
from contextlib import ExitStack
from pathlib import Path
from queue import Queue
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from avenir_goals_scenario._runner.pjnz import _import_pjnz_modvars, find_pjnz_files, import_pjnz, modvars_to_numpy
from avenir_goals_scenario._runner.simulation import _extract_indicators, run_simulation
from avenir_goals_scenario.models import RunConfig, ScenarioSimulations
from avenir_goals_scenario.runner import _run_pjnz_scenario, run_scenario_analysis

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_N_YEARS = 5  # short range for tests: 2020-2024


def _fake_modvars() -> dict:
    # Matches the leapfrog params dict returned by import_pjnz.
    return {"projection_end_year": 2024}


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
        # n_workers=1 keeps joblib sequential so unittest.mock patches are visible
        # to the code under test (patches do not propagate across process boundaries).
        n_workers=1,
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
# import_pjnz
# ---------------------------------------------------------------------------


def test_import_pjnz_raises_when_modvars_is_none(tmp_path):
    pjnz_path = tmp_path / "bad.PJNZ"
    pjnz_path.touch()

    with (
        patch("avenir_goals_scenario._runner.pjnz.GB_ImportProjectionFromFile", return_value=(None, None, None, None)),
        pytest.raises(ValueError, match="Failed to import PJNZ file"),
    ):
        import_pjnz(pjnz_path)


# ---------------------------------------------------------------------------
# modvars_to_numpy
# ---------------------------------------------------------------------------


def test_modvars_to_numpy_raises_on_unconvertible_list():
    # A mixed list that can't be cast to float64.
    bad_value = {"modvar1": [1, "not_a_number"]}
    with pytest.raises(ValueError):
        modvars_to_numpy(bad_value)


def test_modvars_to_numpy_list_of_strings_produces_ndarray():
    result = modvars_to_numpy({"modvar1": ["a", "b", "c"]})
    assert isinstance(result["modvar1"], np.ndarray)


def test_modvars_to_numpy_non_list_passthrough():
    in_modvars = {"modvar1": 42, "modvar2": 3.14}
    assert modvars_to_numpy(in_modvars) == in_modvars


# ---------------------------------------------------------------------------
# run_simulation
# ---------------------------------------------------------------------------


def test_run_simulation_calls_run_goals_and_extracts_indicators():
    goals_output = {"PLHIV": np.ones(5), "Deaths": np.ones(5)}
    with patch("avenir_goals_scenario._runner.simulation.run_goals", return_value=goals_output) as mock_goals:
        result = run_simulation({}, {}, ["PLHIV"], range(2020, 2025))

    mock_goals.assert_called_once_with({}, range(2020, 2025))
    assert list(result.keys()) == ["PLHIV"]


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
# run_scenario_analysis - integration (external calls mocked)
# ---------------------------------------------------------------------------

_P_HIVPOP_SHAPE = (81, 2, _N_YEARS)
_SIM_RESULT = {"p_hivpop": np.asfortranarray(np.ones(_P_HIVPOP_SHAPE))}


def _integration_patches(sim_result: dict) -> ExitStack:
    """Return a context manager with the patches needed for runner integration tests."""
    stack = ExitStack()
    stack.enter_context(patch("avenir_goals_scenario.runner.import_pjnz", return_value=_fake_modvars()))
    stack.enter_context(patch("avenir_goals_scenario.runner.run_simulation", return_value=sim_result))
    return stack


def test_run_scenario_analysis_creates_parquet_per_pjnz_per_scenario(tmp_path):
    pjnz_dir = tmp_path / "pjnz"
    pjnz_dir.mkdir()
    (pjnz_dir / "country.PJNZ").touch()

    scenarios_path = _make_simulations_json(tmp_path, scenario_id=1, n_simulations=2)
    config = _make_run_config(tmp_path, pjnz_dir, scenarios_path, indicators=["p_hivpop"])

    with _integration_patches(_SIM_RESULT):
        run_scenario_analysis(config)

    assert (config.output_dir / "p_hivpop" / "pjnz_name=country" / "scenario_id=1" / "part-0.parquet").exists()


def test_run_scenario_analysis_parquet_row_count(tmp_path):
    pjnz_dir = tmp_path / "pjnz"
    pjnz_dir.mkdir()
    (pjnz_dir / "country.PJNZ").touch()

    import pyarrow.parquet as pq

    n_sims = 3
    scenarios_path = _make_simulations_json(tmp_path, scenario_id=1, n_simulations=n_sims)
    config = _make_run_config(tmp_path, pjnz_dir, scenarios_path, indicators=["p_hivpop"])

    with _integration_patches(_SIM_RESULT):
        run_scenario_analysis(config)

    path = config.output_dir / "p_hivpop" / "pjnz_name=country" / "scenario_id=1" / "part-0.parquet"
    table = pq.read_table(path)
    assert len(table) == n_sims * int(np.prod(_P_HIVPOP_SHAPE))


def test_run_scenario_analysis_multiple_pjnz_creates_separate_partitions(tmp_path):
    pjnz_dir = tmp_path / "pjnz"
    pjnz_dir.mkdir()
    (pjnz_dir / "alpha.PJNZ").touch()
    (pjnz_dir / "beta.PJNZ").touch()

    scenarios_path = _make_simulations_json(tmp_path, n_simulations=1)
    config = _make_run_config(tmp_path, pjnz_dir, scenarios_path, indicators=["p_hivpop"])

    with _integration_patches(_SIM_RESULT):
        run_scenario_analysis(config)

    assert (config.output_dir / "p_hivpop" / "pjnz_name=alpha" / "scenario_id=1" / "part-0.parquet").exists()
    assert (config.output_dir / "p_hivpop" / "pjnz_name=beta" / "scenario_id=1" / "part-0.parquet").exists()


def test_run_scenario_analysis_unknown_indicator_raises_before_pjnz_import(tmp_path):
    pjnz_dir = tmp_path / "pjnz"
    pjnz_dir.mkdir()
    (pjnz_dir / "country.PJNZ").touch()

    scenarios_path = _make_simulations_json(tmp_path, n_simulations=1)
    config = _make_run_config(tmp_path, pjnz_dir, scenarios_path, indicators=["not_a_real_indicator"])

    with (
        patch("avenir_goals_scenario.runner.import_pjnz", return_value=_fake_modvars()) as mock_import,
        pytest.raises(Exception, match="not_a_real_indicator"),
    ):
        run_scenario_analysis(config)

    mock_import.assert_not_called()


def test_run_scenario_analysis_uses_parallel_when_multiple_workers(tmp_path):
    pjnz_dir = tmp_path / "pjnz"
    pjnz_dir.mkdir()
    (pjnz_dir / "country.PJNZ").touch()

    scenarios_path = _make_simulations_json(tmp_path, n_simulations=1)
    config = RunConfig(
        pjnz_dir=pjnz_dir,
        scenario_path=scenarios_path,
        output_dir=tmp_path / "output",
        base_year=2020,
        output_indicators=["p_hivpop"],
        n_workers=2,
    )

    with (
        patch("avenir_goals_scenario.runner.import_pjnz", return_value=_fake_modvars()),
        patch("avenir_goals_scenario.runner.Parallel") as mock_parallel,
        patch("avenir_goals_scenario.runner.delayed"),
    ):
        mock_parallel.return_value.return_value = ["country"]
        run_scenario_analysis(config)

    mock_parallel.assert_called_once_with(n_jobs=2, return_as="generator_unordered")


# ---------------------------------------------------------------------------
# _run_pjnz_scenario - log_queue branch
# ---------------------------------------------------------------------------


def test_run_pjnz_scenario_configures_worker_logging_when_log_queue_provided(tmp_path):
    params = {"projection_end_year": 2024}
    params_path = str(tmp_path / "params.pkl")
    with open(params_path, "wb") as f:
        pickle.dump(params, f)

    scenario = MagicMock()
    scenario.simulations = [{}]
    scenario.scenario_id = 1

    config = _make_run_config(tmp_path, tmp_path, _make_simulations_json(tmp_path), indicators=["PLHIV"])
    log_queue = Queue()

    with (
        patch("avenir_goals_scenario._cli.cli_utils.configure_worker_logging") as mock_configure,
        patch("avenir_goals_scenario.runner.run_simulation", return_value={"PLHIV": np.ones(_N_YEARS)}),
        patch("avenir_goals_scenario.runner.write_scenario_results"),
    ):
        _run_pjnz_scenario(params_path, "country", scenario, config, 2025, log_queue)

    mock_configure.assert_called_once_with(log_queue)


# ---------------------------------------------------------------------------
# _import_pjnz_modvars - success path
# ---------------------------------------------------------------------------


def test_import_pjnz_modvars_converts_list_values_to_numpy(tmp_path):
    pjnz_path = tmp_path / "good.PJNZ"
    pjnz_path.touch()
    fake_modvars = {"nums": [1.0, 2.0], "scalar": 5}

    with patch(
        "avenir_goals_scenario._runner.pjnz.GB_ImportProjectionFromFile", return_value=(fake_modvars, None, None, None)
    ):
        result = _import_pjnz_modvars(pjnz_path)

    assert isinstance(result["nums"], np.ndarray)
    assert result["scalar"] == 5


def test_import_pjnz_returns_leapfrog_params_with_ex_input(tmp_path):
    pjnz_path = tmp_path / "good.PJNZ"
    pjnz_path.touch()
    fake_ss = {"pAG": 17, "NS": 2}
    fake_leapfrog = {"projection_end_year": 2024}

    with (
        patch("avenir_goals_scenario._runner.pjnz._import_pjnz_modvars", return_value={}),
        patch("avenir_goals_scenario._runner.pjnz.get_goals_ss", return_value=fake_ss),
        patch("avenir_goals_scenario._runner.pjnz.modvars_to_leapfrog", return_value=fake_leapfrog),
    ):
        result = import_pjnz(pjnz_path)

    assert "ex_input" in result
    assert result["ex_input"].shape == (17, 2)
