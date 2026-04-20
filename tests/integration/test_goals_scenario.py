import pyarrow.parquet as pq

from avenir_goals_scenario._runner.pjnz import import_pjnz
from avenir_goals_scenario.models.run_config import RunConfig
from avenir_goals_scenario.runner import run_scenario_analysis
from avenir_goals_scenario.scenarios import draw_simulations

_BASE_YEAR = 2010
_N_SIMULATIONS = 2
_INDICATORS = ["p_hivpop", "p_infections", "p_hiv_deaths", "h_artpop"]
_SCENARIOS = [1, 2, 3, 4]
_PJNZ_NAMES = ["Azerbaijan", "Botswana", "DRC", "Ethiopia", "Ghana", "SouthAfrica", "Zambia", "Zimbabwe"]


def test_can_run_goals_scenario_end_to_end(tmp_path_factory, test_data):
    tmp = tmp_path_factory.mktemp("integration")

    simulations = draw_simulations(
        test_data / "scenario_descriptions.csv",
        n_simulations=_N_SIMULATIONS,
        base_year=_BASE_YEAR,
    )

    config = RunConfig(
        pjnz_dir=test_data / "pjnz",
        output_dir=tmp / "output",
        base_year=_BASE_YEAR,
        output_indicators=_INDICATORS,
    )

    out_dir = run_scenario_analysis(config, simulations)

    ## All indicators are output as top-level directories
    indicator_dirs = {p.name for p in out_dir.iterdir() if p.is_dir()}
    assert indicator_dirs == set(_INDICATORS)

    for indicator in _INDICATORS:
        for pjnz_name in _PJNZ_NAMES:
            ## Each PJNZ has the right number of scenario partitions
            pjnz_dir = out_dir / indicator / f"pjnz_name={pjnz_name}"
            scenario_dirs = {p.name for p in pjnz_dir.iterdir() if p.is_dir()}
            assert scenario_dirs == {f"scenario_id={sid}" for sid in _SCENARIOS}

    ## Spot-check p_hivpop schema and row count for scenario 1
    for pjnz_name in _PJNZ_NAMES:
        path = out_dir / "p_hivpop" / f"pjnz_name={pjnz_name}" / "scenario_id=1" / "part-0.parquet"
        table = pq.read_table(path)

        assert "age" in table.schema.names
        assert "sex" in table.schema.names
        assert "year" in table.schema.names
        assert "simulation" in table.schema.names
        assert "value" in table.schema.names

        params = import_pjnz(test_data / "pjnz" / f"{pjnz_name}.PJNZ")
        expected_n_years = params["projection_end_year"] - _BASE_YEAR + 1
        expected_rows = _N_SIMULATIONS * 81 * 2 * expected_n_years
        assert len(table) == expected_rows
