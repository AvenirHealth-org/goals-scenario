# Constants for modvar tags
from pathlib import Path

import numpy as np
import pytest
import SpectrumCommon.Const.DP as dpconst
import SpectrumCommon.Const.HV as hvconst
import SpectrumCommon.Const.PJ as pjconst
from Tools.ImportPJNZ.Importer import GB_ImportProjectionFromFile


class ProjectionConversionError(ValueError):
    def __init__(self, tag: str) -> None:
        super().__init__(f"Failed to convert projection tag {tag} to numpy array.")


def _all_pjnz_files(test_dir: Path) -> list[Path]:
    return sorted(path for path in test_dir.iterdir() if path.suffix.lower() == ".pjnz")


def _convert_projection_lists_to_numpy(projection: dict) -> None:
    float_dtype = np.dtype(np.float64)

    for tag, value in projection.items():
        if not isinstance(value, list):
            continue

        try:
            if value and isinstance(value[0], (dict, str)):
                projection[tag] = np.array(value, order="C")
            else:
                projection[tag] = np.array(value, order="C", dtype=float_dtype)
        except Exception as exc:
            raise ProjectionConversionError(tag) from exc


def test_import_from_ZAF_file(test_dir):
    projection, param, epp_files, shiny90 = GB_ImportProjectionFromFile(test_dir / "SouthAfrica.PJNZ")
    assert projection is not None
    assert param.country == "ZAF"
    assert type(projection[dpconst.DP_TFRTag]) is list
    assert type(projection[hvconst.HVARTCoverageByRGTag]) is list
    # there is no shiny90 or epp files in this test PJNZ
    assert shiny90 is None
    assert epp_files == {}


def test_import_from_missing_file_raises(test_dir):
    with pytest.raises(FileNotFoundError, match="missing\\.PJNZ"):
        GB_ImportProjectionFromFile(test_dir / "missing.PJNZ")


@pytest.mark.parametrize(
    "pjnz_path",
    _all_pjnz_files(Path(__file__).parent / "test_data"),
    ids=lambda path: path.name,
)
def test_import_all_pjnz_files_in_test_dir(pjnz_path):
    projection, param, epp_files, shiny90 = GB_ImportProjectionFromFile(pjnz_path)

    assert projection is not None
    assert param.country
    assert isinstance(projection[dpconst.DP_TFRTag], list)
    assert isinstance(projection[hvconst.HVARTCoverageByRGTag], list)
    assert isinstance(epp_files, dict)
    if shiny90 is not None:
        assert isinstance(shiny90, dict)
        assert shiny90["name"]
        assert shiny90["file"]

    _convert_projection_lists_to_numpy(projection)

    final_year = projection[pjconst.PJN_FinalYearTag]
    first_year = projection[pjconst.PJN_FirstYearTag]
    year_count = final_year - first_year + 1
    assert projection[dpconst.DP_TFRTag].shape == (year_count, )
    assert projection[hvconst.HVARTCoverageByRGTag].shape == (3, 11, year_count)


