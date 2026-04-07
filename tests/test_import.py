from Tools.ImportPJNZ.Importer import GB_ImportProjectionFromFile

#Constants for modvar tags
import SpectrumCommon.Const.DP as dpconst
import SpectrumCommon.Const.AM as amconst
import SpectrumCommon.Const.HV as hvconst
import SpectrumCommon.Const.RN as rnconst

def test_import_projection_from_file():
    projection, param, epp_files, shiny90 = GB_ImportProjectionFromFile(r".\tests\test_data\SouthAfrica.PJNZ")
    assert projection is not None
    assert param.country == "ZAF"
    assert type(projection[dpconst.DP_TFRTag])==list
    assert type(projection[hvconst.HVARTCoverageByRGTag])==list