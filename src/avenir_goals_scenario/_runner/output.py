from pathlib import Path

import h5py
import numpy as np


def write_scenario_results(
    scenario_id: int,
    pjnz_name: str,
    sim_arrays: dict[str, list[np.ndarray]],
    output_dir: Path,
) -> Path:
    """Write simulation results for one scenario/PJNZ combination to HDF5.

    Creates ``{output_dir}/{pjnz_name}/scenario_{scenario_id}.h5``.  The
    parent directory is created if it does not yet exist.

    Each indicator is stored as a single dataset whose first axis is the
    simulation index and remaining axes match the original array shape from
    ``run_goals``.  For example, a 1-D per-year indicator with 61 years and
    50 simulations is stored with shape ``(50, 61)``; a 3-D indicator with
    shape ``(sex=2, age=66, years=61)`` is stored with shape
    ``(50, 2, 66, 61)``.

    Args:
        scenario_id: Scenario identifier, used to name the output file.
        pjnz_name: Stem of the source PJNZ file (e.g. ``"country_2024"``).
            Used as the subdirectory name.
        sim_arrays: Mapping of indicator name to a list of arrays — one
            array per simulation draw, all with the same shape.
        output_dir: Root output directory (must already exist).

    Returns:
        Path to the written ``.h5`` file.
    """
    pjnz_dir = output_dir / pjnz_name
    pjnz_dir.mkdir(exist_ok=True)
    path = pjnz_dir / f"scenario_{scenario_id}.h5"

    with h5py.File(path, "w") as f:
        for indicator, arrays in sim_arrays.items():
            stacked = np.stack(arrays, axis=0)
            f.create_dataset(indicator, data=stacked)

    return path
