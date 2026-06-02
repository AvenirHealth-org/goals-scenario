import os
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any

import numpy as np
from leapfrog_goals import get_goals_ss
from Tools.ImportPJNZ.Importer import GB_ImportProjectionFromFile

from SpectrumCommon.Util.LeapfrogDataMapping import modvars_to_leapfrog


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


def _import_pjnz_modvars(path: Path) -> dict:
    # TODO: remove this silent reading once we make GB_ImportProjectionFromFile
    # less chatty.
    with open(os.devnull, "w") as devnull, redirect_stdout(devnull):
        modvars, _params, _epp_files, _shiny90 = GB_ImportProjectionFromFile(str(path))
    if modvars is None:
        err_msg = f"Failed to import PJNZ file: {path}"
        raise ValueError(err_msg)

    return modvars_to_numpy(modvars)


def import_pjnz(path: Path) -> dict:
    """Import a PJNZ file and return leapfrog params.

    Args:
        path: Path to a ``.PJNZ`` file.

    Returns:
        Dict of parameters for leapfrog-goals.

    Raises:
        ValueError: If the PJNZ file cannot be parsed or is missing expected fields.
    """
    try:
        modvars_base = _import_pjnz_modvars(path)
        ss = get_goals_ss()
        leapfrog_params = modvars_to_leapfrog(modvars_base, ss, "Goals")
        # Temporarily add in required input data for this in-progress
        # version of leapfrog goals
        leapfrog_params["ex_input"] = np.full((ss["pAG"], ss["NS"]), 1)  # ty: ignore[no-matching-overload]
    except KeyError as exc:
        err_msg = (
            f"Failed to read expected field {exc} from {path.name}. "
            "The file may be from an unsupported Spectrum version or missing required data."
        )
        raise ValueError(err_msg) from exc

    return leapfrog_params


class ProjectionConversionError(ValueError):
    def __init__(self, tag: str) -> None:
        self.tag = tag
        super().__init__(f"Failed to convert projection tag {tag} to numpy array.")


def modvars_to_numpy(modvars: dict[str, Any]) -> dict[str, Any]:
    float_dtype = np.dtype(np.float64)

    def convert_modvar(tag: str, value: Any):
        # Taken from FilterUtils.py in SpectrumEngine
        try:
            if not isinstance(value, list):
                return value

            if value and isinstance(value[0], (dict, str, bool)):
                value = np.array(value, order="C")
            else:
                value = np.array(value, order="C", dtype=float_dtype)
        except Exception as exc:
            raise ProjectionConversionError(tag) from exc
        return value

    return {tag: convert_modvar(tag, value) for tag, value in modvars.items()}
