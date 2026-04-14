from __future__ import annotations

import contextlib
import os
import threading
from queue import Empty, Queue

from loguru import logger
from rich.console import Console
from rich.progress import BarColumn, MofNCompleteColumn, Progress, TextColumn, TimeRemainingColumn

from avenir_goals_scenario.models.run_config import RunConfig

console = Console()

# Sentinel placed on the log queue to signal the listener thread to stop.
# Must be None (not object()) because Manager().Queue() pickles items across
# process boundaries — object() loses identity after a pickle round-trip.
_STOP = None


def _log_formatter(verbose: bool):
    color_map = {
        "TRACE": "dim blue",
        "DEBUG": "bold steel_blue",
        "INFO": "bright_white",
        "SUCCESS": "bold green",
        "WARNING": "yellow",
        "ERROR": "bold red",
        "CRITICAL": "bold white on red",
    }

    fn_line = ""
    if verbose:
        fn_line = " [cyan]{name}:{function}:{line}[cyan] -"

    def format_log(record: dict) -> str:
        lvl_color = color_map.get(record["level"].name, "cyan")
        return (
            "[not bold green]{time:YYYY/MM/DD HH:mm:ss}[/not bold green] |"
            + f" [{lvl_color}]{{level:<8}}[/{lvl_color}] |"
            + fn_line
            + f" [{lvl_color}]{{message}}[/{lvl_color}]"
        )

    return format_log


def configure_cli_logging(verbose: bool) -> None:
    logger.remove()
    logger.add(
        lambda m: console.print(m),
        format=_log_formatter(verbose),
        level="DEBUG" if verbose else "INFO",
        colorize=True,
    )


def get_number_of_workers(config: RunConfig) -> int:
    cpu_count = os.cpu_count() or 1
    effective_workers = cpu_count if config.n_workers == -1 else config.n_workers
    logger.info(
        "Using {} worker(s) (cpu_count={}, configured n_workers={})",
        effective_workers,
        cpu_count,
        config.n_workers,
    )
    return effective_workers


def make_log_queue_listener(log_queue: Queue) -> threading.Thread:
    """Start and return a daemon thread that drains *log_queue* into loguru.

    Each item on the queue is a record dict forwarded to loguru in the main
    process, preserving the original name/function/line so the main process
    format string (including verbose file paths) applies correctly. The thread
    stops when it receives ``_STOP``.
    """

    def _listen() -> None:
        while True:
            try:
                item = log_queue.get(timeout=0.01)
            except Empty:
                continue
            if item is _STOP:
                break
            logger.patch(lambda r, rec=item: r.update(rec)).info("")

    thread = threading.Thread(target=_listen, daemon=True)
    thread.start()
    return thread


def stop_log_queue_listener(log_queue: Queue, listener: threading.Thread) -> None:
    """Signal the listener thread to stop and wait for it to finish."""
    log_queue.put(_STOP)
    listener.join()


def configure_worker_logging(log_queue: Queue) -> None:
    """Replace loguru handlers in a worker process with a queue sink.

    Called at the start of each worker function so that all ``logger`` calls
    are forwarded to the main process for display rather than being captured
    by joblib's loky backend.
    """

    def _sink(message) -> None:
        record = message.record
        log_queue.put({
            "level": record["level"],
            "message": record["message"],
            "name": record["name"],
            "function": record["function"],
            "line": record["line"],
        })

    logger.remove()
    logger.add(_sink, format="{message}", colorize=False)


@contextlib.contextmanager
def task_progress(tasks: dict[str, int]):
    with Progress(
        TextColumn("[cyan]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        TimeRemainingColumn(),
        console=console,
    ) as progress:
        task_ids = {label: progress.add_task(label, total=steps) for label, steps in tasks.items()}

        def advance(label: str) -> None:
            progress.advance(task_ids[label])

        yield advance
