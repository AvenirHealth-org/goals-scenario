
#Constants for modvar tags
import SpectrumCommon.Const.DP as dpconst
import SpectrumCommon.Const.HV as hvconst
from Tools.ImportPJNZ.Importer import GB_ImportProjectionFromFile


def test_import_projection_from_file():
    projection, param, epp_files, shiny90 = GB_ImportProjectionFromFile(r".\tests\test_data\SouthAfrica.PJNZ")
    assert projection is not None
    assert param.country == "ZAF"
    assert type(projection[dpconst.DP_TFRTag]) is list
    assert type(projection[hvconst.HVARTCoverageByRGTag]) is list
    # there is no shiny90 or epp files in this test PJNZ
    assert shiny90 is None
    assert epp_files == {}
