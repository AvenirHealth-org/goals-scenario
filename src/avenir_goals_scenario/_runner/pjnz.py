import os
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any

import numpy as np
from leapfrog_goals import get_goals_ss
from loguru import logger
from Tools.ImportPJNZ.Importer import GB_ImportProjectionFromFile

from avenir_goals_scenario._leapfrog.LeapfrogDataMapping import modvars_to_leapfrog


def find_pjnz_files(pjnz_dir: Path) -> list[Path]:
    """Return a sorted list of PJNZ files in a directory.

    Args:
        pjnz_dir: Directory to search.

    Returns:
        Sorted list of paths to ``.PJNZ`` files.

    Raises:
        FileNotFoundError: If no PJNZ files are found in the directory.
    """
    files = sorted(pjnz_dir.glob("*.PJNZ"))
    if not files:
        err_msg = f"No PJNZ files found in {pjnz_dir}"
        raise FileNotFoundError(err_msg)

    logger.info("Found {} PJNZ file(s) in {}", len(files), pjnz_dir)
    return files


def _import_pjnz_modvars(path: Path) -> dict:
    """Import a PJNZ file and return its modvars dict.

    Args:
        path: Path to a ``.PJNZ`` file.

    Returns:
        Modvars dict for use with `modvars_to_leapfrog`.

    Raises:
        ValueError: If the PJNZ file cannot be parsed.
    """
    # TODO: remove this silent reading once we make GB_ImportProjectionFromFile
    # less chatty.
    with open(os.devnull, "w") as devnull, redirect_stdout(devnull):
        modvars, _params, _epp_files, _shiny90 = GB_ImportProjectionFromFile(str(path))
    if modvars is None:
        err_msg = f"Failed to import PJNZ file: {path}"
        raise ValueError(err_msg)
    numpy_modvars = {tag: modvars_to_numpy(value) for tag, value in modvars.items()}

    return numpy_modvars


def import_pjnz(path: Path) -> dict:
    modvars_base = _import_pjnz_modvars(path)
    ss = get_goals_ss()
    leapfrog_params = modvars_to_leapfrog(modvars_base, ss)
    # Temporarily add in required input data for this in-progress
    # version of leapfrog goals
    leapfrog_params["ex_input"] = np.full((ss["pAG"], ss["NS"]), 1)  # ty: ignore[invalid-argument-type]
    return leapfrog_params


def modvars_to_numpy(value: Any) -> Any:
    # Taken from FilterUtils.py in SpectrumEngine
    if isinstance(value, list):
        if len(value) > 0 and isinstance(value[0], (dict, str, bool)):
            value = np.array(value, order="C")
        else:
            value = np.array(value, order="C", dtype=np.dtype(np.float64))

    return value
