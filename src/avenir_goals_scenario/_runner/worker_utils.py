from __future__ import annotations

import os

from loguru import logger

from avenir_goals_scenario.models.run_config import RunConfig


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
