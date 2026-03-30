import pandas as pd
import numpy as np

from AvenirCommon.Util import findTagRow

from SpectrumCommon.Modvars.GB.GBDefs import createProjectionParams
from SpectrumCommon.Const.GB import *
from SpectrumCommon.Const.RN import *


def openRN(file, params: createProjectionParams, projection: dict):
    sheet = pd.read_csv(file, header=None, na_filter=False, encoding='utf-8')

    _import_tag_value(sheet, projection, '<ProjectionValid MV2>',          RNProjectionValidTag)
    _import_tag_value(sheet, projection, '<ProjectionValidDate MV>',       RNProjectionValidDateTag)
    _import_tag_value(sheet, projection, '<Data Source MV>',               RNDataSourceTag)
    _import_tag_value(sheet, projection, '<VariablesRW MV>',               RNVariablesRWTag)
    _import_tag_value(sheet, projection, '<MaxInterventions MV>',          RNMaxInterventionsTag)
    _import_tag_value(sheet, projection, '<MaxPOPConstants MV>',           RNMaxPOPConstantsTag)
    _import_tag_value(sheet, projection, '<MaxPSConstants MV>',            RNMaxPSConstantsTag)
    _import_tag_value(sheet, projection, '<MaxSummaryTableConstants MV>', RNMaxSummaryTableConstantsTag)
    _import_tag_value(sheet, projection, '<FirstYearOfEstimates MV>',      RNFirstYearOfEstimatesTag)
    _import_tag_value(sheet, projection, '<FirstYearOfEstimatesCBIdx MV>', RNFirstYearOfEstimatesCBIdxTag)
    import_PopulationSizes(sheet, params, projection)
    import_UserGeneralPop(sheet, params, projection)
    import_UserMostAtRiskPop(sheet, params, projection)
    import_Coverage(sheet, params, projection)
    import_UserGeneralPopCoverage(sheet, params, projection)
    import_UserMostAtRiskPopCoverage(sheet, params, projection)
    import_UseRNMData(sheet, params, projection)
    import_CurrencyForMitigationCBIdx(sheet, params, projection)
    import_PrEPCoverage(sheet, params, projection)
    import_PrEPEffectiveness(sheet, params, projection)
    import_VaccineCovType(sheet, params, projection)
    import_VacCoverage(sheet, params, projection)
    import_VaccineEffectiveness(sheet, params, projection)
    import_VaccineBehavEffect(sheet, params, projection)
    import_TypeOfVaccine(sheet, params, projection)
    import_VaccineTargeting(sheet, params, projection)
    import_CureCovType(sheet, params, projection)
    import_CureCoverage(sheet, params, projection)
    import_CureEffectiveness(sheet, params, projection)
    import_ADHTreatCov(sheet, params, projection)
    import_ADHTreatReducMort(sheet, params, projection)
    import_PointOfCare(sheet, params, projection)
    import_POCEffect(sheet, params, projection)
    import_UnitCosts(sheet, params, projection)
    import_UserGeneralPopUnitCosts(sheet, params, projection)
    import_UserMostAtRiskPopUnitCosts(sheet, params, projection)
    import_CurrencyForUnitCostsCBIdx(sheet, params, projection)
    import_PreTest(sheet, params, projection)
    import_PostTest(sheet, params, projection)
    import_PostNatal(sheet, params, projection)
    import_Mother(sheet, params, projection)
    import_PCRForInfantAfterBirth(sheet, params, projection)
    import_InfantAfterBF(sheet, params, projection)
    import_Nevirapine200(sheet, params, projection)
    import_NevirapineInfant(sheet, params, projection)
    import_AZT(sheet, params, projection)
    import_ThreeTC(sheet, params, projection)
    import_TripleTreatment(sheet, params, projection)
    import_TripleProphylaxis(sheet, params, projection)
    import_ServiceDelivery(sheet, params, projection)
    import_Formula(sheet, params, projection)
    import_FirstLineARTDrugs(sheet, params, projection)
    import_SecondLineARTDrugs(sheet, params, projection)
    import_AdditARTDrugCostsTBmale(sheet, params, projection)
    import_AdditARTDrugCostsTBfemale(sheet, params, projection)
    import_LabCostsARTTr(sheet, params, projection)
    import_DrugLabCostsTrInf(sheet, params, projection)
    import_CotrimProphylaxis(sheet, params, projection)
    import_TBProphylaxis(sheet, params, projection)
    import_NutritionSuppSixMo(sheet, params, projection)
    import_ChildrenARVDrugs(sheet, params, projection)
    import_ChildrenLabCostsARTTr(sheet, params, projection)
    import_CostPerInpatientDay(sheet, params, projection)
    import_CostPerOutpatientDay(sheet, params, projection)
    import_ARTinpatientDays(sheet, params, projection)
    import_ARToutpatientDays(sheet, params, projection)
    import_OItreatmentInpatientDays(sheet, params, projection)
    import_OItreatmentOutpatientDays(sheet, params, projection)
    import_MigFirstToSecondLine(sheet, params, projection)
    import_TestAndVisitSchedule(sheet, params, projection)
    import_ARTUnitCosts(sheet, params, projection)
    import_PercentOnART(sheet, params, projection)
    import_CurrencyForProgramSupportCBIdx(sheet, params, projection)
    import_ProgramSupport(sheet, params, projection)
    import_UserProgramSupport(sheet, params, projection)
    import_MitigationProgramsEntered(sheet, params, projection)
    import_Mitigation(sheet, params, projection)
    import_MethodMix(sheet, params, projection)
    import_CurrencyDisplayedCBIdx(sheet, params, projection)
    import_ResourcesRequired(sheet, params, projection)
    import_NumberPeopleReached(sheet, params, projection)
    import_PMTCTCosts(sheet, params, projection)
    import_TotalCosts(sheet, params, projection)
    import_OptimizerVars(sheet, params, projection)

    return None


############### Start reading in RN Modvars ######################################


def _parse_value(value):
    if value == '':
        return value

    text = str(value).strip()
    if text == '':
        return ''

    if text.isdigit() or (text.startswith('-') and text[1:].isdigit()):
        try:
            return int(text)
        except ValueError:
            pass

    try:
        return float(text)
    except ValueError:
        return value


def _to_float(value, default=0.0):
    if value == '' or value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _import_tag_value(sheet, projection, source_tag: str, projection_tag: str):
    modvarTagRow = findTagRow(sheet, source_tag)
    if modvarTagRow is None or modvarTagRow < 0:
        return

    row = modvarTagRow + 2
    projection[projection_tag] = _parse_value(sheet.values[row, GB_RW_DataStartCol])


