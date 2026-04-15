import h5py

from avenir_goals_scenario._runner.pjnz import import_pjnz
from avenir_goals_scenario.models.run_config import RunConfig
from avenir_goals_scenario.runner import run_scenario_analysis
from avenir_goals_scenario.scenarios import generate_simulations

_BASE_YEAR = 2010
_N_SIMULATIONS = 2
_INDICATORS = ["p_hivpop", "p_infections", "p_hiv_deaths", "h_artpop"]
_SCENARIOS = [1, 2, 3, 4]
_PJNZ_NAMES = ["Azerbaijan", "Botswana", "DRC", "Ethiopia", "Ghana", "SouthAfrica", "Zambia", "Zimbabwe"]


def test_can_run_goals_scenario_end_to_end(tmp_path_factory, test_data):
    tmp = tmp_path_factory.mktemp("integration")

    simulations_path = generate_simulations(
        test_data / "scenario_descriptions.csv",
        tmp / "scenario.json",
        n_simulations=_N_SIMULATIONS,
    )

    config = RunConfig(
        pjnz_dir=test_data / "pjnz",
        scenario_path=simulations_path,
        output_dir=tmp / "output",
        base_year=_BASE_YEAR,
        output_indicators=_INDICATORS,
    )

    out_dir = run_scenario_analysis(config)

    ## All PJNZ files are output
    subdirs = {p.name for p in out_dir.iterdir() if p.is_dir()}
    assert subdirs == set(_PJNZ_NAMES)

    for pjnz_name in _PJNZ_NAMES:
        ## We output the right number of scenarios
        files = {p.name for p in (out_dir / pjnz_name).iterdir()}
        assert files == {f"scenario_{sid}.h5" for sid in _SCENARIOS}

        path = out_dir / pjnz_name / "scenario_1.h5"
        with h5py.File(path, "r") as f:
            ## All indicators are output
            for indicator in _INDICATORS:
                assert indicator in f, f"Missing dataset '{indicator}' in {path}"

            params = import_pjnz(test_data / "pjnz" / f"{pjnz_name}.PJNZ")
            expected_n_years = params["projection_end_year"] - _BASE_YEAR + 1
            ## Shapes are as expected
            assert f["p_hivpop"].shape[0] == _N_SIMULATIONS
            assert f["p_hivpop"].shape[-1] == expected_n_years
