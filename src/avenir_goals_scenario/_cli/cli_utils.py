import contextlib

from rich.progress import Progress


@contextlib.contextmanager
def task_progress(tasks: dict[str, int]):
    with Progress() as progress:
        task_ids = {label: progress.add_task(f"[cyan]{label}", total=steps) for label, steps in tasks.items()}

        def advance(label: str) -> None:
            progress.advance(task_ids[label])

        yield advance