def _get_rn_year_index_bounds(params):
    """Return (calc_year_idx, final_index) based on projection params.

    Mirrors Delphi's GetGBCalcYearIdx / GetGBFinalYearIdx: both are
    offsets from GB_NativeYear (1970).
    """
    calc_year_idx = max(0, int(params.firstYear) - GB_NativeYear)
    final_index = max(calc_year_idx, int(params.finalYear) - GB_NativeYear)
    return calc_year_idx, final_index


def _read_rn_year_row(sheet, row, calc_year_idx, final_index,
                      start_col=GB_RW_DataStartCol):
    """Read one row of year data into a list indexed [0..final_index].

    Cells are consumed sequentially from *start_col*; empty cells repeat
    the previous value (flatline), matching Delphi's t2+1..t3 extension.
    """
    values = [0.0] * (final_index + 1)
    col = start_col
    last_value = 0.0
    print(sheet.values[row, col:])
    for t in range(calc_year_idx, final_index + 1):
        cell_value = sheet.values[row, col]
        if cell_value != '':
            last_value = _to_float(_parse_value(cell_value), last_value)
            col += 1
        else:
            pass
        values[t] = last_value
    return values


def _read_rn_year_row_contiguous(sheet, row, calc_year_idx, final_index,
                                 start_col=GB_RW_DataStartCol):
    """Read one row of contiguous year columns into [0..final_index]."""
    values = [0.0] * (final_index + 1)
    col = start_col
    for t in range(calc_year_idx, final_index + 1):
        values[t] = _to_float(_parse_value(sheet.values[row, col]))
        col += 1
    return values


