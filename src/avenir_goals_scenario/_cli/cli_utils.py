import threading
from multiprocessing import Manager
from queue import Empty, Queue

from loguru import logger
from rich.console import Console
from rich.progress import BarColumn, MofNCompleteColumn, Progress, TaskID, TextColumn, TimeRemainingColumn
from rich.traceback import Traceback

from avenir_goals_scenario._runner.pjnz import find_pjnz_files
from avenir_goals_scenario._runner.utils import RunCallbacks, get_effective_workers
from avenir_goals_scenario.models import ScenarioSimulations
from avenir_goals_scenario.runner import _run_scenario_analysis

console = Console()

# Sentinel placed on the log queue to signal the listener thread to stop.
_STOP = "stop"


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


def _sink(verbose: bool):
    def sink(message):
        record = message.record

        console.print(message)

        if verbose and record["exception"]:
            exc_type, exc_value, exc_tb = record["exception"]
            tb = Traceback.from_exception(exc_type, exc_value, exc_tb)
            console.print(tb)

    return sink


def configure_cli_logging(verbose: bool) -> None:
    logger.remove()
    logger.add(
        _sink(verbose),
        format=_log_formatter(verbose),
        level="DEBUG" if verbose else "INFO",
        colorize=True,
        backtrace=verbose,
        diagnose=verbose,
    )


def _make_log_queue_listener(log_queue: Queue) -> threading.Thread:
    """Start a daemon thread that drains *log_queue* into loguru."""

    def _listen() -> None:
        while True:
            try:
                item = log_queue.get(timeout=0.01)
            except Empty:
                continue
            if item == _STOP:
                break
            logger.patch(lambda r, rec=item: r.update(rec)).info("")

    thread = threading.Thread(target=_listen, daemon=True)
    thread.start()
    return thread


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


def run_with_progress(config) -> None:
    """Run scenario analysis with Rich progress bars and worker log routing.

    This is the CLI entry point. It sets up a shared Progress display,
    a log queue for worker processes, and wires up RunCallbacks to drive
    the progress bars.
    """

    pjnz_files = find_pjnz_files(config.pjnz_dir)
    n_pjnz = len(pjnz_files)
    n_scenarios = len(ScenarioSimulations.model_validate_json(config.scenario_path.read_bytes()).scenarios)

    effective_workers = get_effective_workers(config)
    use_subprocess = effective_workers != 1
    mp_manager = Manager() if use_subprocess else None
    log_queue: Queue | None = mp_manager.Queue() if mp_manager is not None else None
    listener: threading.Thread | None = _make_log_queue_listener(log_queue) if log_queue is not None else None

    import_progress = Progress(
        TextColumn("[cyan]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        TimeRemainingColumn(),
        console=console,
    )
    run_progress = Progress(
        TextColumn("[cyan]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        TimeRemainingColumn(),
        console=console,
    )

    try:
        import_task = import_progress.add_task("Importing PJNZ files", total=n_pjnz)
        scenario_tasks: dict[str, TaskID] = {}

        def on_pjnz_imported() -> None:
            import_progress.advance(import_task)

        def on_imports_complete() -> None:
            import_progress.stop()
            for pjnz_path in pjnz_files:
                scenario_tasks[pjnz_path.stem] = run_progress.add_task(pjnz_path.stem, total=n_scenarios)
            run_progress.start()

        def on_scenario_complete(stem: str) -> None:
            run_progress.advance(scenario_tasks[stem])

        def on_run_complete() -> None:
            run_progress.stop()

        callbacks = RunCallbacks(
            on_pjnz_imported=on_pjnz_imported,
            on_imports_complete=on_imports_complete,
            on_scenario_complete=on_scenario_complete,
            on_run_complete=on_run_complete,
        )
        import_progress.start()
        _run_scenario_analysis(config, callbacks, log_queue=log_queue)
    finally:
        # Make sure we call stop on these, in the case that a user
        # hits ctrl+c before we call it in the callbacks above
        # or we raise an error
        import_progress.stop()
        run_progress.stop()
        if log_queue is not None and listener is not None:
            log_queue.put(_STOP)
            listener.join()
        if mp_manager is not None:
            mp_manager.shutdown()
