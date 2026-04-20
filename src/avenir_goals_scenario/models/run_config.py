import os
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class RunConfig(BaseModel):
    """Configuration for `avenir_goals_scenario.run_scenario_analysis`.

    Field names are case-insensitive: ``PJNZ_Dir``, ``pjnz_dir``, and
    ``PJNZ_DIR`` are all accepted.

    ``output_dir`` is created if it does not exist, but only one level deep -
    its parent must already exist.

    Attributes:
        pjnz_dir (Path): Directory containing ``.PJNZ`` files.
        definition_path (Path | None): Path to the scenario definition CSV file.
            Required for the ``draw`` command and for ``run`` when draws are not
            pre-generated. Either ``definition_path``, ``scenario_path``, or
            both must be supplied for ``run``.
        scenario_path (Path | None): Path to a scenario simulations JSON file.
            For ``draw``, this is where draws are written. For ``run``, if
            supplied and the file exists the draws are loaded from it rather
            than regenerated.
        output_dir (Path): Directory where per-PJNZ result subdirectories are
            written.  Created automatically if absent (parent must exist).
        base_year (int): First year of the output projection range.
        output_indicators (list[str]): Names of the Goals output indicators to
            write. Each name must be a key in the dict returned by ``run_goals``.
        n_simulations (int): Number of simulations drawn per scenario (default
            100). Ignored when loading draws from an existing ``scenario_path``.
        seed (int | None): Optional RNG seed for reproducible draws. ``None``
            (the default) uses a random seed.
        n_workers (int): Number of parallel worker processes. Follows joblib
            conventions: ``-1`` uses all available CPUs, ``1`` runs
            sequentially, and any positive integer sets an explicit worker
            count. Zero is not valid. Uses 4 by default or the number of
            available CPUs if fewer than 4.
    """

    model_config = ConfigDict(extra="forbid")

    pjnz_dir: Path
    definition_path: Path | None = None
    scenario_path: Path | None = None
    output_dir: Path
    base_year: int
    output_indicators: list[str]
    n_simulations: int = 100
    seed: int | None = None
    n_workers: int = Field(default_factory=lambda: min(os.cpu_count() or 1, 4))

    @field_validator("n_workers")
    @classmethod
    def _n_workers_must_be_nonzero(cls, v: int) -> int:
        if v == 0:
            msg = "n_workers must be non-zero (-1 for all CPUs, or a positive integer)"
            raise ValueError(msg)
        return v

    @field_validator("n_simulations")
    @classmethod
    def _n_simulations_must_be_positive(cls, v: int) -> int:
        if v < 1:
            msg = "n_simulations must be a positive integer"
            raise ValueError(msg)
        return v

    @model_validator(mode="before")
    @classmethod
    def _lowercase_keys(cls, data: Any) -> Any:
        if isinstance(data, dict):
            return {k.lower(): v for k, v in data.items()}
        return data

    @field_validator("pjnz_dir")
    @classmethod
    def _pjnz_dir_must_be_directory(cls, v: Path) -> Path:
        path = v.expanduser().resolve()
        if not path.exists():
            msg = f"PJNZ directory does not exist: {path}"
            raise ValueError(msg)
        if not path.is_dir():
            msg = f"pjnz_dir is not a directory: {path}"
            raise ValueError(msg)
        return path

    @field_validator("definition_path")
    @classmethod
    def _definition_path_must_be_csv(cls, v: Path | None) -> Path | None:
        if v is None:
            return None
        path = v.expanduser().resolve()
        if not path.exists():
            msg = f"Scenario definition file does not exist: {path}"
            raise ValueError(msg)
        if not path.is_file():
            msg = f"definition_path is not a file: {path}"
            raise ValueError(msg)
        if path.suffix.lower() != ".csv":
            msg = f"definition_path must be a .csv file, got: {path.suffix or '(no extension)'}"
            raise ValueError(msg)
        return path

    @field_validator("scenario_path")
    @classmethod
    def _scenario_path_must_not_be_directory(cls, v: Path | None) -> Path | None:
        if v is None:
            return None
        path = v.expanduser().resolve()
        if path.exists() and not path.is_file():
            msg = f"scenario_path is not a file: {path}"
            raise ValueError(msg)
        return path

    @field_validator("output_dir")
    @classmethod
    def _validate_output_dir(cls, v: Path) -> Path:
        path = v.expanduser().resolve()
        if path.exists() and not path.is_dir():
            msg = f"output_dir exists but is not a directory: {path}"
            raise ValueError(msg)
        if not path.exists() and not path.parent.exists():
            msg = f"Cannot create output_dir {path}: parent directory does not exist: {path.parent}"
            raise ValueError(msg)
        return path