def import_PopulationSizes(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<PopulationSizes MV2>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_rn_year_index_bounds(params)

    # Row layout after the tag:
    #   tagRow+1  description row
    #   tagRow+2  header row (Name / Master ID / year labels)  <- Inc(currRow) in Delphi
    #   tagRow+3  first data row
    row = modvarTagRow + 3

    # Use MaxPOPConstants recorded by import_MaxPOPConstants if available,
    # otherwise fall back to the compiled-in constant.
    max_pop = projection.get(RNMaxPOPConstantsTag, RN_POP_MaxPopulations)
    try:
        max_pop = int(max_pop)
    except (TypeError, ValueError):
        max_pop = RN_POP_MaxPopulations

    # Delphi stores Value[CurrID, t]; we key by MstID because Python has
    # no GetRN_POPConstantCurrID mapping.  Consumers look up by MstID.
    result = {}
    for _ in range(max_pop):
        mst_id = _parse_value(sheet.values[row, GB_RW_DataStartCol])
        if mst_id == '' or mst_id is None:
            break
        # c1 = GB_RW_DataStartCol + 1 (year data is one column to the right
        # of the Master ID column, matching Delphi's GetGBYearAndColIndices
        # call with GB_RW_DataStartCol + 1).
        year_data = _read_rn_year_row(sheet, row, calc_year_idx, final_index,
                                      start_col=GB_RW_DataStartCol + 1)
        result[int(mst_id)] = year_data
        row += 1

    projection[RNPopulationSizesTag] = result


def import_UserGeneralPop(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<UserGeneralPop MV2>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_rn_year_index_bounds(params)

    # Delphi layout after tag row:
    #   tagRow+1  count at GB_RW_DataStartCol           (Inc → read count)
    #   tagRow+2  (skipped)                             (Inc)
    #   tagRow+3  first object: name / PerNum / Value   (Inc → first obj)
    #   tagRow+4  ResourcesRequired year data
    #   tagRow+5  NumberPeopleReached year data
    #   (repeat for each subsequent object)
    count = _parse_value(sheet.values[modvarTagRow + 1, GB_RW_DataStartCol])
    try:
        count = int(count)
    except (TypeError, ValueError):
        count = 0

    row = modvarTagRow + 3
    result = []
    for _ in range(count):
        obj = {
            'UserGenPop': sheet.values[row, GB_RW_DataStartCol],
            'PerNum':     _parse_value(sheet.values[row, GB_RW_DataStartCol + 1]),
            'Value':      _to_float(_parse_value(sheet.values[row, GB_RW_DataStartCol + 2])),
        }
        row += 1
        obj['ResourcesRequired']  = _read_rn_year_row(sheet, row, calc_year_idx, final_index)
        row += 1
        obj['NumberPeopleReached'] = _read_rn_year_row(sheet, row, calc_year_idx, final_index)
        row += 1
        result.append(obj)

    projection[RNUserGeneralPopTag] = result


def import_UserMostAtRiskPop(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<UserMostAtRiskPop MV2>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_rn_year_index_bounds(params)

    # Identical layout to UserGeneralPop:
    #   tagRow+1  count at GB_RW_DataStartCol
    #   tagRow+2  (skipped - "Skip Text")
    #   tagRow+3  first object: UserMARPop / PerNum / Value
    #   tagRow+4  ResourcesRequired year data
    #   tagRow+5  NumberPeopleReached year data
    count = _parse_value(sheet.values[modvarTagRow + 1, GB_RW_DataStartCol])
    try:
        count = int(count)
    except (TypeError, ValueError):
        count = 0

    row = modvarTagRow + 3
    result = []
    for _ in range(count):
        obj = {
            'UserMARPop': sheet.values[row, GB_RW_DataStartCol],
            'PerNum':     _parse_value(sheet.values[row, GB_RW_DataStartCol + 1]),
            'Value':      _to_float(_parse_value(sheet.values[row, GB_RW_DataStartCol + 2])),
        }
        row += 1
        obj['ResourcesRequired']   = _read_rn_year_row(sheet, row, calc_year_idx, final_index)
        row += 1
        obj['NumberPeopleReached'] = _read_rn_year_row(sheet, row, calc_year_idx, final_index)
        row += 1
        result.append(obj)

    projection[RNUserMostAtRiskPopTag] = result


def import_Coverage(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<Coverage MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_rn_year_index_bounds(params)

    # Row layout:
    #   tagRow+1  description row
    #   tagRow+2  header strings row  <- Inc(currRow) in Delphi
    #   tagRow+3  first data row
    # Loop count: MaxInterventions - RN_NumIntervExcludedFromCov
    # MstID at GB_RW_DataStartCol (col 3); year data at GB_RW_DataStartCol+1 (col 4)
    max_interventions = projection.get(RNMaxInterventionsTag, RN_MaxInterventions)
    try:
        max_interventions = int(max_interventions)
    except (TypeError, ValueError):
        max_interventions = RN_MaxInterventions

    count = max_interventions - len(RN_NotInCov)
    row = modvarTagRow + 3
    result = {}
    for _ in range(count):
        mst_id = _parse_value(sheet.values[row, GB_RW_DataStartCol])
        if mst_id != '' and mst_id is not None and mst_id != 0:
            year_data = _read_rn_year_row(sheet, row, calc_year_idx, final_index,
                                          start_col=GB_RW_DataStartCol + 1)
            result[int(mst_id)] = year_data
        row += 1

    projection[RNCoverageTag] = result


def import_UserGeneralPopCoverage(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<UserGeneralPopCoverage MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_rn_year_index_bounds(params)

    # Delphi layout after tag row:
    #   tagRow+1  count at GB_RW_DataStartCol
    #   tagRow+2  (skipped)
    #   tagRow+3  first data row: UserGenPop + year values
    count = _parse_value(sheet.values[modvarTagRow + 1, GB_RW_DataStartCol])
    try:
        count = int(count)
    except (TypeError, ValueError):
        count = 0

    row = modvarTagRow + 3
    result = []
    for _ in range(count):
        obj = {
            'UserGenPop': sheet.values[row, GB_RW_DataStartCol],
            'Value': _read_rn_year_row(sheet, row, calc_year_idx, final_index,
                                       start_col=GB_RW_DataStartCol + 1),
        }
        result.append(obj)
        row += 1

    projection[RNUserGeneralPopCoverageTag] = result


def import_UserMostAtRiskPopCoverage(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<UserMostAtRiskPopCoverage MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_rn_year_index_bounds(params)

    # Delphi layout after tag row:
    #   tagRow+1  count at GB_RW_DataStartCol
    #   tagRow+2  (skipped)
    #   tagRow+3  first data row: UserMARPop + year values
    count = _parse_value(sheet.values[modvarTagRow + 1, GB_RW_DataStartCol])
    try:
        count = int(count)
    except (TypeError, ValueError):
        count = 0

    row = modvarTagRow + 3
    result = []
    for _ in range(count):
        obj = {
            'UserMARPop': sheet.values[row, GB_RW_DataStartCol],
            'Value': _read_rn_year_row(sheet, row, calc_year_idx, final_index,
                                       start_col=GB_RW_DataStartCol + 1),
        }
        result.append(obj)
        row += 1

    projection[RNUserMostAtRiskPopCoverageTag] = result


def import_UseRNMData(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<UseRNMData MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    row = modvarTagRow + 2
    value = _parse_value(sheet.values[row, GB_RW_DataStartCol])
    if isinstance(value, str):
        normalized = value.strip().lower()
        projection[RNUseRNMDataTag] = normalized in ('1', 'true', 'yes', 'y')
    else:
        projection[RNUseRNMDataTag] = bool(value)


def import_CurrencyForMitigationCBIdx(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<CurrencyForMitigationCBIdx MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    row = modvarTagRow + 2
    value = _parse_value(sheet.values[row, GB_RW_DataStartCol])
    try:
        projection[RNCurrencyForMitigationCBIdxTag] = int(value)
    except (TypeError, ValueError):
        projection[RNCurrencyForMitigationCBIdxTag] = 0


def import_PrEPCoverage(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<PrEPCoverage MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_rn_year_index_bounds(params)

    # Delphi starts with Inc(currRow), then reads male rows followed by female rows.
    row = modvarTagRow + 2
    result = {
        RN_Male: {},
        RN_Female: {},
    }

    for r in range(RN_LRH, RN_MSMIDU + 1):
        result[RN_Male][r] = _read_rn_year_row_contiguous(
            sheet, row, calc_year_idx, final_index, start_col=GB_RW_DataStartCol
        )
        row += 1

    for r in range(RN_LRH, RN_IDU + 1):
        result[RN_Female][r] = _read_rn_year_row_contiguous(
            sheet, row, calc_year_idx, final_index, start_col=GB_RW_DataStartCol
        )
        row += 1

    projection[RNPrEPCoverageTag] = result


def import_PrEPEffectiveness(sheet, params, projection):
    tag_row_mv3 = findTagRow(sheet, '<PrEPEffectiveness MV3>')
    tag_row_mv2 = findTagRow(sheet, '<PrEPEffectiveness MV2>')
    tag_row_mv1 = findTagRow(sheet, '<PrEPEffectiveness MV>')

    result = {}

    def _set_eff(effect_id, intervention_id, value):
        if effect_id not in result:
            result[effect_id] = {}
        result[effect_id][intervention_id] = value

    if tag_row_mv3 is not None and tag_row_mv3 >= 0:
        row = tag_row_mv3 + 2
        while sheet.values[row, GB_RW_TagCol] != '<End>':
            mst_id = _parse_value(sheet.values[row, GB_RW_DataStartCol])
            if mst_id == '' or mst_id is None:
                break
            try:
                mst_id = int(mst_id)
            except (TypeError, ValueError):
                row += 1
                continue

            for e in range(RN_Effectiveness, RN_DurationMonths + 1):
                _set_eff(e, mst_id, _to_float(_parse_value(sheet.values[row, GB_RW_DataStartCol + e])))
            row += 1

    elif tag_row_mv2 is not None and tag_row_mv2 >= 0:
        row = tag_row_mv2 + 2
        while sheet.values[row, GB_RW_TagCol] != '<End>':
            mst_id = _parse_value(sheet.values[row, GB_RW_DataStartCol])
            if mst_id == '' or mst_id is None:
                break
            try:
                mst_id = int(mst_id)
            except (TypeError, ValueError):
                row += 1
                continue

            for e in range(RN_Effectiveness, RN_Substitution + 1):
                _set_eff(e, mst_id, _to_float(_parse_value(sheet.values[row, GB_RW_DataStartCol + e])))
            row += 1

    elif tag_row_mv1 is not None and tag_row_mv1 >= 0:
        row = tag_row_mv1 + 2
        for e in range(RN_Effectiveness, RN_Adherence + 1):
            for m in (RN_PrEPOralDaily, RN_PrEPInject1Mo, RN_PrEPRing):
                _set_eff(e, m, _to_float(_parse_value(sheet.values[row, GB_RW_DataStartCol])))
                row += 1
                # Delphi skips deprecated gel row after Inject 1-month.
                if m == RN_PrEPInject1Mo:
                    row += 1

    else:
        return

    projection[RNPrEPEffectivenessTag] = result


def import_VaccineCovType(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<VaccineCovType MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    row = modvarTagRow + 2
    value = _parse_value(sheet.values[row, GB_RW_DataStartCol])
    try:
        projection[RNVaccineCovTypeTag] = int(value)
    except (TypeError, ValueError):
        projection[RNVaccineCovTypeTag] = 0


def import_VacCoverage(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<VacCoverage MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_rn_year_index_bounds(params)

    # Delphi skips one row, then reads RN_AllRisk..RN_MSM_F with an extra
    # row skip when crossing to female aggregate (RN_AllRisk_F).
    row = modvarTagRow + 3
    result = np.zeros((RN_MSM_F + 1, final_index + 1))
    for r in range(RN_AllRisk, RN_MSM_F + 1):
        if r == RN_AllRisk_F:
            row += 1
        result[r] = _read_rn_year_row_contiguous(
            sheet, row, calc_year_idx, final_index, start_col=GB_RW_DataStartCol
        )
        row += 1

    projection[RNVacCoverageTag] = result


def import_VaccineEffectiveness(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<VaccineEffectiveness MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    # Delphi reads each parameter as: skip label row, then read value row.
    row = modvarTagRow + 1
    result = np.zeros(RN_Duration + 1)
    for r in range(RN_Efficacy, RN_Duration + 1):
        row += 1
        result[r] = _to_float(_parse_value(sheet.values[row, GB_RW_DataStartCol]))
        row += 1

    projection[RNVaccineEffectivenessTag] = result


def import_VaccineBehavEffect(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<VaccineBehavEffect MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    row = modvarTagRow + 2
    projection[RNVaccineBehavEffectTag] = {
        RN_AmongVacc: _to_float(_parse_value(sheet.values[row, GB_RW_DataStartCol])),
        RN_AmongAdults: _to_float(_parse_value(sheet.values[row + 1, GB_RW_DataStartCol])),
    }


def import_TypeOfVaccine(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<TypeOfVaccine MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    row = modvarTagRow + 2
    value = _parse_value(sheet.values[row, GB_RW_DataStartCol])
    try:
        projection[RNTypeOfVaccineTag] = int(value)
    except (TypeError, ValueError):
        projection[RNTypeOfVaccineTag] = 0


def import_VaccineTargeting(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<VaccineTargeting MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    row = modvarTagRow + 2
    value = _parse_value(sheet.values[row, GB_RW_DataStartCol])
    try:
        projection[RNVaccineTargetingTag] = int(value)
    except (TypeError, ValueError):
        projection[RNVaccineTargetingTag] = 0


def import_CureCovType(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<CureCovType MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    row = modvarTagRow + 2
    value = _parse_value(sheet.values[row, GB_RW_DataStartCol])
    try:
        projection[RNCureCovTypeTag] = int(value)
    except (TypeError, ValueError):
        projection[RNCureCovTypeTag] = 0


def import_CureCoverage(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<CureCoverage MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_rn_year_index_bounds(params)

    # Same Delphi layout/pattern as vaccine coverage.
    row = modvarTagRow + 3
    result = np.zeros((RN_MSM_F + 1, final_index + 1))
    for r in range(RN_AllRisk, RN_MSM_F + 1):
        if r == RN_AllRisk_F:
            row += 1
        result[r] = _read_rn_year_row_contiguous(
            sheet, row, calc_year_idx, final_index, start_col=GB_RW_DataStartCol
        )
        row += 1

    projection[RNCureCoverageTag] = result


def import_CureEffectiveness(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<CureEffectiveness MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    # Same Delphi layout/pattern as vaccine effectiveness.
    row = modvarTagRow + 1
    result = np.zeros(RN_Duration + 1)
    for r in range(RN_Efficacy, RN_Duration + 1):
        row += 1
        result[r] = _to_float(_parse_value(sheet.values[row, GB_RW_DataStartCol]))
        row += 1

    projection[RNCureEffectivenessTag] = result


def import_ADHTreatCov(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<ADHTreatCov MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_rn_year_index_bounds(params)

    row = modvarTagRow + 2
    projection[RNADHTreatCovTag] = _read_rn_year_row_contiguous(
        sheet, row, calc_year_idx, final_index, start_col=GB_RW_DataStartCol
    )


def import_ADHTreatReducMort(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<ADHTreatReducMort MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    row = modvarTagRow + 2
    projection[RNADHTreatReducMortTag] = _to_float(_parse_value(sheet.values[row, GB_RW_DataStartCol]))


def import_PointOfCare(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<PointOfCare MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_rn_year_index_bounds(params)

    # Delphi POCCoverage reads two rows: CD4 and VL, each with year values.
    row = modvarTagRow + 2
    result = np.zeros((RN_POC_VL + 1, final_index + 1))
    for r in range(RN_POC_CD4, RN_POC_VL + 1):
        result[r] = _read_rn_year_row_contiguous(
            sheet, row, calc_year_idx, final_index, start_col=GB_RW_DataStartCol
        )
        row += 1

    projection[RNPointOfCareTag] = result


def import_POCEffect(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<POCEffect MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    row = modvarTagRow + 2
    # Delphi stores this as value[POCType, effectCol], with effectCol fixed at 1.
    projection[RNPOCEffectTag] = {
        RN_POC_CD4: _to_float(_parse_value(sheet.values[row, GB_RW_DataStartCol])),
        RN_POC_VL: _to_float(_parse_value(sheet.values[row + 1, GB_RW_DataStartCol])),
    }


def import_UnitCosts(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<UnitCosts MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_rn_year_index_bounds(params)

    # Delphi skips header row, then loops MaxInterventionsRW - excluded-from-UC.
    max_interventions = projection.get(RNMaxInterventionsTag, RN_MaxInterventions)
    try:
        max_interventions = int(max_interventions)
    except (TypeError, ValueError):
        max_interventions = RN_MaxInterventions

    count = max_interventions - RN_NumIntervExcludedFromUC
    row = modvarTagRow + 3
    result = {}
    for _ in range(count):
        mst_id = _parse_value(sheet.values[row, GB_RW_DataStartCol])
        if mst_id != '' and mst_id is not None:
            try:
                key = int(mst_id)
            except (TypeError, ValueError):
                key = mst_id
            result[key] = _read_rn_year_row_contiguous(
                sheet, row, calc_year_idx, final_index, start_col=GB_RW_DataStartCol + 1
            )
        row += 1

    projection[RNUnitCostsTag] = result


def import_UserGeneralPopUnitCosts(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<UserGeneralPopUnitCosts MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_rn_year_index_bounds(params)

    # Delphi layout after tag row:
    #   tagRow+1  count
    #   tagRow+2  skipped
    #   tagRow+3  first data row: UserGenPop + year values
    count = _parse_value(sheet.values[modvarTagRow + 1, GB_RW_DataStartCol])
    try:
        count = int(count)
    except (TypeError, ValueError):
        count = 0

    row = modvarTagRow + 3
    result = []
    for _ in range(count):
        obj = {
            'UserGenPop': sheet.values[row, GB_RW_DataStartCol],
            'Value': _read_rn_year_row_contiguous(
                sheet, row, calc_year_idx, final_index, start_col=GB_RW_DataStartCol + 1
            ),
        }
        result.append(obj)
        row += 1

    projection[RNUserGeneralPopUnitCostsTag] = result


def import_UserMostAtRiskPopUnitCosts(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<UserMostAtRiskPopUnitCosts MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_rn_year_index_bounds(params)

    count = _parse_value(sheet.values[modvarTagRow + 1, GB_RW_DataStartCol])
    try:
        count = int(count)
    except (TypeError, ValueError):
        count = 0

    row = modvarTagRow + 3
    result = []
    for _ in range(count):
        obj = {
            'UserMARPop': sheet.values[row, GB_RW_DataStartCol],
            'Value': _read_rn_year_row_contiguous(
                sheet, row, calc_year_idx, final_index, start_col=GB_RW_DataStartCol + 1
            ),
        }
        result.append(obj)
        row += 1

    projection[RNUserMostAtRiskPopUnitCostsTag] = result


def import_CurrencyForUnitCostsCBIdx(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<CurrencyForUnitCostsCBIdx MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    row = modvarTagRow + 2
    value = _parse_value(sheet.values[row, GB_RW_DataStartCol])
    try:
        projection[RNCurrencyForUnitCostsCBIdxTag] = int(value)
    except (TypeError, ValueError):
        projection[RNCurrencyForUnitCostsCBIdxTag] = 0


def import_PreTest(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<PreTest MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_rn_year_index_bounds(params)

    row = modvarTagRow + 2
    projection[RNPreTestTag] = _read_rn_year_row_contiguous(
        sheet, row, calc_year_idx, final_index, start_col=GB_RW_DataStartCol
    )


def import_PostTest(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<PostTest MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_rn_year_index_bounds(params)

    row = modvarTagRow + 2
    projection[RNPostTestTag] = _read_rn_year_row_contiguous(
        sheet, row, calc_year_idx, final_index, start_col=GB_RW_DataStartCol
    )


def import_PostNatal(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<PostNatal MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_rn_year_index_bounds(params)

    row = modvarTagRow + 2
    projection[RNPostNatalTag] = _read_rn_year_row_contiguous(
        sheet, row, calc_year_idx, final_index, start_col=GB_RW_DataStartCol
    )


def import_Mother(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<Mother MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_rn_year_index_bounds(params)

    row = modvarTagRow + 2
    projection[RNMotherTag] = _read_rn_year_row_contiguous(
        sheet, row, calc_year_idx, final_index, start_col=GB_RW_DataStartCol
    )


def import_PCRForInfantAfterBirth(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<PCRForInfantAfterBirth MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_rn_year_index_bounds(params)

    row = modvarTagRow + 2
    projection[RNPCRForInfantAfterBirthTag] = _read_rn_year_row_contiguous(
        sheet, row, calc_year_idx, final_index, start_col=GB_RW_DataStartCol
    )


def import_InfantAfterBF(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<InfantAfterBF MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_rn_year_index_bounds(params)

    row = modvarTagRow + 2
    projection[RNInfantAfterBFTag] = _read_rn_year_row_contiguous(
        sheet, row, calc_year_idx, final_index, start_col=GB_RW_DataStartCol
    )


def import_Nevirapine200(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<Nevirapine200 MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_rn_year_index_bounds(params)

    row = modvarTagRow + 2
    projection[RNNevirapine200Tag] = _read_rn_year_row_contiguous(
        sheet, row, calc_year_idx, final_index, start_col=GB_RW_DataStartCol
    )


def import_NevirapineInfant(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<NevirapineInfant MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_rn_year_index_bounds(params)

    row = modvarTagRow + 2
    projection[RNNevirapineInfantTag] = _read_rn_year_row_contiguous(
        sheet, row, calc_year_idx, final_index, start_col=GB_RW_DataStartCol
    )


def import_AZT(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<AZT MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_rn_year_index_bounds(params)

    row = modvarTagRow + 2
    projection[RNAZTTag] = _read_rn_year_row_contiguous(
        sheet, row, calc_year_idx, final_index, start_col=GB_RW_DataStartCol
    )


def import_ThreeTC(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<ThreeTC MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_rn_year_index_bounds(params)

    row = modvarTagRow + 2
    projection[RNThreeTCTag] = _read_rn_year_row_contiguous(
        sheet, row, calc_year_idx, final_index, start_col=GB_RW_DataStartCol
    )


def import_TripleTreatment(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<TripleTreatment MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_rn_year_index_bounds(params)

    row = modvarTagRow + 2
    projection[RNTripleTreatmentTag] = _read_rn_year_row_contiguous(
        sheet, row, calc_year_idx, final_index, start_col=GB_RW_DataStartCol
    )


def import_TripleProphylaxis(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<TripleProphylaxis MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_rn_year_index_bounds(params)

    row = modvarTagRow + 2
    projection[RNTripleProphylaxisTag] = _read_rn_year_row_contiguous(
        sheet, row, calc_year_idx, final_index, start_col=GB_RW_DataStartCol
    )


def import_ServiceDelivery(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<ServiceDelivery MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_rn_year_index_bounds(params)

    row = modvarTagRow + 2
    projection[RNServiceDeliveryTag] = _read_rn_year_row_contiguous(
        sheet, row, calc_year_idx, final_index, start_col=GB_RW_DataStartCol
    )


def import_Formula(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<Formula MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_rn_year_index_bounds(params)

    row = modvarTagRow + 2
    projection[RNFormulaTag] = _read_rn_year_row_contiguous(
        sheet, row, calc_year_idx, final_index, start_col=GB_RW_DataStartCol
    )


def import_FirstLineARTDrugs(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<FirstLineARTDrugs MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_rn_year_index_bounds(params)

    row = modvarTagRow + 2
    projection[RNFirstLineARTDrugsTag] = _read_rn_year_row_contiguous(
        sheet, row, calc_year_idx, final_index, start_col=GB_RW_DataStartCol
    )


def import_SecondLineARTDrugs(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<SecondLineARTDrugs MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_rn_year_index_bounds(params)

    row = modvarTagRow + 2
    projection[RNSecondLineARTDrugsTag] = _read_rn_year_row_contiguous(
        sheet, row, calc_year_idx, final_index, start_col=GB_RW_DataStartCol
    )


def import_AdditARTDrugCostsTBmale(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<AdditARTDrugCostsTBmale MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_rn_year_index_bounds(params)

    row = modvarTagRow + 2
    projection[RNAdditARTDrugCostsTBmaleTag] = _read_rn_year_row_contiguous(
        sheet, row, calc_year_idx, final_index, start_col=GB_RW_DataStartCol
    )


def import_AdditARTDrugCostsTBfemale(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<AdditARTDrugCostsTBfemale MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_rn_year_index_bounds(params)

    row = modvarTagRow + 2
    projection[RNAdditARTDrugCostsTBfemaleTag] = _read_rn_year_row_contiguous(
        sheet, row, calc_year_idx, final_index, start_col=GB_RW_DataStartCol
    )


def import_LabCostsARTTr(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<LabCostsARTTr MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_rn_year_index_bounds(params)

    row = modvarTagRow + 2
    projection[RNLabCostsARTTrTag] = _read_rn_year_row_contiguous(
        sheet, row, calc_year_idx, final_index, start_col=GB_RW_DataStartCol
    )


def import_DrugLabCostsTrInf(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<DrugLabCostsTrInf MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_rn_year_index_bounds(params)

    row = modvarTagRow + 2
    projection[RNDrugLabCostsTrInfTag] = _read_rn_year_row_contiguous(
        sheet, row, calc_year_idx, final_index, start_col=GB_RW_DataStartCol
    )


def import_CotrimProphylaxis(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<CotrimProphylaxis MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_rn_year_index_bounds(params)

    row = modvarTagRow + 2
    projection[RNCotrimProphylaxisTag] = _read_rn_year_row_contiguous(
        sheet, row, calc_year_idx, final_index, start_col=GB_RW_DataStartCol
    )


def import_TBProphylaxis(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<TBProphylaxis MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_rn_year_index_bounds(params)

    row = modvarTagRow + 2
    projection[RNTBProphylaxisTag] = _read_rn_year_row_contiguous(
        sheet, row, calc_year_idx, final_index, start_col=GB_RW_DataStartCol
    )


def import_NutritionSuppSixMo(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<NutritionSuppSixMo MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_rn_year_index_bounds(params)

    row = modvarTagRow + 2
    projection[RNNutritionSuppSixMoTag] = _read_rn_year_row_contiguous(
        sheet, row, calc_year_idx, final_index, start_col=GB_RW_DataStartCol
    )


def import_ChildrenARVDrugs(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<ChildrenARVDrugs MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_rn_year_index_bounds(params)

    row = modvarTagRow + 2
    projection[RNChildrenARVDrugsTag] = _read_rn_year_row_contiguous(
        sheet, row, calc_year_idx, final_index, start_col=GB_RW_DataStartCol
    )


def import_ChildrenLabCostsARTTr(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<ChildrenLabCostsARTTr MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_rn_year_index_bounds(params)

    row = modvarTagRow + 2
    projection[RNChildrenLabCostsARTTrTag] = _read_rn_year_row_contiguous(
        sheet, row, calc_year_idx, final_index, start_col=GB_RW_DataStartCol
    )


def import_CostPerInpatientDay(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<CostPerInpatientDay MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_rn_year_index_bounds(params)

    row = modvarTagRow + 2
    projection[RNCostPerInpatientDayTag] = _read_rn_year_row_contiguous(
        sheet, row, calc_year_idx, final_index, start_col=GB_RW_DataStartCol
    )


def import_CostPerOutpatientDay(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<CostPerOutpatientDay MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_rn_year_index_bounds(params)

    row = modvarTagRow + 2
    projection[RNCostPerOutpatientDayTag] = _read_rn_year_row_contiguous(
        sheet, row, calc_year_idx, final_index, start_col=GB_RW_DataStartCol
    )


def import_ARTinpatientDays(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<ARTinpatientDays MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_rn_year_index_bounds(params)

    row = modvarTagRow + 2
    projection[RNARTinpatientDaysTag] = _read_rn_year_row_contiguous(
        sheet, row, calc_year_idx, final_index, start_col=GB_RW_DataStartCol
    )


def import_ARToutpatientDays(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<ARToutpatientDays MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_rn_year_index_bounds(params)

    row = modvarTagRow + 2
    projection[RNARToutpatientDaysTag] = _read_rn_year_row_contiguous(
        sheet, row, calc_year_idx, final_index, start_col=GB_RW_DataStartCol
    )


def import_OItreatmentInpatientDays(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<OItreatmentInpatientDays MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_rn_year_index_bounds(params)

    row = modvarTagRow + 2
    projection[RNOItreatmentInpatientDaysTag] = _read_rn_year_row_contiguous(
        sheet, row, calc_year_idx, final_index, start_col=GB_RW_DataStartCol
    )


def import_OItreatmentOutpatientDays(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<OItreatmentOutpatientDays MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_rn_year_index_bounds(params)

    row = modvarTagRow + 2
    projection[RNOItreatmentOutpatientDaysTag] = _read_rn_year_row_contiguous(
        sheet, row, calc_year_idx, final_index, start_col=GB_RW_DataStartCol
    )


def import_MigFirstToSecondLine(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<MigFirstToSecondLine MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_rn_year_index_bounds(params)

    # Delphi does an initial Inc(currRow) before reading this year row.
    row = modvarTagRow + 3
    projection[RNMigFirstToSecondLineTag] = _read_rn_year_row_contiguous(
        sheet, row, calc_year_idx, final_index, start_col=GB_RW_DataStartCol
    )


def import_TestAndVisitSchedule(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<TestAndVisitSchedule MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    row = modvarTagRow + 3
    result = np.zeros((RN_PregnantWomen + 1, RN_EID + 1))

    for i in range(RN_PatientsInitiatingART, RN_PregnantWomen + 1):
        for j in range(RN_CD4Test, RN_EID + 1):
            is_preg_excluded = i == RN_PregnantWomen and j in (
                RN_CD4Test, RN_ViralLoadTests, RN_DrugDelivAdherenceVisits
            )
            is_eid_excluded = (
                RN_PatientsInitiatingART <= i <= RN_PatientsNotVirallySuppressed
                and j == RN_EID
            )
            if is_preg_excluded or is_eid_excluded:
                continue

            result[i][j] = _to_float(_parse_value(sheet.values[row, GB_RW_DataStartCol]))
            row += 1

    projection[RNTestAndVisitScheduleTag] = result


def import_ARTUnitCosts(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<ARTUnitCosts MV2>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_rn_year_index_bounds(params)

    row = modvarTagRow + 3
    result = np.zeros((RN_CostOfThirdLineARVs + 1, final_index + 1))
    for i in range(RN_CostPerCD4Test, RN_CostOfThirdLineARVs + 1):
        result[i] = _read_rn_year_row_contiguous(
            sheet, row, calc_year_idx, final_index, start_col=GB_RW_DataStartCol
        )
        row += 1

    projection[RNARTUnitCostsTag] = result


def import_PercentOnART(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<PercentOnART MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_rn_year_index_bounds(params)

    row = modvarTagRow + 3
    result = np.zeros((RN_PercentPatientsThirdLine + 1, final_index + 1))
    for i in range(RN_PercentPatientsSecondLine, RN_PercentPatientsThirdLine + 1):
        result[i] = _read_rn_year_row_contiguous(
            sheet, row, calc_year_idx, final_index, start_col=GB_RW_DataStartCol
        )
        row += 1

    projection[RNPercentOnARTTag] = result


def import_CurrencyForProgramSupportCBIdx(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<CurrencyForProgramSupportCBIdx MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    row = modvarTagRow + 2
    value = _parse_value(sheet.values[row, GB_RW_DataStartCol])
    try:
        projection[RNCurrencyForProgramSupportCBIdxTag] = int(value)
    except (TypeError, ValueError):
        projection[RNCurrencyForProgramSupportCBIdxTag] = 0


def import_ProgramSupport(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<ProgramSupport MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_rn_year_index_bounds(params)

    max_ps_constants = projection.get(RNMaxPSConstantsTag, RN_PS_MaxProgramSupport)
    try:
        max_ps_constants = int(max_ps_constants)
    except (TypeError, ValueError):
        max_ps_constants = RN_PS_MaxProgramSupport

    row = modvarTagRow + 3
    values = {}
    options = {}

    for k in range(RN_Number, RN_Percent + 1):
        for i in range(1, max_ps_constants + 1):
            support_id = _parse_value(sheet.values[row, GB_RW_DataStartCol])
            try:
                support_id = int(support_id)
            except (TypeError, ValueError):
                support_id = i

            option_val = _parse_value(sheet.values[row, GB_RW_DataStartCol + 1])
            try:
                options[support_id] = int(option_val)
            except (TypeError, ValueError):
                options[support_id] = RN_Percent

            if support_id not in values:
                values[support_id] = {}

            values[support_id][k] = _read_rn_year_row_contiguous(
                sheet, row, calc_year_idx, final_index, start_col=GB_RW_DataStartCol + 2
            )
            row += 1

    projection[RNProgramSupportTag] = {
        'Values': values,
        'Options': options,
    }


def import_UserProgramSupport(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<UserProgramSupport MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_rn_year_index_bounds(params)

    count = _parse_value(sheet.values[modvarTagRow + 2, GB_RW_DataStartCol])
    try:
        count = int(count)
    except (TypeError, ValueError):
        count = 0

    row = modvarTagRow + 4
    result = []

    for k in range(RN_Number, RN_Percent + 1):
        for i in range(count):
            if k == RN_Number:
                support_function = sheet.values[row, GB_RW_DataStartCol]
                obj = {
                    'SupportFunction': support_function,
                    'Value': {},
                    'Option': RN_Percent,
                }
                result.append(obj)
            else:
                obj = result[i]

            obj['Value'][k] = _read_rn_year_row_contiguous(
                sheet, row, calc_year_idx, final_index, start_col=GB_RW_DataStartCol + 1
            )
            row += 1

    row += 1
    for i in range(count):
        option_value = RN_Percent
        for t in range(calc_year_idx, final_index + 1):
            parsed = _parse_value(sheet.values[row, GB_RW_DataStartCol + 1 + (t - calc_year_idx)])
            try:
                option_value = int(parsed)
            except (TypeError, ValueError):
                pass
        result[i]['Option'] = option_value
        row += 1

    projection[RNUserProgramSupportTag] = result


def import_MitigationProgramsEntered(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<MitigationProgramsEntered MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    row = modvarTagRow + 2
    value = _parse_value(sheet.values[row, GB_RW_DataStartCol])
    if isinstance(value, str):
        projection[RNMitigationProgramsEnteredTag] = value.strip().lower() in ('1', 'true', 'yes', 'y')
    else:
        projection[RNMitigationProgramsEnteredTag] = bool(value)


def import_Mitigation(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<Mitigation MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_rn_year_index_bounds(params)

    count = _parse_value(sheet.values[modvarTagRow + 1, GB_RW_DataStartCol])
    try:
        count = int(count)
    except (TypeError, ValueError):
        count = 0

    programs_entered = bool(projection.get(RNMitigationProgramsEnteredTag, False))

    row = modvarTagRow + 3
    result = []
    for _ in range(count):
        obj = {
            'MitProgram': sheet.values[row, GB_RW_DataStartCol],
        }
        if programs_entered:
            obj['Value'] = _read_rn_year_row_contiguous(
                sheet, row, calc_year_idx, final_index, start_col=GB_RW_DataStartCol + 1
            )
        result.append(obj)
        row += 1

    projection[RNMitigationTag] = result


def import_MethodMix(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<MethodMix MV5>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    row = modvarTagRow + 2
    projection[RNMethodMixTag] = _parse_value(sheet.values[row, GB_RW_DataStartCol])


def import_CurrencyDisplayedCBIdx(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<CurrencyDisplayedCBIdx MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    row = modvarTagRow + 2
    value = _parse_value(sheet.values[row, GB_RW_DataStartCol])
    try:
        projection[RNCurrencyDisplayedCBIdxTag] = int(value)
    except (TypeError, ValueError):
        projection[RNCurrencyDisplayedCBIdxTag] = 0


def import_ResourcesRequired(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<ResourcesRequired MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_rn_year_index_bounds(params)

    max_summary = projection.get(RNMaxSummaryTableConstantsTag, RN_ST_MaxSummaryTable)
    try:
        max_summary = int(max_summary)
    except (TypeError, ValueError):
        max_summary = RN_ST_MaxSummaryTable

    row = modvarTagRow + 3
    result = {}
    for _ in range(max_summary):
        mst_id = _parse_value(sheet.values[row, GB_RW_DataStartCol])
        try:
            mst_id = int(mst_id)
        except (TypeError, ValueError):
            row += 1
            continue

        result[mst_id] = _read_rn_year_row_contiguous(
            sheet, row, calc_year_idx, final_index, start_col=GB_RW_DataStartCol + 1
        )
        row += 1

    projection[RNResourcesRequiredTag] = result


def import_NumberPeopleReached(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<NumberPeopleReached MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_rn_year_index_bounds(params)

    max_summary = projection.get(RNMaxSummaryTableConstantsTag, RN_ST_MaxSummaryTable)
    try:
        max_summary = int(max_summary)
    except (TypeError, ValueError):
        max_summary = RN_ST_MaxSummaryTable

    row = modvarTagRow + 3
    result = {}
    for _ in range(max_summary):
        mst_id = _parse_value(sheet.values[row, GB_RW_DataStartCol])
        try:
            mst_id = int(mst_id)
        except (TypeError, ValueError):
            row += 1
            continue

        result[mst_id] = _read_rn_year_row_contiguous(
            sheet, row, calc_year_idx, final_index, start_col=GB_RW_DataStartCol + 1
        )
        row += 1

    projection[RNNumberPeopleReachedTag] = result


def import_PMTCTCosts(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<PMTCTCosts MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_rn_year_index_bounds(params)

    row = modvarTagRow + 2
    projection[RNPMTCTCostsTag] = _read_rn_year_row_contiguous(
        sheet, row, calc_year_idx, final_index, start_col=GB_RW_DataStartCol
    )


def import_TotalCosts(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<TotalCosts MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_rn_year_index_bounds(params)

    row = modvarTagRow + 2
    projection[RNTotalCostsTag] = _read_rn_year_row_contiguous(
        sheet, row, calc_year_idx, final_index, start_col=GB_RW_DataStartCol
    )


def import_OptimizerVars(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<OptimizerVars MV2>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_rn_year_index_bounds(params)

    row = modvarTagRow + 2
    result = {}
    result['StartYearIndex'] = int(_to_float(_parse_value(sheet.values[row, GB_RW_DataStartCol])))
    row += 1
    result['TargetYearIndex'] = int(_to_float(_parse_value(sheet.values[row, GB_RW_DataStartCol])))
    row += 1
    result['FinalYearIndex'] = int(_to_float(_parse_value(sheet.values[row, GB_RW_DataStartCol])))
    row += 1
    result['GoalIndex'] = int(_to_float(_parse_value(sheet.values[row, GB_RW_DataStartCol])))
    row += 1
    result['DiscountRate'] = int(_to_float(_parse_value(sheet.values[row, GB_RW_DataStartCol])))
    row += 1

    load_default_raw = _parse_value(sheet.values[row, GB_RW_DataStartCol])
    if isinstance(load_default_raw, str):
        result['LoadDefaultValues'] = load_default_raw.strip().lower() in ('1', 'true', 'yes', 'y')
    else:
        result['LoadDefaultValues'] = bool(load_default_raw)
    row += 1

    coverages = {
        RN_MinCov: {},
        RN_MaxCov: {},
    }
    for iv in range(1, RN_OP_MaxOptimize + 1):
        coverages[RN_MinCov][iv] = _to_float(_parse_value(sheet.values[row, GB_RW_NotesCol + iv]))
    row += 1
    for iv in range(1, RN_OP_MaxOptimize + 1):
        coverages[RN_MaxCov][iv] = _to_float(_parse_value(sheet.values[row, GB_RW_NotesCol + iv]))
    row += 1

    funding_amnts = [0.0] * (final_index + 1)
    multiplier = 0
    for t in range(1, final_index + 1):
        if t % RN_OP_MaxOptimize == 0:
            row += 1
            multiplier += 1
        offset = t - multiplier * RN_OP_MaxOptimize
        if multiplier > 0:
            offset += 1
        funding_amnts[t] = _to_float(_parse_value(sheet.values[row, GB_RW_NotesCol + offset]))

    row += 1
    cea_available_raw = _parse_value(sheet.values[row, GB_RW_DataStartCol])
    if isinstance(cea_available_raw, str):
        cea_available = cea_available_raw.strip().lower() in ('1', 'true', 'yes', 'y')
    else:
        cea_available = bool(cea_available_raw)
    row += 1

    use_prior_raw = _parse_value(sheet.values[row, GB_RW_DataStartCol])
    if isinstance(use_prior_raw, str):
        use_prior_cea = use_prior_raw.strip().lower() in ('1', 'true', 'yes', 'y')
    else:
        use_prior_cea = bool(use_prior_raw)
    row += 1

    cost_infections_averted = {}
    for i in range(RN_ComMob, RN_MaxCEA + 1):
        cost_infections_averted[i] = _to_float(_parse_value(sheet.values[row, GB_RW_NotesCol + i]))
    row += 1

    cost_aids_deaths_averted = {}
    for i in range(RN_ComMob, RN_MaxCEA + 1):
        cost_aids_deaths_averted[i] = _to_float(_parse_value(sheet.values[row, GB_RW_NotesCol + i]))
    row += 1

    cost_dalys_averted = {}
    for i in range(RN_ComMob, RN_MaxCEA + 1):
        cost_dalys_averted[i] = _to_float(_parse_value(sheet.values[row, GB_RW_NotesCol + i]))

    result['Coverages'] = coverages
    result['FundingAmnts'] = funding_amnts
    result['CEAValuesAvailable'] = cea_available
    result['UsePriorCEAValues'] = use_prior_cea
    result['CostInfectionsAverted'] = cost_infections_averted
    result['CostAIDSDeathsAverted'] = cost_aids_deaths_averted
    result['CostDALYsAverted'] = cost_dalys_averted

    projection[RNOptimizerVarsTag] = result
