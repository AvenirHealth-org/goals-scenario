import os
from contextlib import redirect_stdout
from pathlib import Path

import numpy as np
from Tools.ImportPJNZ.Importer import GB_ImportProjectionFromFile


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
    return files


def import_pjnz(path: Path) -> dict:
    """Import a PJNZ file and return its modvars dict.

    Args:
        path: Path to a ``.PJNZ`` file.

    Returns:
        Modvars dict for use with :func:`modvars_to_leapfrog`.

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
    numpy_modvars = {tag: modvars_to_numpy(tag, value) for tag, value in modvars.items()}

    return numpy_modvars


def modvars_to_numpy(tag, value):
    # Taken from FilterUtils.py in SpectrumEngine
    if type(value) is list:
        try:
            if len(value) > 0 and ((type(value[0]) is dict) or (type(value[0]) is str) or (type(value[0]) is bool)):
                value = np.array(value, order="C")
            else:
                value = np.array(value, order="C", dtype=np.dtype(np.float64))

        except Exception as _e:
            print(f"Failed to convert list to numpy array {tag}")

    return value
