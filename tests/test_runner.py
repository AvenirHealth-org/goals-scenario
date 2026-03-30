import pytest

from avenir_goals_scenario.runner import find_pjnz_files, run_scenario_analysis


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


def test_run_scenario_analysis_runs(tmp_path):
    pjnz_dir = tmp_path / "pjnz"
    pjnz_dir.mkdir()
    (pjnz_dir / "country.PJNZ").touch()

    scenarios_file = tmp_path / "scenarios.csv"
    scenarios_file.touch()

    # This just confirms the function runs without error.
    run_scenario_analysis(
        pjnz_dir=pjnz_dir,
        scenarios_path=scenarios_file,
        output_path=tmp_path / "output",
    )


def test_run_scenario_analysis_raises_when_pjnz_dir_missing(tmp_path):
    with pytest.raises(FileNotFoundError, match="PJNZ directory does not exist"):
        run_scenario_analysis(
            pjnz_dir=tmp_path / "nonexistent",
            scenarios_path=tmp_path / "scenarios.csv",
            output_path=tmp_path / "output",
        )


def test_run_scenario_analysis_raises_when_scenarios_path_missing(tmp_path):
    pjnz_dir = tmp_path / "pjnz"
    pjnz_dir.mkdir()

    with pytest.raises(FileNotFoundError, match="Scenarios file does not exist"):
        run_scenario_analysis(
            pjnz_dir=pjnz_dir,
            scenarios_path=tmp_path / "nonexistent.csv",
            output_path=tmp_path / "output",
        )


def test_run_scenario_analysis_resolves_relative_paths(tmp_path, monkeypatch):
    pjnz_dir = tmp_path / "pjnz"
    pjnz_dir.mkdir()
    (pjnz_dir / "country.PJNZ").touch()
    (tmp_path / "scenarios.csv").touch()

    monkeypatch.chdir(tmp_path)

    # Relative paths should resolve without error.
    run_scenario_analysis(
        pjnz_dir="pjnz",
        scenarios_path="scenarios.csv",
        output_path="output",
    )
