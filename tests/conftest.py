from pathlib import Path
from typing import Any

import orjson
import pytest


@pytest.fixture
def write_json(tmp_path: Path):
    """Factory fixture: writes a dict as JSON to a temp file, returns the path."""

    def _write(data: dict[str, Any], filename: str = "input.json") -> Path:
        path = tmp_path / filename
        path.write_bytes(orjson.dumps(data))
        return path

    return _write


@pytest.fixture
def write_csv(tmp_path: Path):
    """Factory fixture: writes CSV text to a temp file, returns the path."""

    def _write(content: str, filename: str = "input.csv") -> Path:
        path = tmp_path / filename
        path.write_text(content, encoding="utf-8")
        return path

    return _write
