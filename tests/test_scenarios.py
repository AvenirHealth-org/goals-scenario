import pytest

from goals_sa.scenarios import generate_scenarios


def test_generate_scenarios_runs(tmp_path):
    # Stub raises NotImplementedError — update this test when implemented.
    with pytest.raises(NotImplementedError):
        generate_scenarios(tmp_path / "scenarios.csv")


def test_generate_scenarios_raises_when_parent_missing(tmp_path):
    with pytest.raises(FileNotFoundError, match="Destination directory does not exist"):
        generate_scenarios(tmp_path / "nonexistent_dir" / "scenarios.csv")


def test_generate_scenarios_resolves_relative_paths(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    # Relative path — parent (cwd = tmp_path) exists, so we get NotImplementedError not FileNotFoundError.
    with pytest.raises(NotImplementedError):
        generate_scenarios("scenarios.csv")
