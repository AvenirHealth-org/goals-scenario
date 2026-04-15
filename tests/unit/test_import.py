# Constants for modvar tags
from pathlib import Path

import pytest
import SpectrumCommon.Const.DP as dpconst
import SpectrumCommon.Const.HV as hvconst
import SpectrumCommon.Const.PJ as pjconst
from Tools.ImportPJNZ.Importer import GB_ImportProjectionFromFile

from avenir_goals_scenario._runner.pjnz import find_pjnz_files, modvars_to_numpy


def test_import_from_ZAF_file(test_data):
    projection, param, epp_files, shiny90 = GB_ImportProjectionFromFile(test_data / "pjnz" / "SouthAfrica.PJNZ")
    assert projection is not None
    assert param.country == "ZAF"
    assert type(projection[dpconst.DP_TFRTag]) is list
    assert type(projection[hvconst.HVARTCoverageByRGTag]) is list
    # there is no shiny90 or epp files in this test PJNZ
    assert shiny90 is None
    assert epp_files == {}


def test_import_from_missing_file_raises(test_data):
    with pytest.raises(FileNotFoundError, match="missing\\.PJNZ"):
        GB_ImportProjectionFromFile(test_data / "pjnz" / "missing.PJNZ")


@pytest.mark.parametrize(
    "pjnz_path",
    find_pjnz_files(Path(__file__).parent.parent / "test_data" / "pjnz"),
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

    projection = modvars_to_numpy(projection)

    final_year = projection[pjconst.PJN_FinalYearTag]
    first_year = projection[pjconst.PJN_FirstYearTag]
    year_count = final_year - first_year + 1
    assert projection[dpconst.DP_TFRTag].shape == (year_count,)
    assert projection[hvconst.HVARTCoverageByRGTag].shape == (3, 11, year_count)
