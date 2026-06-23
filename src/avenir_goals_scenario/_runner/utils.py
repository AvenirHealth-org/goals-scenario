import os
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from avenir_goals_scenario.models.run_config import RunConfig


def get_effective_workers(config: RunConfig) -> int:
    cpu_count = os.cpu_count() or 1
    effective_workers = cpu_count if config.n_workers == -1 else config.n_workers
    return effective_workers


@dataclass(frozen=True)
class WorkUnitResult:
    """Outcome of running a single ``(PJNZ, scenario)`` work unit.

    ``ok`` is ``False`` when the simulation or result write raised; ``error``
    then holds a short message. Failures are non-fatal: the run continues and
    failed units are collected into a :class:`RunResult` and the
    ``failures.json`` manifest.
    """

    pjnz: str
    scenario_id: str
    ok: bool
    error: str | None = None


@dataclass
class RunResult:
    """Outcome of a full scenario analysis run.

    ``failures`` is empty on a fully successful run. A non-empty list means some
    ``(PJNZ, scenario)`` units failed but the rest completed and were written.
    """

    output_dir: Path
    failures: list[WorkUnitResult] = field(default_factory=list)


_noop = lambda *_args, **_kwargs: None


@dataclass
class RunCallbacks:
    """Optional hooks called during a scenario analysis run.

    All default to no-ops so callers only supply what they care about.
    """

    on_pjnz_imported: Callable[[], None] = field(default=_noop)
    on_imports_complete: Callable[[], None] = field(default=_noop)
    on_scenario_complete: Callable[[str], None] = field(default=_noop)
    on_scenario_failed: Callable[[str], None] = field(default=_noop)
    on_run_complete: Callable[[], None] = field(default=_noop)
