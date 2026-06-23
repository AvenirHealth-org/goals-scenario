import pyarrow.parquet as pq

from avenir_goals_scenario._runner.pjnz import import_pjnz
from avenir_goals_scenario.models.run_config import RunConfig
from avenir_goals_scenario.runner import run_scenario_analysis
from avenir_goals_scenario.scenarios import draw_simulations
from tests.conftest import requires_test_data

_BASE_YEAR = 2010
_N_SIMULATIONS = 2
_INDICATORS = ["p_hivpop", "p_infections", "p_hiv_deaths", "h_artpop"]
_SCENARIOS = [1, 2, 3, 4]
_PJNZ_NAMES = ["SouthAfrica"]
# _PJNZ_NAMES = ["Azerbaijan", "Botswana", "DRC", "Ethiopia", "Ghana", "SouthAfrica", "Zambia", "Zimbabwe"]

# Every output indicator type, including the resource and calculated indicators.
_ALL_INDICATORS = [
    "p_hivpop",
    "p_infections",
    "p_hiv_deaths",
    "h_artpop",
    "num_people_reached",
    "resources_required",
    "p_prevalence",
    "p_incidence",
]
# Scenarios in scenario_definitions_all_products.json: baseline + one scenario
# exercising every intervention/product type.
_ALL_PRODUCT_SCENARIOS = ["0", "all_products"]


@requires_test_data
def test_can_run_goals_scenario_end_to_end(tmp_path_factory, test_data):
    tmp = tmp_path_factory.mktemp("integration")

    simulations = draw_simulations(
        test_data / "scenario_definitions.json",
        base_year=_BASE_YEAR,
        n_simulations=_N_SIMULATIONS,
    )

    config = RunConfig(
        pjnz_dir=test_data / "pjnz" / "goals",
        output_dir=tmp / "output",
        base_year=_BASE_YEAR,
        output_indicators=_INDICATORS,
    )

    result = run_scenario_analysis(config, simulations)
    assert result.failures == []
    out_dir = result.output_dir

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

        params = import_pjnz(test_data / "pjnz" / "goals" / f"{pjnz_name}.PJNZ")
        expected_n_years = params["projection_end_year"] - _BASE_YEAR + 1
        expected_rows = _N_SIMULATIONS * 81 * 2 * expected_n_years
        assert len(table) == expected_rows


@requires_test_data
def test_every_product_type_runs_end_to_end(tmp_path_factory, test_data):
    """Guard that a scenario containing one of every intervention/product type
    applies cleanly and runs through Goals, producing every output indicator.

    The fixture restricts itself to a single PJNZ (SouthAfrica) via ``pjnz_names``
    to keep the test fast.
    """
    tmp = tmp_path_factory.mktemp("all_products")

    simulations = draw_simulations(
        test_data / "scenario_definitions_all_products.json",
        base_year=_BASE_YEAR,
        n_simulations=_N_SIMULATIONS,
    )

    config = RunConfig(
        pjnz_dir=test_data / "pjnz" / "goals",
        output_dir=tmp / "output",
        base_year=_BASE_YEAR,
        output_indicators=_ALL_INDICATORS,
    )

    result = run_scenario_analysis(config, simulations)
    assert result.failures == []
    out_dir = result.output_dir

    # Every requested indicator is written as a top-level directory.
    indicator_dirs = {p.name for p in out_dir.iterdir() if p.is_dir()}
    assert indicator_dirs == set(_ALL_INDICATORS)

    # Each indicator has output for both scenarios (baseline + all-products) for
    # the single targeted PJNZ. Reaching this point means every product type was
    # dispatched and applied without error.
    for indicator in _ALL_INDICATORS:
        pjnz_dir = out_dir / indicator / "pjnz_name=SouthAfrica"
        scenario_dirs = {p.name for p in pjnz_dir.iterdir() if p.is_dir()}
        assert scenario_dirs == {f"scenario_id={sid}" for sid in _ALL_PRODUCT_SCENARIOS}
