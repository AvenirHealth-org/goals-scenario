import time
from pathlib import Path
from queue import Queue
from unittest.mock import MagicMock, patch

import pytest
from loguru import logger

from avenir_goals_scenario._cli.cli_utils import (
    _STOP,
    _make_log_queue_listener,
    configure_worker_logging,
    run_with_progress,
)

# ---------------------------------------------------------------------------
# _make_log_queue_listener
# ---------------------------------------------------------------------------


def test_make_log_queue_listener_stops_on_sentinel():
    q = Queue()

    thread = _make_log_queue_listener(q)
    # Let the thread spin at least once (hitting the except Empty: continue branch)
    time.sleep(0.05)
    q.put(_STOP)
    thread.join(timeout=2.0)

    assert not thread.is_alive()


def test_make_log_queue_listener_processes_log_record_then_stops():
    q = Queue()
    fake_record = {
        "level": MagicMock(name="INFO"),
        "message": "hello",
        "name": "module",
        "function": "fn",
        "line": 1,
    }
    q.put(fake_record)
    q.put(_STOP)

    with patch("avenir_goals_scenario._cli.cli_utils.logger") as mock_logger:
        mock_logger.patch.return_value = mock_logger
        thread = _make_log_queue_listener(q)
        thread.join(timeout=2.0)

    assert not thread.is_alive()
    mock_logger.patch.assert_called_once()


# ---------------------------------------------------------------------------
# configure_worker_logging
# ---------------------------------------------------------------------------


def test_configure_worker_logging_puts_log_records_on_queue():
    q = Queue()
    configure_worker_logging(q)

    logger.info("worker test message")

    item = q.get(timeout=1.0)
    assert item["message"] == "worker test message"
    assert item["name"] is not None


# ---------------------------------------------------------------------------
# run_with_progress
# ---------------------------------------------------------------------------


def _mock_pjnz_path(stem: str) -> MagicMock:
    p = MagicMock(spec=Path)
    p.stem = stem
    return p


def test_run_with_progress_calls_run_scenario_analysis():
    config = MagicMock()
    mock_paths = [_mock_pjnz_path("alpha"), _mock_pjnz_path("beta")]
    mock_scenarios = MagicMock()
    mock_scenarios.scenarios = [MagicMock(), MagicMock()]

    with (
        patch("avenir_goals_scenario._cli.cli_utils.find_pjnz_files", return_value=mock_paths),
        patch("avenir_goals_scenario._cli.cli_utils.ScenarioSimulations") as mock_ss,
        patch("avenir_goals_scenario._cli.cli_utils.get_effective_workers", return_value=1),
        patch("avenir_goals_scenario._cli.cli_utils._run_scenario_analysis") as mock_run,
    ):
        mock_ss.model_validate_json.return_value = mock_scenarios
        run_with_progress(config)

    mock_run.assert_called_once()


def test_run_with_progress_exercises_all_callbacks():
    config = MagicMock()
    mock_paths = [_mock_pjnz_path("country")]
    mock_scenarios = MagicMock()
    mock_scenarios.scenarios = [MagicMock()]

    def fake_run(cfg, callbacks, log_queue=None):
        callbacks.on_pjnz_imported()
        callbacks.on_imports_complete()
        callbacks.on_scenario_complete("country")
        callbacks.on_run_complete()

    with (
        patch("avenir_goals_scenario._cli.cli_utils.find_pjnz_files", return_value=mock_paths),
        patch("avenir_goals_scenario._cli.cli_utils.ScenarioSimulations") as mock_ss,
        patch("avenir_goals_scenario._cli.cli_utils.get_effective_workers", return_value=1),
        patch("avenir_goals_scenario._cli.cli_utils._run_scenario_analysis", side_effect=fake_run),
    ):
        mock_ss.model_validate_json.return_value = mock_scenarios
        run_with_progress(config)


def test_run_with_progress_stops_progress_on_exception():
    config = MagicMock()
    mock_paths = [_mock_pjnz_path("country")]
    mock_scenarios = MagicMock()
    mock_scenarios.scenarios = [MagicMock()]

    with (
        patch("avenir_goals_scenario._cli.cli_utils.find_pjnz_files", return_value=mock_paths),
        patch("avenir_goals_scenario._cli.cli_utils.ScenarioSimulations") as mock_ss,
        patch("avenir_goals_scenario._cli.cli_utils.get_effective_workers", return_value=1),
        patch("avenir_goals_scenario._cli.cli_utils._run_scenario_analysis", side_effect=RuntimeError("boom")),
    ):
        mock_ss.model_validate_json.return_value = mock_scenarios
        with pytest.raises(RuntimeError, match="boom"):
            run_with_progress(config)


def test_run_with_progress_with_multiple_workers_cleans_up():
    config = MagicMock()
    mock_paths = [_mock_pjnz_path("country")]
    mock_scenarios = MagicMock()
    mock_scenarios.scenarios = [MagicMock()]

    mock_manager = MagicMock()
    mock_queue = MagicMock()
    mock_manager.Queue.return_value = mock_queue
    mock_listener = MagicMock()

    with (
        patch("avenir_goals_scenario._cli.cli_utils.find_pjnz_files", return_value=mock_paths),
        patch("avenir_goals_scenario._cli.cli_utils.ScenarioSimulations") as mock_ss,
        patch("avenir_goals_scenario._cli.cli_utils.get_effective_workers", return_value=2),
        patch("avenir_goals_scenario._cli.cli_utils.Manager", return_value=mock_manager),
        patch("avenir_goals_scenario._cli.cli_utils._make_log_queue_listener", return_value=mock_listener),
        patch("avenir_goals_scenario._cli.cli_utils._run_scenario_analysis"),
    ):
        mock_ss.model_validate_json.return_value = mock_scenarios
        run_with_progress(config)

    mock_queue.put.assert_called_with(_STOP)
    mock_listener.join.assert_called_once()
    mock_manager.shutdown.assert_called_once()
