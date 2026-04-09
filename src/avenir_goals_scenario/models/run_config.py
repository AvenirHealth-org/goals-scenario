from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator, model_validator


class RunConfig(BaseModel):
    """Configuration for `avenir_goals_scenario.run_scenario_analysis`.

    Field names are case-insensitive: ``PJNZ_Dir``, ``pjnz_dir``, and
    ``PJNZ_DIR`` are all accepted.

    ``output_dir`` is created if it does not exist, but only one level deep —
    its parent must already exist.

    Attributes:
        pjnz_dir (Path): Directory containing ``.PJNZ`` files.
        scenario_path (Path): Path to the scenario simulations JSON file produced by
            `avenir_goals_scenario.generate_simulations`.
        output_dir (Path): Directory where per-PJNZ result subdirectories are written.
            Created automatically if absent (parent must exist).
        base_year (int): First year of the output projection range.
        output_indicators (list[str]): Names of the Goals output indicators to write.
            Each name must be a key in the dict returned by ``run_goals``.
    """

    model_config = ConfigDict(extra="forbid")

    pjnz_dir: Path
    scenario_path: Path
    output_dir: Path
    base_year: int
    output_indicators: list[str]

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

    @field_validator("scenario_path")
    @classmethod
    def _scenario_path_must_be_file(cls, v: Path) -> Path:
        path = v.expanduser().resolve()
        if not path.exists():
            msg = f"Scenario file does not exist: {path}"
            raise ValueError(msg)
        if not path.is_file():
            msg = f"scenario_path is not a file: {path}"
            raise ValueError(msg)
        return path

    @field_validator("output_dir")
    @classmethod
    def _create_output_dir(cls, v: Path) -> Path:
        path = v.expanduser().resolve()
        if path.exists() and not path.is_dir():
            msg = f"output_dir exists but is not a directory: {path}"
            raise ValueError(msg)
        if not path.exists():
            if not path.parent.exists():
                msg = f"Cannot create output_dir {path}: parent directory does not exist: {path.parent}"
                raise ValueError(msg)
            path.mkdir()
        return path
