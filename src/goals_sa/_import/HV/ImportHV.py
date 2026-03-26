import pandas as pd
import numpy as np

from AvenirCommon.Util import findTagRow

from SpectrumCommon.Modvars.GB.GBDefs import createProjectionParams
from SpectrumCommon.Const.GB import *
from SpectrumCommon.Const.HV import *
from SpectrumCommon.Const.RN import RN_AllVacc, RN_IDUDrugSub, RN_NoProt, RN_UnV



def openHV(file, params: createProjectionParams, projection: dict):
    sheet = pd.read_csv(file, header=None, na_filter=False, encoding='utf-8')


    _import_tag_value(sheet, projection, '<FirstYear MV>',           HVFirstYearTag)
    _import_tag_value(sheet, projection, '<FinalYear MV>',           HVFinalYearTag)
    _import_tag_value(sheet, projection, '<FinalIndex MV>',          HVFinalIndexTag)
    _import_tag_value(sheet, projection, '<DataChanged MV>',         HVDataChangedTag)
    _import_tag_value(sheet, projection, '<ProjectionValid MV>',     HVProjectionValidTag)
    _import_tag_value(sheet, projection, '<projectionValidDate MV>', HVProjectionValidDateTag)
    _import_tag_value(sheet, projection, '<FileName MV>',            HVFileNameTag)

    import_Behavior(sheet, params, projection)
    import_AgeFirstSex(sheet, params, projection)
    import_ForceInf(sheet, params, projection)
    import_Infectiousness(sheet, params, projection)
    import_Prevalence(sheet, params, projection)
    import_CondomPercent(sheet, params, projection)
    _import_tag_value(sheet, projection, '<TransMultSTI MV>', HVTransMultSTITag)
    _import_tag_value(sheet, projection, '<TransHIVF MV>',    HVTransHIVFTag)
    _import_tag_value(sheet, projection, '<TransMultM MV>',   HVTransMultMTag)
    _import_tag_value(sheet, projection, '<CondomEff MV>',    HVCondomEffTag)
    import_NumPart(sheet, params, projection)
    import_SexActs(sheet, params, projection)
    import_STIPrev(sheet, params, projection)
    import_EpidemicStYr(sheet, params, projection)
    import_IncRecruitment(sheet, params, projection)
    import_AllRiskOutput(sheet, params, projection)
    import_MaxAllRisk(sheet, params, projection)
    import_PercMarried(sheet, params, projection)
    import_PerIDUsharing(sheet, params, projection)
    import_InitialPulse(sheet, params, projection)
    import_TransMultMSM(sheet, params, projection)
    import_RedWHenCircum(sheet, params, projection)
    import_InfectMultiplierOnART(sheet, params, projection)
    import_BloodInfection(sheet, params, projection)
    import_ARTReceive(sheet, params, projection)
    import_MonthsInPrimaryStage(sheet, params, projection)
    import_GoalsBaseYearIdx(sheet, params, projection)
    import_GoalsTargetYearIdx(sheet, params, projection)
    import_ImpactMatrix(sheet, params, projection)
    import_ImpactMatrixCBIdx(sheet, params, projection)
    _import_tag_value(sheet, projection, '<ARTInputCoverageByRG MV>', HVARTInputCoverageByRGTag)
    import_NumMSMRiskGroups(sheet, params, projection)
    import_BalanceSexActs(sheet, params, projection)
    import_CondomUseRadioGroupIdx(sheet, params, projection)
    import_CondomUseLogCurveParVal(sheet, params, projection)
    import_CondomUseInterpolatedVal(sheet, params, projection)
    import_CondomUseLogisticsVal(sheet, params, projection)
    import_STIPrevRadioGroupIdx(sheet, params, projection)
    import_STIPrevLogCurveParVal(sheet, params, projection)
    import_STIPrevInterpolatedVal(sheet, params, projection)
    import_STIPrevLogisticsVal(sheet, params, projection)
    import_RiskGroupNames(sheet, params, projection)
    import_EdHVSource(sheet, params, projection)
    # import_CalcStateData(sheet, params, projection)
    import_Adults(sheet, params, projection)
    import_RiskGroupPercent(sheet, params, projection)
    import_NonAIDSDeathRate(sheet, params, projection)
    import_RateofAging(sheet, params, projection)
    import_Populations(sheet, params, projection)
    import_Vaccinated(sheet, params, projection)
    import_TotalVaccinated(sheet, params, projection)
    import_Unvaccinated(sheet, params, projection)
    import_NewVaccinations(sheet, params, projection)
    import_TotalNewVaccinations(sheet, params, projection)
    import_TotalAdultsHIV(sheet, params, projection)
    import_NewlyOnART(sheet, params, projection)
    import_NewlyEligibleART(sheet, params, projection)
    import_TotalAdultsART(sheet, params, projection)
    import_RMultAll(sheet, params, projection)
    import_CalcPrevalence(sheet, params, projection)
    import_NewInfections(sheet, params, projection)
    import_ExitRate(sheet, params, projection)
    import_AIDSDeaths(sheet, params, projection)
    import_AIDSDeathsART(sheet, params, projection)
    import_TotalAIDSDeaths(sheet, params, projection)
    import_TotalNewInfection(sheet, params, projection)
    import_Incidence(sheet, params, projection)
    import_IncSexRatio(sheet, params, projection)
    import_PercentPop(sheet, params, projection)
    import_InfectionsAverted(sheet, params, projection)
    import_CumInfectionsAverted(sheet, params, projection)
    import_DeathsAverted(sheet, params, projection)
    import_CumDeathsAverted(sheet, params, projection)
    import_ARTCoverageByRG(sheet, params, projection)
    import_TotalARTCoverage(sheet, params, projection)
    import_NewHIV(sheet, params, projection)
    import_FitData(sheet, params, projection)
    import_FitParamSet(sheet, params, projection)
    import_FitControl(sheet, params, projection)
    import_LowRiskCondomUseFromFP(sheet, params, projection)
    _import_tag_value(sheet, projection, '<edFmHighlight MV>', HVEdFmHighlightTag)

    return None

