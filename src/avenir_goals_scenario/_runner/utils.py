import os
from collections.abc import Callable
from dataclasses import dataclass, field

from avenir_goals_scenario.models.run_config import RunConfig


def get_effective_workers(config: RunConfig) -> int:
    cpu_count = os.cpu_count() or 1
    effective_workers = cpu_count if config.n_workers == -1 else config.n_workers
    return effective_workers


_noop = lambda *_args, **_kwargs: None


@dataclass
class RunCallbacks:
    """Optional hooks called during a scenario analysis run.

    All default to no-ops so callers only supply what they care about.
    """

    on_pjnz_imported: Callable[[], None] = field(default=_noop)
    on_imports_complete: Callable[[], None] = field(default=_noop)
    on_scenario_complete: Callable[[str], None] = field(default=_noop)
    on_run_complete: Callable[[], None] = field(default=_noop)