############### Start reading in HV Modvars ######################################


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


def _import_tag_value(sheet, projection, source_tag: str, projection_tag: str):
    modvarTagRow = findTagRow(sheet, source_tag)
    if modvarTagRow is None or modvarTagRow < 0:
        return

    row = modvarTagRow + 2
    projection[projection_tag] = _parse_value(sheet.values[row, GB_RW_DataStartCol])


def _to_float(value, default=0.0):
    if value == '' or value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _get_year_index_bounds(params, projection):
    calc_year_idx = max(0, int(params.firstYear) - GB_NativeYear)
    final_index = int(params.finalYear) - int(params.firstYear)
    final_index = max(calc_year_idx, int(final_index))
    return calc_year_idx, final_index


def _read_year_row_with_flatline(sheet, row: int, calc_year_idx: int, final_index: int,
                                 start_col: int = GB_RW_DataStartCol):
    values = [0.0] * (final_index + 1)
    col = start_col
    last_value = 0.0
    for t in range(calc_year_idx, final_index + 1):
        cell_value = sheet.values[row, col]
        if cell_value != '':
            last_value = _to_float(_parse_value(cell_value), last_value)
            col += 1
        else:
            pass
        values[t] = last_value
    return values


def import_Behavior(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<Behavior MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    row = modvarTagRow + 4
    behavior = np.zeros((HV_IDU_F3 + 1, HV_AvgDur + 1))

    for i in range(HV_None, HV_MSMIDU + 1):
        row += 1
        for s in range(HV_PercPop, HV_AvgDur + 1):
            behavior[i, s] = _parse_value(sheet.values[row, GB_RW_DataStartCol + s - 1])
        row += 1

    row += 1
    for i in range(HV_None_F3, HV_IDU_F3 + 1):
        row += 1
        for s in range(HV_PercPop, HV_AvgDur + 1):
            behavior[i, s] = _parse_value(sheet.values[row, GB_RW_DataStartCol + s - 1])
        row += 1

    projection[HVBehaviorTag] = behavior

def import_AgeFirstSex(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<AgeFirstSex MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    # Delphi reads two rows: males at +2 and females at +4, then flatlines to final index.
    calc_year_idx, final_index = _get_year_index_bounds(params, projection)

    age_first_sex = np.zeros((HV_Female + 1, final_index + 1))

    for row_offset, sex in ((2, HV_Male), (4, HV_Female)):
        row = modvarTagRow + row_offset
        col = GB_RW_DataStartCol
        last_value = 0.0
        for t in range(calc_year_idx, final_index + 1):
            cell_value = sheet.values[row, col]
            if cell_value != '':
                last_value = _parse_value(cell_value)
                col += 1
            age_first_sex[sex, t] = last_value

    projection[HVAgeFirstSexTag] = age_first_sex.tolist()

def import_ForceInf(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<ForceInf MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_year_index_bounds(params, projection)
    force_inf = np.zeros((HV_Adults_P + 1, final_index + 1))

    # Delphi reads males at tag+2 and females at tag+4 with flatline beyond imported years.
    for sex, row_offset in ((HV_Male, 4), (HV_Female, 6)):
        row_values = _read_year_row_with_flatline(sheet, modvarTagRow + row_offset, calc_year_idx, final_index)
        force_inf[sex] = row_values

    projection[HVForceInfTag] = force_inf.tolist()

def import_Infectiousness(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<Infectiousness MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    infectiousness = np.zeros(HV_SympART + 1)
    row = modvarTagRow + 2

    for t in range(HV_PrimaryInf, HV_SympART + 1):
        row += 1
        infectiousness[t] = _to_float(_parse_value(sheet.values[row, GB_RW_DataStartCol]))
        row += 1

    projection[HVInfectiousnessTag] = infectiousness.tolist()

def import_Prevalence(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<Prevalence MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_year_index_bounds(params, projection)
    prevalence = np.zeros((HV_Adults_P + 1, final_index + 1))

    row = modvarTagRow + 3
    for s in range(HV_Males_P, HV_Adults_P + 1):
        row += 1
        prevalence[s] = _read_year_row_with_flatline(sheet, row, calc_year_idx, final_index)
        row += 1

    projection[HVPrevalenceTag] = prevalence.tolist()

def import_CondomPercent(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<CondomPercent MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_year_index_bounds(params, projection)
    condom_percent = np.zeros((HV_Adults_P + 1, final_index + 1))

    row = modvarTagRow + 3
    nrow = 1
    for r in range(HV_LRH, HV_MSMHR):
        nrow += 1
        if r == HV_IDU:
            nrow += 1
        row += 1
        condom_percent[nrow] = _read_year_row_with_flatline(sheet, row, calc_year_idx, final_index)
        row += 1

    projection[HVCondomPercentTag] = condom_percent.tolist()

def import_NumPart(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<NumPart MV2>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_year_index_bounds(params, projection)
    num_part = np.zeros((HV_MSM_F3 + 1, final_index + 1))

    row = modvarTagRow + 3
    for r in range(HV_AllRisk, HV_MSM_F3 + 1):
        num_part[r] = _read_year_row_with_flatline(sheet, row, calc_year_idx, final_index)
        row += 1

    projection[HVNumPartTag] = num_part.tolist()

def import_SexActs(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<SexActs MV2>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_year_index_bounds(params, projection)
    sex_acts = np.zeros((HV_MSM_F3 + 1, final_index + 1))

    row = modvarTagRow + 3
    for r in range(HV_AllRisk, HV_MSM_F3 + 1):
        sex_acts[r] = _read_year_row_with_flatline(sheet, row, calc_year_idx, final_index)
        row += 1

    projection[HVSexActsTag] = sex_acts.tolist()

def import_STIPrev(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<STIPrev MV2>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_year_index_bounds(params, projection)
    sti_prev = np.zeros((HV_MSM_F3 + 1, final_index + 1))

    row = modvarTagRow + 3
    for r in range(HV_AllRisk, HV_MSM_F3 + 1):
        sti_prev[r] = _read_year_row_with_flatline(sheet, row, calc_year_idx, final_index)
        row += 1

    projection[HVSTIPrevTag] = sti_prev.tolist()

def import_EpidemicStYr(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<EpidemicStYr MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    row = modvarTagRow + 2
    value = int(_to_float(_parse_value(sheet.values[row, GB_RW_DataStartCol]), 1980.0))
    if value < int(params.firstYear):
        value = 1980
    projection[HVEpidemicStYrTag] = value

def import_IncRecruitment(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<IncRecruitment MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    inc_recruitment = np.zeros((HV_Female + 1, HV_MSMIDU + 1))

    curr_row = modvarTagRow + 2
    curr_row += 1
    for s in range(HV_Male, HV_Female + 1):
        curr_row += 1
        for r in range(HV_None, HV_MSMIDU + 1):
            curr_row += 1
            inc_recruitment[s, r] = _to_float(_parse_value(sheet.values[curr_row, GB_RW_DataStartCol]))
            curr_row += 1

    projection[HVIncRecruitmentTag] = inc_recruitment.tolist()

def import_AllRiskOutput(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<AllRiskOutput MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_year_index_bounds(params, projection)
    all_risk_output = np.zeros((HV_max_services, final_index + 1))

    row = modvarTagRow + 3
    for i in range(0, HV_max_services):
        all_risk_output[i] = _read_year_row_with_flatline(sheet, row, calc_year_idx, final_index)
        row += 1

    projection[HVAllRiskOutputTag] = all_risk_output.tolist()

def import_MaxAllRisk(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<MaxAllRisk MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    row = modvarTagRow + 2
    projection[HVMaxAllRiskTag] = _to_float(_parse_value(sheet.values[row, GB_RW_DataStartCol]))

def import_PercMarried(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<PercMarried MV2>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    perc_married = np.zeros(HV_MSM_F3 + 1)

    row = modvarTagRow + 3
    for r in range(HV_AllRisk, HV_MSM_F3 + 1):
        perc_married[r] = _to_float(_parse_value(sheet.values[row, GB_RW_DataStartCol]))
        row += 1

    projection[HVPercMarriedTag] = perc_married.tolist()

def import_PerIDUsharing(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<PerIDUsharing MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_year_index_bounds(params, projection)
    row = modvarTagRow + 3
    projection[HVPerIDUsharingTag] = _read_year_row_with_flatline(sheet, row, calc_year_idx, final_index)

def import_InitialPulse(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<InitialPulse MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    row = modvarTagRow + 2
    projection[HVInitialPulseTag] = _to_float(_parse_value(sheet.values[row, GB_RW_DataStartCol]))

def import_TransMultMSM(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<TransMultMSM MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    row = modvarTagRow + 2
    projection[HVTransMultMSMTag] = _to_float(_parse_value(sheet.values[row, GB_RW_DataStartCol]))

def import_RedWHenCircum(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<RedWHenCircum MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    row = modvarTagRow + 2
    red_when_circum = np.zeros(HV_Infect + 1)
    for i in range(HV_Susceptibility, HV_Infect + 1):
        red_when_circum[i] = _to_float(_parse_value(sheet.values[row, GB_RW_DataStartCol + i - 1]))
    projection[HVRedWHenCircumTag] = red_when_circum.tolist()

def import_InfectMultiplierOnART(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<InfectMultiplierOnART MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_year_index_bounds(params, projection)
    row = modvarTagRow + 4
    projection[HVInfectMultiplierOnARTTag] = _read_year_row_with_flatline(sheet, row, calc_year_idx, final_index)

def import_BloodInfection(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<BloodInfection MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_year_index_bounds(params, projection)
    row = modvarTagRow + 4
    projection[HVBloodInfectionTag] = _read_year_row_with_flatline(sheet, row, calc_year_idx, final_index)

def import_ARTReceive(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<ARTReceive MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_year_index_bounds(params, projection)
    row = modvarTagRow + 3
    projection[HVARTReceiveTag] = _read_year_row_with_flatline(sheet, row, calc_year_idx, final_index)

def import_MonthsInPrimaryStage(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<MonthsInPrimaryStage MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    row = modvarTagRow + 2
    projection[HVMonthsInPrimaryStageTag] = _to_float(_parse_value(sheet.values[row, GB_RW_DataStartCol]))

def import_GoalsBaseYearIdx(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<GoalsBaseYearIdx MV2>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    row = modvarTagRow + 2
    projection[HVGoalsBaseYearIdxTag] = int(_to_float(_parse_value(sheet.values[row, GB_RW_DataStartCol]), 0.0))

def import_GoalsTargetYearIdx(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<GoalsTargetYearIdx MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    row = modvarTagRow + 2
    projection[HVGoalsTargetYearIdxTag] = int(_to_float(_parse_value(sheet.values[row, GB_RW_DataStartCol]), 0.0))

def import_ImpactMatrix(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<ImpactMatrix MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    impact_matrix = np.zeros((HV_Data + 1, RN_IDUDrugSub + 1, HV_MaxRiskGroups + 1))

    row = modvarTagRow + 2
    for d in range(HV_Default, HV_Data + 1):
        for i in range(1, RN_IDUDrugSub + 1):
            for r in range(1, HV_MaxRiskGroups + 1):
                impact_matrix[d, i, r] = _to_float(_parse_value(sheet.values[row, GB_RW_DataStartCol + r]))
            row += 1

    projection[HVImpactMatrixTag] = impact_matrix.tolist()

def import_ImpactMatrixCBIdx(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<ImpactMatrixCBIdx MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    row = modvarTagRow + 2
    projection[HVImpactMatrixCBIdxTag] = int(_to_float(_parse_value(sheet.values[row, GB_RW_DataStartCol]), 0.0))

def import_ARTInputCoverageByRG(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<ARTInputCoverageByRG MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    row = modvarTagRow + 2
    projection[HVARTInputCoverageByRGTag] = _parse_value(sheet.values[row, GB_RW_DataStartCol])

def import_NumMSMRiskGroups(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<NumMSMRiskGroups MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    row = modvarTagRow + 2
    projection[HVNumMSMRiskGroupsTag] = int(_to_float(_parse_value(sheet.values[row, GB_RW_DataStartCol]), 0.0))

def import_BalanceSexActs(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<BalanceSexActs MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    row = modvarTagRow + 2
    projection[HVBalanceSexActsTag] = bool(int(_to_float(_parse_value(sheet.values[row, GB_RW_DataStartCol]), 0.0)))

def import_CondomUseRadioGroupIdx(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<CondomUseRadioGroupIdx MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    row = modvarTagRow + 2
    projection[HVCondomUseRadioGroupIdxTag] = int(_to_float(_parse_value(sheet.values[row, GB_RW_DataStartCol]), 0.0))

def import_CondomUseLogCurveParVal(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<CondomUseLogCurveParVal MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    log_curve_par_val = np.zeros((HV_MSMHR + 1, HV_CU_Q + 1))

    row = modvarTagRow + 2
    for r in range(HV_LRH, HV_MSMHR + 1):
        for par in range(HV_CU_A, HV_CU_Q + 1):
            log_curve_par_val[r, par] = _to_float(_parse_value(sheet.values[row, GB_RW_DataStartCol + par - 1]))
        row += 1

    projection[HVCondomUseLogCurveParValTag] = log_curve_par_val.tolist()

def import_CondomUseInterpolatedVal(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<CondomUseInterpolatedVal MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_year_index_bounds(params, projection)
    interpolated_val = np.zeros((HV_MSMIDU + 1, final_index + 1))

    row = modvarTagRow + 3
    nrow = 1
    for r in range(HV_LRH, HV_MSMHR):
        nrow += 1
        if r == HV_IDU:
            nrow += 1
        row += 1
        interpolated_val[nrow] = _read_year_row_with_flatline(sheet, row, calc_year_idx, final_index)
        row += 1

    projection[HVCondomUseInterpolatedValTag] = interpolated_val.tolist()

def import_CondomUseLogisticsVal(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<CondomUseLogisticsVal MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_year_index_bounds(params, projection)
    logistics_val = np.zeros((HV_MSMIDU + 1, final_index + 1))

    row = modvarTagRow + 2
    nrow = 1
    for r in range(HV_LRH, HV_MSMHR):
        nrow += 1
        if r == HV_IDU:
            nrow += 1
        row += 1
        logistics_val[nrow] = _read_year_row_with_flatline(sheet, row, calc_year_idx, final_index)
        row += 1

    projection[HVCondomUseLogisticsValTag] = logistics_val.tolist()

def import_STIPrevRadioGroupIdx(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<STIPrevRadioGroupIdx MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    row = modvarTagRow + 2
    projection[HVSTIPrevRadioGroupIdxTag] = int(_to_float(_parse_value(sheet.values[row, GB_RW_DataStartCol]), 0.0))

def import_STIPrevLogCurveParVal(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<STIPrevLogCurveParVal MV2>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    log_curve_par_val = np.zeros((HV_MSM_F3 + 1, HV_CU_Q + 1))

    row = modvarTagRow + 2
    for r in range(HV_AllRisk, HV_MSM_F3 + 1):
        for par in range(HV_CU_A, HV_CU_Q + 1):
            log_curve_par_val[r, par] = _to_float(_parse_value(sheet.values[row, GB_RW_DataStartCol + par - 1]))
        row += 1

    projection[HVSTIPrevLogCurveParValTag] = log_curve_par_val.tolist()

def import_STIPrevInterpolatedVal(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<STIPrevInterpolatedVal MV2>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_year_index_bounds(params, projection)
    interpolated_val = np.zeros((HV_MSM_F3 + 1, final_index + 1))

    row = modvarTagRow + 3
    for r in range(HV_AllRisk, HV_MSM_F3 + 1):
        interpolated_val[r] = _read_year_row_with_flatline(sheet, row, calc_year_idx, final_index)
        row += 1

    projection[HVSTIPrevInterpolatedValTag] = interpolated_val.tolist()

def import_STIPrevLogisticsVal(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<STIPrevLogisticsVal MV2>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_year_index_bounds(params, projection)
    logistics_val = np.zeros((HV_MSM_F3 + 1, final_index + 1))

    row = modvarTagRow + 3
    for r in range(HV_AllRisk, HV_MSM_F3 + 1):
        logistics_val[r] = _read_year_row_with_flatline(sheet, row, calc_year_idx, final_index)
        row += 1

    projection[HVSTIPrevLogisticsValTag] = logistics_val.tolist()

def import_RiskGroupNames(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<RiskGroupNames MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    row = modvarTagRow + 2
    count = int(_to_float(_parse_value(sheet.values[row, GB_RW_DataStartCol]), 0.0))
    names = []
    for s in range(1, count + 1):
        names.append(sheet.values[row, GB_RW_DataStartCol + s])
    projection[HVRiskGroupNamesTag] = names

def import_EdHVSource(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<EdHVSource MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    row = modvarTagRow + 2
    count = int(_to_float(_parse_value(sheet.values[row, GB_RW_DataStartCol]), 0.0))
    sources = []
    for s in range(1, count + 1):
        sources.append(sheet.values[row, GB_RW_DataStartCol + s])
    projection[HVEdHVSourceTag] = sources

# def import_CalcStateData(sheet, params, projection):
#     modvarTagRow = findTagRow(sheet, '<CalcStateData MV2>')
#     if modvarTagRow is None or modvarTagRow < 0:
#         return

#     row = modvarTagRow + 2
#     projection[HVCalcStateDataTag] = _parse_value(sheet.values[row, GB_RW_DataStartCol])

def import_Adults(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<Adults MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_year_index_bounds(params, projection)
    adults = np.zeros((HV_Female + 1, HV_MSMIDU + 1, HV_AllHIV + 1, RN_NoProt + 1, final_index + 1))

    row = modvarTagRow + 2
    for s in range(HV_BothSexes, HV_Female + 1):
        row += 1
        for r in range(HV_AllRisk, HV_MSMIDU + 1):
            for h in range(HV_Negative, HV_AllHIV + 1):
                for v in range(RN_AllVacc, RN_NoProt + 1):
                    adults[s, r, h, v] = _read_year_row_with_flatline(
                        sheet, row, calc_year_idx, final_index,
                        start_col=GB_RW_DataStartCol + 2
                    )
                    row += 1

    projection[HVAdultsTag] = adults.tolist()

def import_RiskGroupPercent(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<RiskGroupPercent MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    risk_group_percent = np.zeros(HV_MSM_F3 + 1)

    curr_row = modvarTagRow + 2
    for s in range(HV_AllRisk, HV_MSM_F3 + 1):
        curr_row += 1
        risk_group_percent[s] = _to_float(_parse_value(sheet.values[curr_row, GB_RW_DataStartCol]))
        curr_row += 1

    projection[HVRiskGroupPercentTag] = risk_group_percent.tolist()

def import_NonAIDSDeathRate(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<NonAIDSDeathRate MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_year_index_bounds(params, projection)
    non_aids_death_rate = np.zeros((HV_Female + 1, final_index + 1))

    row = modvarTagRow + 2
    for i in range(HV_BothSexes, HV_Female):
        non_aids_death_rate[i] = _read_year_row_with_flatline(sheet, row, calc_year_idx, final_index)
        row += 1

    projection[HVNonAIDSDeathRateTag] = non_aids_death_rate.tolist()

def import_RateofAging(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<RateofAging MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_year_index_bounds(params, projection)
    rate_of_aging = np.zeros((HV_Female + 1, final_index + 1))

    row = modvarTagRow + 2
    for i in range(HV_BothSexes, HV_Female):
        rate_of_aging[i] = _read_year_row_with_flatline(sheet, row, calc_year_idx, final_index)
        row += 1

    projection[HVRateofAgingTag] = rate_of_aging.tolist()

def import_Populations(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<Populations MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_year_index_bounds(params, projection)
    populations = np.zeros((HV_Female + 1, final_index + 1))

    curr_row = modvarTagRow + 2
    for s in range(HV_BothSexes, HV_Female + 1):
        curr_row += 1
        populations[s] = _read_year_row_with_flatline(sheet, curr_row, calc_year_idx, final_index)
        curr_row += 1

    projection[HVPopulationsTag] = populations.tolist()

def import_Vaccinated(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<Vaccinated MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_year_index_bounds(params, projection)
    vaccinated = np.zeros((HV_Female + 1, HV_MSMIDU + 1, HV_AllHIV + 1, final_index + 1))

    row = modvarTagRow + 2
    for s in range(HV_BothSexes, HV_Female):
        for r in range(HV_AllRisk, HV_MSMIDU):
            for h in range(HV_Negative, HV_AllHIV):
                vaccinated[s, r, h] = _read_year_row_with_flatline(sheet, row, calc_year_idx, final_index)
                row += 1

    projection[HVVaccinatedTag] = vaccinated.tolist()

def import_TotalVaccinated(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<TotalVaccinated MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_year_index_bounds(params, projection)
    total_vaccinated = np.zeros((HV_Female + 1, final_index + 1))

    curr_row = modvarTagRow + 2
    for s in range(HV_BothSexes, HV_Female + 1):
        curr_row += 1
        total_vaccinated[s] = _read_year_row_with_flatline(sheet, curr_row, calc_year_idx, final_index)
        curr_row += 1

    projection[HVTotalVaccinatedTag] = total_vaccinated.tolist()

def import_Unvaccinated(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<Unvaccinated MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_year_index_bounds(params, projection)
    row = modvarTagRow + 2
    projection[HVUnvaccinatedTag] = _read_year_row_with_flatline(sheet, row, calc_year_idx, final_index)

def import_NewVaccinations(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<NewVaccinations MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_year_index_bounds(params, projection)
    new_vaccinations = np.zeros((HV_Female + 1, HV_MSMIDU + 1, final_index + 1))

    curr_row = modvarTagRow + 2
    for s in range(HV_Male, HV_Female + 1):
        curr_row += 1
        for r in range(HV_None, HV_MSMIDU + 1):
            curr_row += 1
            new_vaccinations[s, r] = _read_year_row_with_flatline(sheet, curr_row, calc_year_idx, final_index)
            curr_row += 1
    curr_row += 1

    projection[HVNewVaccinationsTag] = new_vaccinations.tolist()

def import_TotalNewVaccinations(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<TotalNewVaccinations MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_year_index_bounds(params, projection)

    curr_row = modvarTagRow + 3
    projection[HVTotalNewVaccinationsTag] = _read_year_row_with_flatline(
        sheet,
        curr_row,
        calc_year_idx,
        final_index,
    )

def import_TotalAdultsHIV(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<TotalAdultsHIV MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_year_index_bounds(params, projection)
    total_adults_hiv = np.zeros((HV_Female + 1, final_index + 1))

    curr_row = modvarTagRow + 2
    for s in range(HV_Male, HV_Female + 1):
        curr_row += 1
        total_adults_hiv[s] = _read_year_row_with_flatline(sheet, curr_row, calc_year_idx, final_index)
        curr_row += 1

    projection[HVTotalAdultsHIVTag] = total_adults_hiv.tolist()

def import_NewlyOnART(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<NewlyOnART MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_year_index_bounds(params, projection)
    newly_on_art = np.zeros((HV_Female + 1, HV_CD4_LT50_ART + 1, final_index + 1))

    row = modvarTagRow + 2
    for s in range(HV_BothSexes, HV_Female + 1):
        for h in range(HV_CD4_GT500_ART, HV_CD4_LT50_ART + 1):
            newly_on_art[s, h] = _read_year_row_with_flatline(sheet, row, calc_year_idx, final_index)
            row += 1

    projection[HVNewlyOnARTTag] = newly_on_art.tolist()

def import_NewlyEligibleART(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<NewlyEligibleART MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_year_index_bounds(params, projection)
    newly_eligible_art = np.zeros((HV_Female + 1, HV_CD4_LT50_ART + 1, final_index + 1))

    row = modvarTagRow + 2
    for s in range(HV_BothSexes, HV_Female + 1):
        for h in range(HV_CD4_GT500_ART, HV_CD4_LT50_ART + 1):
            newly_eligible_art[s, h] = _read_year_row_with_flatline(sheet, row, calc_year_idx, final_index)
            row += 1

    projection[HVNewlyEligibleARTTag] = newly_eligible_art.tolist()

def import_TotalAdultsART(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<TotalAdultsART MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_year_index_bounds(params, projection)
    total_adults_art = np.zeros((HV_Female + 1, final_index + 1))

    curr_row = modvarTagRow + 2
    for s in range(HV_Male, HV_Female + 1):
        curr_row += 1
        total_adults_art[s] = _read_year_row_with_flatline(sheet, curr_row, calc_year_idx, final_index)
        curr_row += 1

    projection[HVTotalAdultsARTTag] = total_adults_art.tolist()

def import_RMultAll(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<rMultAll MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_year_index_bounds(params, projection)
    r_mult_all = np.zeros((HV_Female + 1, HV_MSMIDU + 1, final_index + 1))

    curr_row = modvarTagRow + 2
    curr_row += 1
    for s in range(HV_Male, HV_Female + 1):
        for r in range(HV_None, HV_MSMIDU + 1):
            r_mult_all[s, r] = _read_year_row_with_flatline(sheet, curr_row, calc_year_idx, final_index)
            curr_row += 1

    projection[HVRMultAllTag] = r_mult_all.tolist()

def import_CalcPrevalence(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<CalcPrevalence MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_year_index_bounds(params, projection)
    calc_prevalence = np.zeros((HV_Female + 1, HV_MSMIDU + 1, final_index + 1))

    curr_row = modvarTagRow + 2
    curr_row += 1
    for s in range(HV_Male, HV_Female + 1):
        curr_row += 1
        for r in range(HV_None, HV_MSMIDU + 1):
            curr_row += 1
            calc_prevalence[s, r] = _read_year_row_with_flatline(sheet, curr_row, calc_year_idx, final_index)
            curr_row += 1

    projection[HVCalcPrevalenceTag] = calc_prevalence.tolist()

def import_NewInfections(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<NewInfections MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_year_index_bounds(params, projection)
    new_infections = np.zeros((HV_Female + 1, HV_MSMIDU + 1, RN_NoProt + 1, final_index + 1))

    curr_row = modvarTagRow + 2
    for s in range(HV_Male, HV_Female + 1):
        curr_row += 1
        for r in range(HV_None, HV_MSMIDU + 1):
            curr_row += 1
            for v in range(RN_AllVacc, RN_NoProt + 1):
                curr_row += 1
                new_infections[s, r, v] = _read_year_row_with_flatline(sheet, curr_row, calc_year_idx, final_index)
                curr_row += 1

    projection[HVNewInfectionsTag] = new_infections.tolist()

def import_ExitRate(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<ExitRate MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_year_index_bounds(params, projection)
    exit_rate = np.zeros((HV_Female + 1, HV_MSMIDU + 1, HV_CD4_LT50 + 1, final_index + 1))

    row = modvarTagRow + 2
    for s in range(HV_BothSexes, HV_Female):
        for r in range(HV_AllRisk, HV_MSMIDU):
            for h in range(HV_Primary, HV_CD4_LT50):
                exit_rate[s, r, h] = _read_year_row_with_flatline(sheet, row, calc_year_idx, final_index)
                row += 1

    projection[HVExitRateTag] = exit_rate.tolist()

def import_AIDSDeaths(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<AIDSDeaths MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_year_index_bounds(params, projection)
    aids_deaths = np.zeros((HV_Female + 1, HV_MSMIDU + 1, RN_NoProt + 1, final_index + 1))

    curr_row = modvarTagRow + 2
    for s in range(HV_Male, HV_Female + 1):
        curr_row += 1
        for r in range(HV_None, HV_MSMIDU + 1):
            curr_row += 1
            for v in range(RN_UnV, RN_NoProt + 1):
                curr_row += 1
                aids_deaths[s, r, v] = _read_year_row_with_flatline(sheet, curr_row, calc_year_idx, final_index)
                curr_row += 1

    projection[HVAIDSDeathsTag] = aids_deaths.tolist()

def import_AIDSDeathsART(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<AIDSDeathsART MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_year_index_bounds(params, projection)
    aids_deaths_art = np.zeros((HV_Female + 1, HV_MSMIDU + 1, final_index + 1))

    row = modvarTagRow + 2
    for s in range(HV_BothSexes, HV_Female + 1):
        for r in range(HV_AllRisk, HV_MSMIDU + 1):
            aids_deaths_art[s, r] = _read_year_row_with_flatline(sheet, row, calc_year_idx, final_index)
            row += 1

    projection[HVAIDSDeathsARTTag] = aids_deaths_art.tolist()

def import_TotalAIDSDeaths(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<TotalAIDSDeaths MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_year_index_bounds(params, projection)

    curr_row = modvarTagRow + 3
    projection[HVTotalAIDSDeathsTag] = _read_year_row_with_flatline(sheet, curr_row, calc_year_idx, final_index)

def import_TotalNewInfection(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<TotalNewInfection MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_year_index_bounds(params, projection)

    curr_row = modvarTagRow + 3
    projection[HVTotalNewInfectionTag] = _read_year_row_with_flatline(sheet, curr_row, calc_year_idx, final_index)

def import_Incidence(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<Incidence MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_year_index_bounds(params, projection)

    curr_row = modvarTagRow + 3
    projection[HVIncidenceTag] = _read_year_row_with_flatline(sheet, curr_row, calc_year_idx, final_index)

def import_IncSexRatio(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<IncSexRatio MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_year_index_bounds(params, projection)
    row = modvarTagRow + 2
    projection[HVIncSexRatioTag] = _read_year_row_with_flatline(sheet, row, calc_year_idx, final_index)

def import_PercentPop(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<PercentPop MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_year_index_bounds(params, projection)
    data = np.zeros((HV_Female + 1, final_index + 1))
    curr_row = modvarTagRow + 2
    for s in range(HV_Male, HV_Female + 1):
        curr_row += 1
        data[s] = _read_year_row_with_flatline(sheet, curr_row, calc_year_idx, final_index)
        curr_row += 1
    projection[HVPercentPopTag] = data.tolist()

def import_InfectionsAverted(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<InfectionsAverted MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_year_index_bounds(params, projection)
    row = modvarTagRow + 2
    projection[HVInfectionsAvertedTag] = _read_year_row_with_flatline(sheet, row, calc_year_idx, final_index)

def import_CumInfectionsAverted(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<CumInfectionsAverted MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_year_index_bounds(params, projection)
    row = modvarTagRow + 2
    projection[HVCumInfectionsAvertedTag] = _read_year_row_with_flatline(sheet, row, calc_year_idx, final_index)

def import_DeathsAverted(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<DeathsAverted MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_year_index_bounds(params, projection)
    row = modvarTagRow + 2
    projection[HVDeathsAvertedTag] = _read_year_row_with_flatline(sheet, row, calc_year_idx, final_index)

def import_CumDeathsAverted(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<CumDeathsAverted MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_year_index_bounds(params, projection)
    row = modvarTagRow + 2
    projection[HVCumDeathsAvertedTag] = _read_year_row_with_flatline(sheet, row, calc_year_idx, final_index)

def import_ARTCoverageByRG(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<ARTCoverageByRG MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_year_index_bounds(params, projection)
    data = np.zeros((HV_Female + 1, HV_MSMIDU + 1, final_index + 1))
    curr_row = modvarTagRow + 2
    for s in range(HV_BothSexes, HV_Female + 1):
        for r in range(HV_None, HV_MSMIDU + 1):
            data[s, r] = _read_year_row_with_flatline(sheet, curr_row, calc_year_idx, final_index)
            curr_row += 1
    projection[HVARTCoverageByRGTag] = data.tolist()

def import_TotalARTCoverage(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<TotalARTCoverage MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_year_index_bounds(params, projection)
    data = np.zeros((HV_Female + 1, final_index + 1))
    curr_row = modvarTagRow + 2
    for s in range(HV_BothSexes, HV_Female + 1):
        data[s] = _read_year_row_with_flatline(sheet, curr_row, calc_year_idx, final_index)
        curr_row += 1
    projection[HVTotalARTCoverageTag] = data.tolist()

def import_NewHIV(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<NewHIV MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    calc_year_idx, final_index = _get_year_index_bounds(params, projection)
    data = np.zeros((HV_Female + 1, final_index + 1))
    curr_row = modvarTagRow + 2
    for i in range(HV_BothSexes, HV_Female + 1):
        data[i] = _read_year_row_with_flatline(sheet, curr_row, calc_year_idx, final_index)
        curr_row += 1
    projection[HVNewHIVTag] = data.tolist()

def import_FitData(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<FitData MV2>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    curr_row = modvarTagRow + 2
    count = int(sheet.values[curr_row, GB_RW_NotesCol])
    curr_row += 1
    records = []
    for i in range(count):
        records.append({
            'pop':    int(sheet.values[curr_row, 1]),
            'sex':    int(sheet.values[curr_row, 2]),
            'year':   int(sheet.values[curr_row, 3]),
            'value':  float(sheet.values[curr_row, 4]),
            'lower':  float(sheet.values[curr_row, 5]),
            'upper':  float(sheet.values[curr_row, 6]),
            'ssize':  float(sheet.values[curr_row, 7]),
            'use':    bool(int(sheet.values[curr_row, 8])),
            'source': str(sheet.values[curr_row, 9]),
        })
        curr_row += 1
    projection[HVFitDataTag] = records

def import_FitParamSet(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<FitParamSet MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    curr_row = modvarTagRow + 2
    curr_row += 1  # header row with count
    count = min(int(sheet.values[curr_row, GB_RW_NotesCol]), HV_MaxFitParams)
    curr_row += 1  # blank separator row
    param_set = {}
    for i in range(count):
        curr_row += 1
        index = int(sheet.values[curr_row, 1])
        param_set[index] = {
            'prior':  int(sheet.values[curr_row, 2]),
            'init':   float(sheet.values[curr_row, 3]),
            'mu':     float(sheet.values[curr_row, 4]),
            'sd':     float(sheet.values[curr_row, 5]),
            'value':  float(sheet.values[curr_row, 6]),
            'use':    bool(int(sheet.values[curr_row, 7])),
            'fitted': bool(int(sheet.values[curr_row, 8])),
        }
    projection[HVFitParamSetTag] = param_set

def import_FitControl(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<FitControl MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    curr_row = modvarTagRow + 2
    curr_row += 1  # data row
    projection[HVFitControlTag] = {
        'MaxIterations':  int(sheet.values[curr_row, 1]),
        'ErrorTolerance': float(sheet.values[curr_row, 2]),
        'PrevWeight':     int(sheet.values[curr_row, 3]),
    }

def import_LowRiskCondomUseFromFP(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<lowRiskCondomUseFromFP MV>')
    if modvarTagRow is None or modvarTagRow < 0:
        return

    row = modvarTagRow + 2
    projection[HVLowRiskCondomUseFromFPTag] = bool(_parse_value(sheet.values[row, GB_RW_DataStartCol]))

