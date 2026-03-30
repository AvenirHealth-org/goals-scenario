# fmt: off
from multiprocessing.dummy import connection
from os import environ
import pandas as pd
import numpy as np
from datetime import datetime

from AvenirCommon.Util import GBRange, findTagRow, dateTime_fromDelphi

from SpectrumCommon.Modvars.GB.GBDefs import createProjectionParams
from Tools.ImportExportPJNZ.ImportExportUtil import getRowOfYearVals, getRowOfYearValsInt, getFloatValue
from Tools.AM.EPP.EPPDataRW import getPathInfoDict

from SpectrumCommon.Const.GB import *
from SpectrumCommon.Modvars.GB.GBUtil import *
from SpectrumCommon.Const.DP import *
from SpectrumCommon.Const.AM.AMTags import *
from SpectrumCommon.Modvars.AM.AMUtil import getCustomSAPDataDict
from SpectrumCommon.Modvars.AM.AMModvarDef import HIVSexRatio_Meta_Init
from SpectrumCommon.Const.PJ import *


def addData(df : pd.DataFrame, text, value : np.ndarray):
    if value.ndim == 1:
        df[text] = value
    else:
        for i in range(0, value.shape[0]):
            addData(df, str(i) + ', ' + text, value[i])

def openDP(file, params : createProjectionParams, projection : dict):
    sheet = pd.read_csv(file, header = None, na_filter = False, encoding='utf-8')
    
    import_CustomFileYears(sheet, params, projection)
    import_CustomPopStopRescalingYear(sheet, params, projection)
    import_EdAdSource(sheet, params, projection)
    import_ChangesLog(sheet, params, projection)
    import_EdDmSource(sheet, params, projection)
    import_DPSources(sheet, params, projection)

    import_DefaultUPDLE(sheet, params, projection)
    import_DefaultUPDIMR(sheet, params, projection)
    import_DefaultUPDCMR(sheet, params, projection)
    import_DefaultUPDSurvRate(sheet, params, projection)
    import_BigPop(sheet, params, projection)
    import_TFR(sheet, params, projection)
    import_ASFR(sheet, params, projection)
    import_UNPopASFR(sheet, params, projection)
    import_ASFRNum(sheet, params, projection)
    import_ASFRCustomFlag(sheet, params, projection)
    import_SexBirthRatio(sheet, params, projection)
    import_LE(sheet, params, projection)
    import_MigrRate(sheet, params, projection)
    import_MigrAgeDist(sheet, params, projection)
    import_ModelLifeFileName(sheet, params, projection)
    import_UseFYrSingleAges(sheet, params, projection)
    import_RegionalAdjustPopData(sheet, params, projection)
    import_RegionalAdjustPopCBState(sheet, params, projection)
    import_RegionalAdjustPopFName(sheet, params, projection)
    import_RegionalAdjustPopFDate(sheet, params, projection)
    import_LifeTableNum(sheet, params, projection)
    import_SurvRate(sheet, params, projection)
    
    # AM
    if GB_AM in params.modules:
        import_CD4ThreshHold(sheet, params, projection)
        import_PopsEligTreat(sheet, params, projection)
        import_AgeHIVChildOnTreatment(sheet, params, projection)
        import_CD4ThreshHoldAdults(sheet, params, projection)
        import_InfantFeedingOptions(sheet, params, projection)
        import_ARVRegimen(sheet, params, projection)
        import_PatientsReallocated(sheet, params, projection)
        import_PercentARTDelivery(sheet, params, projection)
        import_PregTermAbortionPerNum(sheet, params, projection)
        import_PregTermAbortion(sheet, params, projection)
        import_MedCD4CountInit(sheet, params, projection)
        import_PercLostFollowup(sheet, params, projection)
        import_NumberInitTreatmentReinit(sheet, params, projection)
        import_NumNewlyInitART(sheet, params, projection)
        import_PercLostFollowupChild(sheet, params, projection)
        import_NumberInitTreatmentReinitsChild(sheet, params, projection)
        import_NumNewlyInitARTChild(sheet, params, projection)
        import_HAARTBySex(sheet, params, projection)
        import_HAARTBySexPerNum(sheet, params, projection)
        import_AdultARTAdjFactor(sheet, params, projection)
        import_AdultPatsAllocToFromOtherRegion(sheet, params, projection)
        import_AdultARTAdjFactorFlag(sheet, params, projection)   
        import_CD4Coverage(sheet, params, projection)
        import_ARTByAgeInputType(sheet, params, projection)
        import_ARTByAge5YearAG(sheet, params, projection)
        import_ARTByAgeGAMAG(sheet, params, projection)
        import_CovPopsEligTreat(sheet, params, projection)
        import_ChildTreatInputs(sheet, params, projection)
        import_ChildARTAdjFactor(sheet, params, projection)
        import_ChildARTAdjFactorFlag(sheet, params, projection)
        import_ChildARTByAgeGroupPerNum(sheet, params, projection)
        import_ANCTestingValues(sheet, params, projection)
        # import_NewInfectionsLessImmigrants(sheet, params, projection)
        import_HIVTesting(sheet, params, projection)
        import_HIVTestingHTSTestsByAge(sheet, params, projection)
        import_Shiny90SurveyData(sheet, params, projection)
        import_Shiny90ProgramData(sheet, params, projection)
        import_Shiny90AIDSDeathsFYear(sheet, params, projection)
        import_Shiny90Pop(sheet, params, projection)
        import_Shiny90NumTests(sheet, params, projection)
        import_Shiny90NumTested12M(sheet, params, projection)
        import_Shiny90TotalTests(sheet, params, projection)
        import_Shiny90EverTested(sheet, params, projection)
        import_Shiny90Diagnosed(sheet, params, projection)
        import_Shiny90NumAware(sheet, params, projection)
        import_Shiny90NumDiagnoses(sheet, params, projection)
        import_Shiny90NumDiagnosesMod(sheet, params, projection)
        import_Shiny90NumLateDiagnoses(sheet, params, projection)
        import_Shiny90NotDiagHIV1Yr(sheet, params, projection)
        import_Shiny90NumReTestHIVNeg(sheet, params, projection)
        import_Shiny90NumFirstTestHIVNeg(sheet, params, projection)
        import_Shiny90NumRetestPLHIVOnART(sheet, params, projection)
        import_Shiny90NumRetestPLHIVNoART(sheet, params, projection)
        import_Shiny90NumNewDiagnoses(sheet, params, projection)
        import_Shiny90PosRate(sheet, params, projection)
        import_Shiny90YieldNewDiagn(sheet, params, projection)
        import_Shiny90IsFitted(sheet, params, projection)
        import_KnowledgeOfStatusInputType(sheet, params, projection)
        import_KnowledgeOfStatusInput(sheet, params, projection)
        import_KnowledgeOfStatusFileTitle(sheet, params, projection)
        import_ViralSuppressionInputType(sheet, params, projection)
        import_ViralSuppressionInput(sheet, params, projection)
        import_ViralSuppressionThreshold(sheet, params, projection)
        import_ChildAnnRateProgressLowerCD4(sheet, params, projection)
        import_ChildDistNewInfectionsCD4(sheet, params, projection)
        import_ChildMortByCD4NoART(sheet, params, projection)
        import_ChildMortalityRates(sheet, params, projection)
        import_ChildMortalityRatesMultiplier(sheet, params, projection)
        import_ChildMortByCD4WithART0to6(sheet, params, projection)
        import_ChildMortByCD4WithART7to12(sheet, params, projection)
        import_ChildMortByCD4WithARTGT12(sheet, params, projection)
        import_ChildARTDist(sheet, params, projection)
        import_EffectTreatChild(sheet, params, projection)
        import_ChildWeightBands(sheet, params, projection)
        import_AdultAnnRateProgressLowerCD4(sheet, params, projection)
        import_AdultDistNewInfectionsCD4(sheet, params, projection)
        import_AdultMortByCD4NoART(sheet, params, projection)
        import_AdultInfectReduc(sheet, params, projection)
        import_MortalityRates(sheet, params, projection)
        import_MortalityRatesMultiplier(sheet, params, projection)
        import_AdultMortByCD4WithART0to6(sheet, params, projection)
        import_AdultMortByCD4WithART7to12(sheet, params, projection)
        import_AdultMortByCD4WithARTGT12(sheet, params, projection)
        import_TFRRegion(sheet, params, projection)
        import_HIVTFRCustomFlag(sheet, params, projection)
        import_HIVTFR(sheet, params, projection)
        import_TFRInputType(sheet, params, projection)
        import_FertCD4Discount(sheet, params, projection)
        import_RatioWomenOnART(sheet, params, projection)
        import_FRRFitInput(sheet, params, projection)
        import_FRRbyLocation(sheet, params, projection)
        import_TransEffAssump(sheet, params, projection)
        import_DALYDisabilityWeights(sheet, params, projection)
        import_NewARTPatAlloc(sheet, params, projection)
        import_NewARTPatAllocationMethod(sheet, params, projection)
        import_RiskPopOrphans(sheet, params, projection)
        import_ECDCValues(sheet, params, projection)
        import_ECDCFQName(sheet, params, projection)
        import_NosocomialInfectionsByAge(sheet, params, projection)
        import_HIVMigrantsByAgeSex(sheet, params, projection)
        import_IncidenceInput1970(sheet, params, projection)
        import_CSAVRInputAIDSDeathsSource(sheet, params, projection)
        import_CSAVRInputAIDSDeathsSourceName(sheet, params, projection)
        import_CSAVRInputAIDSDeaths(sheet, params, projection)
        import_CSAVRInputAIDSDeathsBySex(sheet, params, projection)
        import_CSAVRInputAIDSDeathsBySexAge(sheet, params, projection)
        import_CSAVRInputNewDiagnoses(sheet, params, projection)
        import_CSAVRInputNewDiagnosesBySex(sheet, params, projection)
        import_CSAVRInputNewDiagnosesBySexAge(sheet, params, projection)
        import_CSAVRInputNewDiagnosesBySexAgeCD4(sheet, params, projection)
        import_CSAVRInputCD4DistAtDiag(sheet, params, projection)
        import_FitIncidencePopulationValue(sheet, params, projection)
        import_AIDSMortalityAllAges(sheet, params, projection)
        import_AnnualInterruptionRate(sheet, params, projection)
        import_IncreasedLikelihoodOfReinit(sheet, params, projection)
        import_OffARTMortRateMultiplier(sheet, params, projection)
        import_ChildAnnualInterruptionRate(sheet, params, projection)
        import_ChildIncreasedLikelihoodOfReinit(sheet, params, projection)
        import_ChildOffARTMortRateMultiplier(sheet, params, projection)
        import_CSAVRFitOptions(sheet, params, projection)
        import_FitIncidenceParameters(sheet, params, projection)
        import_FitIncidenceIncScaleParameters(sheet, params, projection)
        import_FitIncidenceUncertaintyParams(sheet, params, projection)
        import_CSAVRConstrainPLHIVGTNumART(sheet, params, projection)
        import_FitIncidenceTypeOfFit(sheet, params, projection)
        import_CSAVRAdjustIRRs(sheet, params, projection)
        # import_FitIncidenceFitMethod(sheet, params, projection)
        import_CSAVRMetaData(sheet, params, projection)
        import_MeanCD4atDiagnosis(sheet, params, projection)
        import_MeanCD4atDiagnosisByAgeSex(sheet, params, projection)
        import_TimeInfToDiag(sheet, params, projection)
        import_PropOfDiagnosed(sheet, params, projection)
        import_PropOfDiagnosedNoART(sheet, params, projection)
        import_PropofDiagnosedByAgeSexCD4(sheet, params, projection)
        import_CSAVRNumPLHIV(sheet, params, projection)
        import_CSAVRNumPLHIVByAgeSexCD4(sheet, params, projection)
        import_CSAVRNumDiagnosed(sheet, params, projection)
        import_CSAVRNumDiagnosedByAgeSexCD4(sheet, params, projection)
        import_CSAVRAIDSDeaths(sheet, params, projection)
        import_CSAVRAIDSDeathsByAgeSex(sheet, params, projection)
        import_CSAVRNumNewInfections(sheet, params, projection)
        import_CSAVRIncidenceByFit(sheet, params, projection)
        import_HIVSexRatio(sheet, params, projection)
        import_CSAVRHIVSexRatio(sheet, params, projection)
        import_DistOfHIV(sheet, params, projection)
        import_CSAVRDistOfHIV(sheet, params, projection)

        import_SAPFittingValues(sheet, params, projection)
        
        # import_FittingAICData(sheet, params, projection)
        # import_IRRFittingValues(sheet, params, projection)
        # import_HIVSexRatioFittingValues(sheet, params, projection)

        # import_ARTTreatFittingData(sheet, params, projection)
        # import_ARTTreatFitDistOfHIV(sheet, params, projection)
        # import_ARTTreatFitHIVSexRatio(sheet, params, projection)
        
        import_AIDS45q15(sheet, params, projection)
        import_NonAIDS45q15(sheet, params, projection)
        import_Total45q15(sheet, params, projection)
        import_Under5MortRate(sheet, params, projection)
        import_PMTCTProgEstNeed(sheet, params, projection)
        import_NumberOnART(sheet, params, projection)
        import_ARTCovByAge(sheet, params, projection)
        import_KeyPops(sheet, params, projection)
        import_KeyPopsYear(sheet, params, projection)
        import_KeyPopsFName(sheet, params, projection)
        import_PregWomenPrevRoutineTest(sheet, params, projection)
        import_PregWomenPrev(sheet, params, projection)
        import_PrevSurveyData(sheet, params, projection)
        import_PrevSurveyUsed(sheet, params, projection)
        import_PrevSurveyName(sheet, params, projection)
        import_PrevSurveyYear(sheet, params, projection)
        import_ARTCovSurveyData(sheet, params, projection)
        import_ARTCovSurveyUsed(sheet, params, projection)
        import_ARTCovSurveyName(sheet, params, projection)
        import_ARTCovSurveyYear(sheet, params, projection)
        import_MortRateByAge(sheet, params, projection)
        import_AllCauseMortality(sheet, params, projection)
        import_AIDSMortality(sheet, params, projection)
        import_NumberOnARTByAge(sheet, params, projection)
        import_NewlyStartingART(sheet, params, projection)
        import_AdultsChildrenStartingART(sheet, params, projection)
        import_PercentOfPop(sheet, params, projection)
        import_FirstYearOfEpidemic(sheet, params, projection)
        import_ARTCoverageSelection(sheet, params, projection)
        import_BFYearsRGIdx(sheet, params, projection)
        import_BFArvRGIdx(sheet, params, projection)
        import_ChildHIVMortARTRegion(sheet, params, projection)
        import_ChildHIVMortARTCustomFlag(sheet, params, projection)
        import_ChildARTDistRegion(sheet, params, projection)
        import_ChildARTDistCustomFlag(sheet, params, projection)
        import_AdultProgressRatesRegion(sheet, params, projection)
        import_AdultProgressRatesCustomFlag(sheet, params, projection)
        import_AdultHIVMortNoARTRegion(sheet, params, projection)
        import_AdultHIVMortNoARTCustomFlag(sheet, params, projection)
        import_AdultHIVMortARTRegion(sheet, params, projection)
        import_AdultHIVMortARTCustomFlag(sheet, params, projection)
        import_DALYBaseYear(sheet, params, projection)
        import_DALYDiscountRate(sheet, params, projection)
        import_DALYUseStandardLifeTable(sheet, params, projection)
        import_OrphansRegionalPattern(sheet, params, projection)
        import_IncidenceInput1970Bool(sheet, params, projection)
        import_IncidenceOptions(sheet, params, projection)
        import_IncidenceByFit(sheet, params, projection)
        import_FourDecPlaceID(sheet, params, projection)
        import_EPPPrevAdj(sheet, params, projection)
        import_EPPMaxAdjFactor(sheet, params, projection)
        import_EPPPopulationAges(sheet, params, projection)
        import_CustomSAPDataIndex(sheet, params, projection)
        import_IncEpidemicCustomFlagIdx(sheet, params, projection)
        import_SexRatioFromEPP(sheet, params, projection)
        import_HIVSexRatioFromEPP(sheet, params, projection)
        import_EpidemicTypeFromEPP(sheet, params, projection)
        import_AdultPrevalence(sheet, params, projection)
        import_NumOfEPPEpidemics(sheet, params, projection)
        import_EPPCountryName(sheet, params, projection)
        import_EPPEpiName(sheet, params, projection)
        import_EPPEpidemic(sheet, params, projection)
        import_EPPPrevData(sheet, params, projection)
        import_EPPIncData(sheet, params, projection)
        import_EPPPopData(sheet, params, projection)
        import_EPPSexRatio(sheet, params, projection)
        import_EPPBaseYrPop(sheet, params, projection)
        import_EPPIDUMortality(sheet, params, projection)
        import_EPPPathInfo(sheet, params, projection)
        import_EppAgeRange(sheet, params, projection)
        import_YrPtPrevalence_WB(sheet, params, projection)
        import_AIDSDeathsAmongIDU(sheet, params, projection)
        import_PropIDU_WB(sheet, params, projection)
        import_NonAIDSDeathsAmongIDU(sheet, params, projection)
        import_SexuallyActive15to19(sheet, params, projection)
        import_AIDSMortAllAgesFYrAdjIdx(sheet, params, projection)
        import_ValidationAllCauseDeathsART(sheet, params, projection)
        import_AdvOptsMeningitis(sheet, params, projection)
        import_PrevNeedFirstTime(sheet, params, projection)
        has_prev_need = not projection.get(AM_PreventionNeedsFirstTimeTag, True)
        if has_prev_need:
            import_PrevNeedShowVMMC(sheet, params, projection)
            import_PrevNeedKeyPop(sheet, params, projection)
            import_PrevNeedVMMC(sheet, params, projection)
            import_PrevNeedCondoms(sheet, params, projection)
            import_PrevNeedPrEP_V2(sheet, params, projection)
            import_PrevNeedPrEP_V3(sheet, params, projection)
        # remove the first time flag because data will be loaded
        if AM_PreventionNeedsFirstTimeTag in projection:
            del projection[AM_PreventionNeedsFirstTimeTag]
        import_PrEPParameters(sheet, params, projection)
        import_PrEPForPregnantWomen(sheet, params, projection)
        import_KOSNewDiagnosesAdults15Plus(sheet, params, projection)
        import_KOSNewDiagnosesChildren0to14(sheet, params, projection)
        import_KOSNewDiagnosesRecCD4Test(sheet, params, projection)
    
    # DP_TGX_PrEPParameters_MV                  = '<PrEPParameters MV>';
    # DP_TGX_PrEPForPregnantWomen_MV            = '<PrEPForPregnantWomen MV>';
# AM_PMTCTPrEPParametersTag = '<AM_PMTCTPrEPParameters_V1>'
# AM_PMTCTReceivingOralPrEPTag = '<AM_PMTCTReceivingOralPrEP_V1>'
# AM_PMTCTReceivingLongActingPrEPTag = '<AM_PMTCTReceivingLongActingPrEP_V1>'

    return True

def import_CustomFileYears(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<CustomFileYears MV>')
    if (modvarTagRow < 0): return
    modvar = projection[DP_CustomFileYearsTag]

    row = modvarTagRow + 2
    modvar['DP_CPopFirstYr'] = int(sheet.values[row, GB_RW_DataStartCol])
    modvar['DP_CPopFinalYr'] = int(sheet.values[row, GB_RW_DataStartCol + 1])

def import_CustomPopStopRescalingYear(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<CustomPopStopRescalingYear MV>')
    if (modvarTagRow < 0): return

    row = modvarTagRow + 2
    projection[DP_CustomPopStopRescalingYearTag] = int(sheet.values[row, GB_RW_DataStartCol])

def import_EdAdSource(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<EdAdSource MV>')
    if (modvarTagRow < 0): return
    # projection[AM_EdAdSourceTag] = []
    modvar = projection[PJN_UserSourceTag]

    row = modvarTagRow + 2
    sourceCount = int(sheet.values[row, GB_RW_DataStartCol])
    sourceCount = min(sourceCount, len(sheet.values[row]) - 1)
    for col in GBRange(GB_RW_DataStartCol+1, GB_RW_DataStartCol+sourceCount):
        if col <= len(sheet.values[row]) - 1:
            modvar.append(str(sheet.values[row, col]))

def import_ChangesLog(sheet, params, projection):  
    modvarTagRow = findTagRow(sheet, '<ChangesLog MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_ChangesLogTag]
    
    row = modvarTagRow + 2
    count = int(sheet.values[row, GB_RW_DataStartCol])
    for s in GBRange(1, count):
        if (GB_RW_DataStartCol + s) < len(sheet.values[row]):
            modvar.append(str(sheet.values[row, GB_RW_DataStartCol + s]))

def import_EdDmSource(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<EdDmSource MV>')
    if (modvarTagRow < 0): return
    # projection[DP_EdDmSourceTag] = []
    modvar = projection[PJN_UserSourceTag]

    row = modvarTagRow + 2
    sourceCount = int(sheet.values[row, GB_RW_DataStartCol])
    sourceCount = min(sourceCount, len(sheet.values[row]) - 1)
    for col in GBRange(GB_RW_DataStartCol+1, GB_RW_DataStartCol+sourceCount):
        if col <= len(sheet.values[row]) - 1:
            modvar.append(str(sheet.values[row, col]))

def import_DPSources(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<DPSources MV>')
    if (modvarTagRow < 0): return
    modvar = projection[DP_DPSourcesTag]

    row = modvarTagRow + 2
    modvar['Provider'] = sheet.values[row, GB_RW_DataStartCol]
    modvar['VersionNum'] = sheet.values[row + 1, GB_RW_DataStartCol]
    
    row += 2
    for i in GBRange(DP_UPD_Pop, DP_UPD_Migration):
      modvar['Sources'][i]['Name'] = sheet.values[row, GB_RW_DataStartCol]
      modvar['Sources'][i]['Summary'] = sheet.values[row, GB_RW_DataStartCol + 1]
      modvar['Sources'][i]['Source'] = sheet.values[row, GB_RW_DataStartCol + 2]
      modvar['Sources'][i]['Date'] = sheet.values[row, GB_RW_DataStartCol + 3]
      row += 1

def import_Sources(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<Sources MV>')
    if (modvarTagRow < 0): return

    row = modvarTagRow + 2

    projection[DP_DataSourceTag] = str(sheet.values[row, GB_RW_DataStartCol + 1])
    projection[AM_DataSourceTag] = str(sheet.values[row + 1, GB_RW_DataStartCol + 1])


def import_DefaultUPDLE(sheet, params, projection):    
    modvarTagRow = findTagRow(sheet, '<DefaultUPDLE MV>')
    if (modvarTagRow < 0): return
    modvar = projection[DP_DefaultUPDLETag]

    row = modvarTagRow + 4
    for sex in GBRange(GB_Male, GB_Female):
        values = modvar[sex]
        getRowOfYearVals(sheet, values, params, row)    
        row += 1

def import_DefaultUPDIMR(sheet, params, projection):    
    modvarTagRow = findTagRow(sheet, '<DefaultUPDIMR MV>')
    if (modvarTagRow < 0): return
    modvar = projection[DP_DefaultUPDIMRTag]

    row = modvarTagRow + 4
    for sex in GBRange(GB_Male, GB_Female):
        values = modvar[sex]
        getRowOfYearVals(sheet, values, params, row)    
        row += 1

def import_DefaultUPDCMR(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<DefaultUPDCMR MV>')
    if (modvarTagRow < 0): return
    modvar = projection[DP_DefaultUPDCMRTag]

    row = modvarTagRow + 4
    for sex in GBRange(GB_Male, GB_Female):
        values = modvar[sex]
        getRowOfYearVals(sheet, values, params, row)    
        row += 1

def import_DefaultUPDSurvRate(sheet, params, projection):    
    modvarTagRow = findTagRow(sheet, '<DefaultUPDSurvRate MV>')
    if (modvarTagRow < 0): return
    modvar = projection[DP_DefaultUPDSurvRateTag]

    row = modvarTagRow + 3
    sStart = int(sheet.values[row, GB_RW_DataStartCol])
    sEnd = int(sheet.values[row, GB_RW_DataStartCol + 1])
    row += 1
    aStart = int(sheet.values[row, GB_RW_DataStartCol])
    aEnd = int(sheet.values[row, GB_RW_DataStartCol + 1])
    row += 1

    for age in GBRange(aStart, aEnd):
        for sex in GBRange(sStart, sEnd):
            values = modvar[age][sex]
            getRowOfYearVals(sheet, values, params, row)    
            row += 1

def import_BigPop(sheet, params, projection):    
    modvarTagRow = findTagRow(sheet, '<BigPop MV3>')
    if (modvarTagRow < 0): return
    modvar = projection[DP_BigPopTag]

    row = modvarTagRow + 3
    
    for sex in GBRange(GB_Male, GB_Female):
        for age in GBRange(0, DP_MaxSingleAges):
            values = modvar[sex][age]
            getRowOfYearVals(sheet, values, params, row, rowIncludesFirstYear = True)    
            row += 1
    
    for age in GBRange(0, DP_MaxSingleAges):
        for year in GBRange(params.firstYear, params.finalYear):
            t = getYearIdx(year, params.firstYear)
            modvar[GB_BothSexes][age][t] = modvar[GB_Male][age][t] + modvar[GB_Female][age][t]

def import_TFR(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<TFR MV>')
    if (modvarTagRow < 0): return
    modvar = projection[DP_TFRTag]

    row = modvarTagRow + 2
    values = modvar
    getRowOfYearVals(sheet, values, params, row)    

def import_ASFR(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<ASFR MV>')
    if (modvarTagRow < 0): return
    modvar = projection[DP_ASFRTag]

    for year in GBRange(params.firstYear, params.finalYear):
        t = getYearIdx(year, params.firstYear)
        modvar[DP_AllAges][t] = 0

    row = modvarTagRow + 3
    for age in GBRange(DP_A15_19, DP_A45_49):
        values = modvar[age]
        getRowOfYearVals(sheet, values, params, row)  
        row += 1  
        
    for year in GBRange(params.firstYear, params.finalYear):
        t = getYearIdx(year, params.firstYear)
        modvar[DP_AllAges][t] = modvar[DP_AllAges][t] + values[t]

def import_UNPopASFR(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<UNPopASFR MV>')
    if (modvarTagRow < 0): return
    modvar = projection[DP_UNPopASFRTag]

    for year in GBRange(params.firstYear, params.finalYear):
        t = getYearIdx(year, params.firstYear)
        modvar[DP_AllAges][t] = 0

    row = modvarTagRow + 3
    for age in GBRange(DP_A15_19, DP_A45_49):
        values = modvar[age]
        getRowOfYearVals(sheet, values, params, row)  
        row += 1  
        
    for year in GBRange(params.firstYear, params.finalYear):
        t = getYearIdx(year, params.firstYear)
        modvar[DP_AllAges][t] = modvar[DP_AllAges][t] + values[t]

def import_ASFRTables(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<ASFRTables MV>')
    if (modvarTagRow < 0): return
    modvar = projection[DP_ASFRTablesTag]

    row = modvarTagRow + 2
    for m in GBRange(DP_ASFR_UNAfrica, DP_ASFR_Average):
        for r in GBRange(1, DP_ASFR_NumRows):
            for c in GBRange(1, DP_ASFR_NumCols):
                modvar[m, c, r] = float(sheet.values[row, GB_RW_DataStartCol + c - 1])
            row += 1

def import_ASFRNum(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<ASFRNum MV>')
    if (modvarTagRow < 0): return
    # modvar = projection[DP_ASFRNumTag]
    
    row = modvarTagRow + 2
    value = int(sheet.values[row, GB_RW_DataStartCol])
    if value != DP_INPUTTED_TABLE:
        projection[DP_ASFRNumTag] = value
            
def import_ASFRCustomFlag(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<ASFRCustomFlag MV>')
    if (modvarTagRow < 0): return
    # modvar = projection[DP_ASFRCustomFlagTag]
    
    row = modvarTagRow + 2
    projection[DP_ASFRCustomFlagTag] = bool(int(sheet.values[row, GB_RW_DataStartCol]))

def import_SexBirthRatio(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<SexBirthRatio MV>')
    if (modvarTagRow < 0): return
    modvar = projection[DP_SexBirthRatioTag]

    row = modvarTagRow + 2
    values = modvar
    getRowOfYearVals(sheet, values, params, row)    

def import_LE(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<LE MV2>')
    if (modvarTagRow < 0): return
    modvar = projection[DP_LETag]

    row = modvarTagRow + 3
    for sex in GBRange(GB_Male, GB_Female):
        values = modvar[sex]
        getRowOfYearVals(sheet, values, params, row)    
        row += 1

def import_MigrRate(sheet, params, projection):    
    modvarTagRow = findTagRow(sheet, '<MigrRate MV2>')
    if (modvarTagRow < 0): return
    modvar = projection[DP_MigrRateTag]

    row = modvarTagRow + 4
    values = modvar[GB_Male][DP_AllAges]
    getRowOfYearVals(sheet, values, params, row)    
    
    row += 2
    values = modvar[GB_Female][DP_AllAges]
    getRowOfYearVals(sheet, values, params, row)  

def import_MigrAgeDist(sheet, params, projection):    
    modvarTagRow = findTagRow(sheet, '<MigrAgeDist MV2>')
    if (modvarTagRow < 0): return
    modvar = projection[DP_MigrAgeDistTag]

    row = modvarTagRow + 3
    
    for sex in GBRange(GB_Male, GB_Female):
        for age in GBRange(DP_A0_4, DP_MAX_AGE):
            values = modvar[sex][age]
            getRowOfYearVals(sheet, values, params, row)    
            row += 1

def import_ModelLifeFileName(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<ModelLifeFileName MV2>')
    if (modvarTagRow < 0): return
    # modvar = projection[DP_ModelLifeFileNameTag]

    row = modvarTagRow + 3
    projection[DP_ModelLifeFileNameTag] = str(sheet.values[row, GB_RW_DataStartCol])

def import_UseFYrSingleAges(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<UseFYrSingleAges MV2>')
    if (modvarTagRow < 0): return
    # modvar = projection[DP_UseFYrSingleAgesTag]

    row = modvarTagRow + 3
    projection[DP_UseFYrSingleAgesTag] = bool(int(sheet.values[row, GB_RW_DataStartCol]))

def import_RegionalAdjustPopData(sheet, params, projection):    
    modvarTagRow = findTagRow(sheet, '<RegionalAdjustPopData MV2>')
    if (modvarTagRow < 0): return
    modvar = projection[DP_RegionalAdjustPopDataTag]

    row = modvarTagRow + 3
    
    for sex in GBRange(GB_Male, GB_Female):  
        for age in GBRange(0, 80):
            values = modvar[sex][age]
            getRowOfYearVals(sheet, values, params, row)    
            row += 1
        row += 1 # skip total row
    pass

def import_RegionalAdjustPopCBState(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<RegionalAdjustPopCBState MV>')
    if (modvarTagRow < 0): return
    # modvar = projection[DP_RegionalAdjustPopCBStateTag]

    row = modvarTagRow + 2
    projection[DP_RegionalAdjustPopCBStateTag] = bool(int(sheet.values[row, GB_RW_DataStartCol]))

def import_RegionalAdjustPopFName(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<RegionalAdjustPopFName MV>')
    if (modvarTagRow < 0): return
    # modvar = projection[DP_RegionalAdjustPopFNameTag]

    row = modvarTagRow + 2
    projection[DP_RegionalAdjustPopFNameTag] = str(sheet.values[row, GB_RW_DataStartCol])

def import_RegionalAdjustPopFDate(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<RegionalAdjustPopFDate MV>')
    if (modvarTagRow < 0): return
    # modvar = projection[DP_RegionalAdjustPopFDateTag]

    row = modvarTagRow + 2
    projection[DP_RegionalAdjustPopFDateTag] = str(sheet.values[row, GB_RW_DataStartCol])

def import_LifeTableNum(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<LifeTableNum MV2>')
    if (modvarTagRow < 0): return
    # modvar = projection[DP_LifeTableNumTag]

    row = modvarTagRow + 3
    projection[DP_LifeTableNumTag] = int(sheet.values[row, GB_RW_DataStartCol])

def import_SurvRate(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<SurvRate MV2>')
    if (modvarTagRow < 0): return
    modvar = projection[DP_SurvRateTag]

    row = modvarTagRow + 3
    for sex in GBRange(GB_Male, GB_Female):
        for sr in GBRange(1, 82):
            values = modvar[sr][sex]
            getRowOfYearVals(sheet, values, params, row)    
            row += 1

# AM

def import_CD4ThreshHold(sheet, params, projection):    
    modvarTagRow = findTagRow(sheet, '<CD4ThreshHold MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_CD4ThreshHoldTag]

    row = modvarTagRow + 2
    
    for pernum in GBRange(DP_Number, DP_Percent):
        for age in GBRange(DP_AgeLT11Mths, DP_AgeGT5Years):
            values = modvar[pernum][age]
            getRowOfYearVals(sheet, values, params, row)    
            row += 1

def import_PopsEligTreat(sheet, params, projection):    
    modvarTagRow = findTagRow(sheet, '<PopsEligTreat MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_PopsEligTreatTag]

    row = modvarTagRow + 3
    
    for pop in GBRange(1, DP_EligTreatPopsMax):
            modvar[pop]['Eligible'] = bool(int(sheet.values[row, GB_RW_DataStartCol]))
            modvar[pop]['PercentHIV'] = float(sheet.values[row, GB_RW_DataStartCol + 1])
            modvar[pop]['Year'] = int(sheet.values[row, GB_RW_DataStartCol + 2])
            row += 1
            
def import_AgeHIVChildOnTreatment(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<AgeHIVChildOnTreatment MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_AgeHIVChildOnTreatmentTag]

    row = modvarTagRow + 2
    values = modvar
    getRowOfYearVals(sheet, values, params, row)   
            
def import_CD4ThreshHoldAdults(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<CD4ThreshHoldAdults MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_CD4ThreshHoldAdultsTag]

    row = modvarTagRow + 2
    values = modvar
    getRowOfYearVals(sheet, values, params, row)   

def import_InfantFeedingOptions(sheet, params, projection):    
    modvarTagRow = findTagRow(sheet, '<InfantFeedingOptions MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_InfantFeedingOptionsTag]

    row = modvarTagRow + 2
    
    for id in GBRange(DP_NotInPMTCT, DP_InPMTCT):
        for r in GBRange(1, DP_InfantFeedingMths):
            values = modvar[r][id]
            getRowOfYearVals(sheet, values, params, row)    
            row += 1
    pass

def import_ARVRegimen(sheet, params, projection):    
    modvarTagRow = findTagRow(sheet, '<ARVRegimen MV3>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_ARVRegimenTag]
    
    row = modvarTagRow + 2

    #   (* No prophylaxis *)
    values = modvar[DP_PrenatalProphylaxis][DP_NoProphylaxis][DP_Percent]
    getRowOfYearVals(sheet, values, params, row, startCol = GB_RW_DataStartCol + 1)    
    row += 1

    #   (* Single dose nevir *)
    values = modvar[DP_PrenatalProphylaxis][DP_SingleDoseNevir][DP_Number]
    getRowOfYearVals(sheet, values, params, row, startCol = GB_RW_DataStartCol + 1)    
    row += 1
    values = modvar[DP_PrenatalProphylaxis][DP_SingleDoseNevir][DP_Percent]
    getRowOfYearVals(sheet, values, params, row, startCol = GB_RW_DataStartCol + 1)    
    row += 1
    
    #   (* Dual ARV *)
    values = modvar[DP_PrenatalProphylaxis][DP_DualARV][DP_Number]
    getRowOfYearVals(sheet, values, params, row, startCol = GB_RW_DataStartCol + 1)    
    row += 1
    values = modvar[DP_PrenatalProphylaxis][DP_DualARV][DP_Percent]
    getRowOfYearVals(sheet, values, params, row, startCol = GB_RW_DataStartCol + 1)    
    row += 1

    #   (* Option A - maternal *)
    values = modvar[DP_PrenatalProphylaxis][DP_OptA][DP_Number]
    getRowOfYearVals(sheet, values, params, row, startCol = GB_RW_DataStartCol + 1)    
    row += 1
    values = modvar[DP_PrenatalProphylaxis][DP_OptA][DP_Percent]
    getRowOfYearVals(sheet, values, params, row, startCol = GB_RW_DataStartCol + 1)    
    row += 1

    #   (* Option B - triple prophylaxis from 14 weeks *)
    values = modvar[DP_PrenatalProphylaxis][DP_OptB][DP_Number]
    getRowOfYearVals(sheet, values, params, row, startCol = GB_RW_DataStartCol + 1)    
    row += 1
    values = modvar[DP_PrenatalProphylaxis][DP_OptB][DP_Percent]
    getRowOfYearVals(sheet, values, params, row, startCol = GB_RW_DataStartCol + 1)    
    row += 1
    
    #   (* Triple ART started before pregnancy *)
    values = modvar[DP_PrenatalProphylaxis][DP_TripleARTBefPreg][DP_Number]
    getRowOfYearVals(sheet, values, params, row, startCol = GB_RW_DataStartCol + 1)    
    row += 1
    values = modvar[DP_PrenatalProphylaxis][DP_TripleARTBefPreg][DP_Percent]
    getRowOfYearVals(sheet, values, params, row, startCol = GB_RW_DataStartCol + 1)    
    row += 1
    
    #   (* Triple ART started during pregnancy *)
    values = modvar[DP_PrenatalProphylaxis][DP_TripleARTDurPreg][DP_Number]
    getRowOfYearVals(sheet, values, params, row, startCol = GB_RW_DataStartCol + 1)    
    row += 1
    values = modvar[DP_PrenatalProphylaxis][DP_TripleARTDurPreg][DP_Percent]
    getRowOfYearVals(sheet, values, params, row, startCol = GB_RW_DataStartCol + 1)    
    row += 1
   
    #   (* Triple ART started during pregnancy - Late *)
    values = modvar[DP_PrenatalProphylaxis][DP_TripleARTDurPreg_Late][DP_Number]
    getRowOfYearVals(sheet, values, params, row, startCol = GB_RW_DataStartCol + 1)    
    row += 1
    values = modvar[DP_PrenatalProphylaxis][DP_TripleARTDurPreg_Late][DP_Percent]
    getRowOfYearVals(sheet, values, params, row, startCol = GB_RW_DataStartCol + 1)    
    row += 1
    
    #   (* Total *)
    values = modvar[DP_PrenatalProphylaxis][DP_TotalTreat][DP_Number]
    getRowOfYearVals(sheet, values, params, row, startCol = GB_RW_DataStartCol + 1)    
    row += 1
    
    #   (* Postnatal prophylaxis *)
    
    #   (* No prophylaxis *)
    values = modvar[DP_PostnatalProphylaxis][DP_NoProphylaxis][DP_Percent]
    getRowOfYearVals(sheet, values, params, row, startCol = GB_RW_DataStartCol + 1)    
    row += 1
    
    #   (* Option A *)
    values = modvar[DP_PostnatalProphylaxis][DP_OptA][DP_Number]
    getRowOfYearVals(sheet, values, params, row, startCol = GB_RW_DataStartCol + 1)    
    row += 1
    values = modvar[DP_PostnatalProphylaxis][DP_OptA][DP_Percent]
    getRowOfYearVals(sheet, values, params, row, startCol = GB_RW_DataStartCol + 1)    
    row += 1
    
    #   (* Option B *)
    values = modvar[DP_PostnatalProphylaxis][DP_OptB][DP_Number]
    getRowOfYearVals(sheet, values, params, row, startCol = GB_RW_DataStartCol + 1)    
    row += 1
    values = modvar[DP_PostnatalProphylaxis][DP_OptB][DP_Percent]
    getRowOfYearVals(sheet, values, params, row, startCol = GB_RW_DataStartCol + 1)    
    row += 1
    
    #   (* Total *)
    values = modvar[DP_PostnatalProphylaxis][DP_TotalTreat][DP_Number]
    getRowOfYearVals(sheet, values, params, row, startCol = GB_RW_DataStartCol + 1)    
    row += 1

    #   (* Option A *)
    values = modvar[DP_AnnDropPostnatalProph][DP_OptA][DP_Percent]
    getRowOfYearVals(sheet, values, params, row, startCol = GB_RW_DataStartCol + 1)    
    row += 1

    #   (* Option B *)
    values = modvar[DP_AnnDropPostnatalProph][DP_OptB][DP_Percent]
    getRowOfYearVals(sheet, values, params, row, startCol = GB_RW_DataStartCol + 1)    
    row += 1
    
    #   (* ART 0-12 months BF *)
    values = modvar[DP_AnnDropPostnatalProph][DP_ART0_12MthsBF][DP_Percent]
    getRowOfYearVals(sheet, values, params, row, startCol = GB_RW_DataStartCol + 1)    
    row += 1

    #   (* ART 12+ months BF *)
    values = modvar[DP_AnnDropPostnatalProph][DP_ARTGT12MthsBF][DP_Percent]
    getRowOfYearVals(sheet, values, params, row, startCol = GB_RW_DataStartCol + 1)    
    row += 1

def import_PatientsReallocated(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<DP_TGX_PatientsReallocated_MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_PatientsReallocatedTag]

    row = modvarTagRow + 2
    values = modvar
    getRowOfYearVals(sheet, values, params, row)  

def import_PercentARTDelivery(sheet, params, projection):    
    modvarTagRow = findTagRow(sheet, '<PercentARTDelivery MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_PercentARTDeliveryTag]

    row = modvarTagRow + 2
    
    for i in GBRange(DP_OnARTAtDelivery, DP_StartingARTAtDelivery):
        values = modvar[i]
        getRowOfYearVals(sheet, values, params, row)    
        row += 1

def import_PregTermAbortionPerNum(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<PregTermAbortionPerNum MV2>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_PregTermAbortionPerNumTag]

    row = modvarTagRow + 2
    values = modvar
    getRowOfYearValsInt(sheet, values, params, row)  

def import_PregTermAbortion(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<PregTermAbortion MV3>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_PregTermAbortionTag]

    row = modvarTagRow + 2
    values = modvar
    getRowOfYearVals(sheet, values, params, row)  

def import_MedCD4CountInit(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<MedCD4CountInit MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_MedCD4CountInitTag]

    row = modvarTagRow + 2
    values = modvar
    getRowOfYearVals(sheet, values, params, row)  

def import_PercLostFollowup(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<PercLostFollowup MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_PercInterruptedTag]

    row = modvarTagRow + 2
    values = modvar
    getRowOfYearVals(sheet, values, params, row)   

def import_NumberInitTreatmentReinit(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<NumberInitTreatmentReinits MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_NumberInitTreatmentReinitsTag]

    row = modvarTagRow + 2
    values = modvar
    getRowOfYearVals(sheet, values, params, row)  
    
    for year in GBRange(params.firstYear, DP_FirstYearOfART - 1):
        t = getYearIdx(year, params.firstYear)
        values[t] = 0

def import_NumNewlyInitART(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<NumNewlyInitART MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_NumNewlyInitARTTag]

    row = modvarTagRow + 2
    for sex in GBRange(GB_Male, GB_Female):
        values = modvar[sex]
        getRowOfYearVals(sheet, values, params, row)    
        row += 1

def import_PercLostFollowupChild(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<PercLostFollowupChild MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_PercInterruptedChildTag]

    row = modvarTagRow + 2
    values = modvar
    getRowOfYearVals(sheet, values, params, row)  
    
    for year in GBRange(params.firstYear, DP_FirstYearOfART - 1):
        t = getYearIdx(year, params.firstYear)
        values[t] = 0

def import_NumberInitTreatmentReinitsChild(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<NumberInitTreatmentReinitsChild MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_NumberInitTreatmentReinitsChildTag]

    row = modvarTagRow + 2
    values = modvar
    getRowOfYearVals(sheet, values, params, row)  
    
    for year in GBRange(params.firstYear, DP_FirstYearOfART - 1):
        t = getYearIdx(year, params.firstYear)
        values[t] = 0

def import_NumNewlyInitARTChild(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<NumNewlyInitARTChild MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_NumNewlyInitARTChildTag]

    row = modvarTagRow + 2
    values = modvar
    getRowOfYearVals(sheet, values, params, row)  
    
    for year in GBRange(params.firstYear, DP_FirstYearOfART - 1):
        t = getYearIdx(year, params.firstYear)
        values[t] = 0

def import_HAARTBySex(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<HAARTBySex MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_HAARTBySexTag]

    row = modvarTagRow + 3
    for sex in GBRange(GB_BothSexes, GB_Female):
        values = modvar[sex]
        getRowOfYearVals(sheet, values, params, row)  
        
        for year in GBRange(params.firstYear, DP_FirstYearOfART - 1):
            t = getYearIdx(year, params.firstYear)
            values[t] = 0
        row += 1

def import_HAARTBySexPerNum(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<HAARTBySexPerNum MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_HAARTBySexPerNumTag]

    row = modvarTagRow + 3
    for sex in GBRange(GB_BothSexes, GB_Female):
        values = modvar[sex]
        getRowOfYearVals(sheet, values, params, row)  
        
        for year in GBRange(params.firstYear, DP_FirstYearOfART - 1):
            t = getYearIdx(year, params.firstYear)
            values[t] = 0 # desktop does not do this.
        row += 1

def import_AdultARTAdjFactor(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<AdultARTAdjFactor>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_AdultARTAdjFactorTag]

    row = modvarTagRow + 3
    for sex in GBRange(GB_Male, GB_Female):
        values = modvar[sex]
        getRowOfYearVals(sheet, values, params, row)    
        row += 1
        
def import_AdultPatsAllocToFromOtherRegion(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<AdultPatsAllocToFromOtherRegion>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_AdultPatsAllocToFromOtherRegionTag]

    row = modvarTagRow + 3
    for sex in GBRange(GB_Male, GB_Female):
        values = modvar[sex]
        getRowOfYearVals(sheet, values, params, row)    
        row += 1

        
        
def import_AdultARTAdjFactorFlag(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<AdultARTAdjFactorFlag>')
    if (modvarTagRow < 0): return
    # modvar = projection[AM_AdultARTAdjFactorFlagTag]

    row = modvarTagRow + 2
    projection[AM_AdultARTAdjFactorFlagTag] = bool(int(sheet.values[row, GB_RW_DataStartCol]))

def import_CD4Coverage(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<CD4Coverage MV2>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_CD4CoverageTag]
    
    row = modvarTagRow + 3

    for perNum in GBRange(DP_CD4Percent, DP_CD4Number):
        for i in GBRange(DP_CD4_GT500, DP_CD4_LT50):
            values = modvar[perNum][i]
            getRowOfYearVals(sheet, values, params, row)    
            row += 1

            for year in GBRange(params.firstYear, DP_FirstYearOfART - 1):
                t = getYearIdx(year, params.firstYear)
                values[t] = 0
        row += 1

def import_ARTByAgeInputType(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<ARTByAgeInputType MV>')
    if (modvarTagRow < 0): return
    # modvar = projection[AM_ARTByAgeInputTypeTag]

    row = modvarTagRow + 2
    projection[AM_ARTByAgeInputTypeTag] = int(sheet.values[row, GB_RW_DataStartCol])

def import_ARTByAge5YearAG(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<ARTByAge5YearAG MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_ARTByAge5YearAGTag]

    row = modvarTagRow + 3
    for sex in GBRange(GB_Male, GB_Female):
        for age in GBRange(DP_A0_4, DP_A80_Up):
            values = modvar[sex][age]
            getRowOfYearVals(sheet, values, params, row)    
            row += 1

            for year in GBRange(params.firstYear, DP_FirstYearOfART - 1):
                t = getYearIdx(year, params.firstYear)
                values[t] = 0

def import_ARTByAgeGAMAG(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<ARTByAgeGAMAG MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_ARTByAgeGAMAGTag]

    row = modvarTagRow + 3
    for sex in GBRange(GB_Male, GB_Female):
        for age in GBRange(DP_A0_4, DP_GAMAG_A50Plus):
            values = modvar[sex][age]
            getRowOfYearVals(sheet, values, params, row)    
            row += 1

            for year in GBRange(params.firstYear, DP_FirstYearOfART - 1):
                t = getYearIdx(year, params.firstYear)
                values[t] = 0

def import_CovPopsEligTreat(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<CovPopsEligTreat MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_CovPopsEligTreatTag]

    row = modvarTagRow + 3
    for pop in GBRange(DP_EligTreatPregnantWomen, DP_EligTreatPopsMax):
        values = modvar[pop]
        getRowOfYearVals(sheet, values, params, row)    
        row += 1

def import_ChildTreatInputs(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<ChildTreatInputs MV3>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_ChildTreatInputsTag]

    initValues = modvar.copy()
    row = modvarTagRow + 2
    for id in GBRange(DP_PerChildHIVPosCot, DP_PerChildHIVRecART10_14):
        values = modvar[id]
        getRowOfYearVals(sheet, values, params, row)    
        row += 1

def import_ChildARTAdjFactor(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<ChildARTAdjFactor MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_ChildARTAdjFactorTag]

    row = modvarTagRow + 2
    values = modvar
    getRowOfYearVals(sheet, values, params, row)  

def import_ChildARTAdjFactorFlag(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<ChildARTAdjFactorFlag>')
    if (modvarTagRow < 0): return
    # modvar = projection[AM_ChildARTAdjFactorFlagTag]

    row = modvarTagRow + 2
    projection[AM_ChildARTAdjFactorFlagTag] = bool(int(sheet.values[row, GB_RW_DataStartCol]))

def import_ChildARTByAgeGroupPerNum(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<ChildARTByAgeGroupPerNum MV2>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_ChildARTByAgeGroupPerNumTag]

    row = modvarTagRow + 2
    for id in GBRange(DP_PerChildHIVPosCot, DP_PerChildHIVRecART10_14):
        values = modvar[id]
        getRowOfYearVals(sheet, values, params, row)    
        row += 1

def import_ANCTestingValues(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<ANCTestingValues MV4>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_ANCTestingValuesTag]

    row = modvarTagRow + 2
    for id in GBRange(DP_FirstANCVisits, DP_HIVNegFirstANCVisit):
        values = modvar[id]
        getRowOfYearVals(sheet, values, params, row)    
        row += 1

# def import_NewInfectionsLessImmigrants(sheet, params, projection):   
#     modvarTagRow = findTagRow(sheet, '<NewInfectionsLessImmigrants MV>')
#     if (modvarTagRow < 0): return
#     modvar = projection[AM_NewInfectionsLessImmigrantsTag]

#     row = modvarTagRow + 3
#     for sex in GBRange(GB_BothSexes, GB_Female):
#         values = np.zeros(params.finalYear - params.firstYear + 1).tolist()  #old all single-ages sum row
#         getRowOfYearVals(sheet, values, params, row)    
#         row += 1

#         for age in GBRange(0, 80):
#             values = modvar[sex][age]
#             getRowOfYearVals(sheet, values, params, row)    
#             row += 1
            
def import_HIVTesting(sheet, params, projection):   
    # It was requested that we support both V2 and V3 for this modvar when importing desktop projections
    modvarTagRowV2 = findTagRow(sheet, '<HIVTesting MV2>')
    if (modvarTagRowV2 < 0): pass
    else:
        modvar = projection[AM_HIVTestingTag]

        row = modvarTagRowV2 + 2
                                              #non-calcstate projection or no 'first-year' values imported
        col = 3
        for year in GBRange(params.firstYear, params.finalYear):
            t = getYearIdx(year, params.firstYear)
            if not sheet.values[row, col] == '':
                modvar[t]['DiagTests'] = getFloatValue(sheet, row, col, DPNotAvail)
                modvar[t]['PosTests'] = getFloatValue(sheet, row + 1, col, DPNotAvail)
                modvar[t]['HTSTests'] = getFloatValue(sheet, row + 2, col, DPNotAvail)
                modvar[t]['PosHTSTests'] = getFloatValue(sheet, row + 3, col, DPNotAvail)
                modvar[t]['ANCTests'] = getFloatValue(sheet, row + 4, col, DPNotAvail)
                modvar[t]['PosANCTests'] = getFloatValue(sheet, row + 5, col, DPNotAvail)
                modvar[t]['SelfTests'] = getFloatValue(sheet, row + 6, col, DPNotAvail)
                # Old fields which are no longer supported
                # modvar[t]['AssistedSelfTests'] = getFloatValue(sheet, row + 7, col, DPNotAvail)
                # modvar[t]['UnassistedSelfTests'] = getFloatValue(sheet, row + 8, col, DPNotAvail)
                # modvar[t]['AssistedPosReactiveSelfTests'] = getFloatValue(sheet, row + 9, col, DPNotAvail)
                # modvar[t]['PrimarySelfTests'] = getFloatValue(sheet, row + 10, col, DPNotAvail)
                # modvar[t]['SecondarySelfTests'] = getFloatValue(sheet, row + 11, col, DPNotAvail)
                # modvar[t]['PosHTSTestsWPrevReactiveSelfTest'] = getFloatValue(sheet, row + 12, col, DPNotAvail)
                # modvar[t]['IndexPartnerTests'] = getFloatValue(sheet, row + 13, col, DPNotAvail)
                # modvar[t]['PosIndexPartnerTests'] = getFloatValue(sheet, row + 14, col, DPNotAvail)
            col += 1
        return
    
    modvarTagRowV3 = findTagRow(sheet, '<HIVTesting MV3>')
    if (modvarTagRowV3 < 0): return
    modvar = projection[AM_HIVTestingTag]

    row = modvarTagRowV3 + 3
                                              #non-calcstate projection or no 'first-year' values imported
    col = 3
    for year in GBRange(params.firstYear, params.finalYear):
        t = getYearIdx(year, params.firstYear)
        if not sheet.values[row, col] == '':
            modvar[t]['DiagTests'] = getFloatValue(sheet, row, col, DPNotAvail)
            modvar[t]['PosTests'] = getFloatValue(sheet, row + 1, col, DPNotAvail)
            modvar[t]['HTSTests'] = getFloatValue(sheet, row + 2, col, DPNotAvail)
            modvar[t]['PosHTSTests'] = getFloatValue(sheet, row + 3, col, DPNotAvail)
            modvar[t]['ANCTests'] = getFloatValue(sheet, row + 4, col, DPNotAvail)
            modvar[t]['PosANCTests'] = getFloatValue(sheet, row + 5, col, DPNotAvail)
            modvar[t]['CommunityBasedTests'] = getFloatValue(sheet, row + 6, col, DPNotAvail)
            modvar[t]['CommunityBasedTestsHIVPos'] = getFloatValue(sheet, row + 7, col, DPNotAvail)
            modvar[t]['SelfTests'] = getFloatValue(sheet, row + 8, col, DPNotAvail)
            modvar[t]['TestsChild0t14'] = getFloatValue(sheet, row + 9, col, DPNotAvail)
            modvar[t]['TestsMen15Plus'] = getFloatValue(sheet, row + 10, col, DPNotAvail)
            modvar[t]['TestsFemale15Plus'] = getFloatValue(sheet, row + 11, col, DPNotAvail)
            modvar[t]['TestsTrans15Plus'] = getFloatValue(sheet, row + 12, col, DPNotAvail)
            modvar[t]['TestsHIVPosChild0t14'] = getFloatValue(sheet, row + 13, col, DPNotAvail)
            modvar[t]['TestsHIVPosMen15Plus'] = getFloatValue(sheet, row + 14, col, DPNotAvail)
            modvar[t]['TestsHIVPosFemale15Plus'] = getFloatValue(sheet, row + 15, col, DPNotAvail)
            modvar[t]['TestsHIVPosTrans15Plus'] = getFloatValue(sheet, row + 16, col, DPNotAvail)
        col += 1
    pass

def import_HIVTestingHTSTestsByAge(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<HIVTestingHTSTestsByAge MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_HIVTestingHTSTestsByAgeTag]

    row = modvarTagRow + 3

    for s in GBRange(GB_Male, GB_Female):
        for a in GBRange(DP_AllAges, DP_GAMAG_A50Plus):
            values = modvar[s][a]
            getRowOfYearVals(sheet, values, params, row)    
            row += 1

def import_Shiny90SurveyData(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<Shiny90SurveyData MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_Shiny90SurveyDataTag]
    emptyEntry = projection[AM_Shiny90SurveyData_MetaTag]['default']
    
    row = modvarTagRow + 2
    count = int(sheet.values[row, GB_RW_NotesCol])
    row += 1
    for s in GBRange(1, count):
        modvar.append(emptyEntry.copy())
        modvar[-1]['isUsed']        = bool(int(sheet.values[row, 1]))
        modvar[-1]['surveyID']      = sheet.values[row, 2]
        modvar[-1]['year']          = int(sheet.values[row, 3])
        modvar[-1]['ageGroup']      = int(sheet.values[row, 4])
        modvar[-1]['sex']           = int(sheet.values[row, 5])
        modvar[-1]['HIVStatus']     = int(sheet.values[row, 6])
        modvar[-1]['estimate']      = float(sheet.values[row, 7])
        modvar[-1]['standardError'] = float(sheet.values[row, 8])
        modvar[-1]['lowerBound']    = float(sheet.values[row, 9])
        modvar[-1]['upperBound']    = float(sheet.values[row, 10])
        modvar[-1]['count']         = int(sheet.values[row, 11])
        row += 1

def import_Shiny90ProgramData(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<Shiny90ProgramData MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_Shiny90ProgramDataTag]
    emptyEntry = projection[AM_Shiny90ProgramData_MetaTag]['default']
    
    row = modvarTagRow + 2
    count = int(sheet.values[row, GB_RW_NotesCol])
    row += 1
    for s in GBRange(1, count):
        modvar.append(emptyEntry.copy())
        modvar[-1]['isUsed']            = bool(int(sheet.values[row, 1]))
        modvar[-1]['year']              = int(sheet.values[row, 2])
        modvar[-1]['sex']               = int(sheet.values[row, 3])
        modvar[-1]['totalTests']        = int(sheet.values[row, 4])
        modvar[-1]['totalPosTests']     = float(sheet.values[row, 5])
        modvar[-1]['totalHTCTests']     = float(sheet.values[row, 6])
        modvar[-1]['totalPosHTCTests']  = float(sheet.values[row, 7])
        modvar[-1]['totalANCTests']     = float(sheet.values[row, 8])
        modvar[-1]['totalPosANCTests']  = int(sheet.values[row, 9])
        row += 1

def import_Shiny90AIDSDeathsFYear(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<Shiny90AIDSDeathsFYear MV>')
    if (modvarTagRow < 0): return

    row = modvarTagRow + 2
    projection[AM_Shiny90AIDSDeathsFYearTag] = int(sheet.values[row, GB_RW_DataStartCol])

def import_Shiny90Pop(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<Shiny90Pop MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_Shiny90PopTag]

    row = modvarTagRow + 2
    for HIV in GBRange(DP_D_All, DP_D_HIVPos):
        for sex in GBRange(GB_BothSexes, GB_Female):
            for age in GBRange(DP_S90_15_24, DP_S90_15Plus):
                for dataType in GBRange(DP_Number, DP_UpperBound):
                    values = modvar[HIV][sex][age][dataType]
                    getRowOfYearVals(sheet, values, params, row)    
                    row += 1

def import_Shiny90NumTests(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<Shiny90NumTests MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_Shiny90NumTestsTag]

    row = modvarTagRow + 2
    for HIV in GBRange(DP_D_All, DP_D_HIVPos):
        for sex in GBRange(GB_BothSexes, GB_Female):
            for age in GBRange(DP_S90_15_24, DP_S90_15Plus):
                for dataType in GBRange(DP_Number, DP_UpperBound):
                    values = modvar[HIV][sex][age][dataType]
                    getRowOfYearVals(sheet, values, params, row)    
                    row += 1

def import_Shiny90NumTested12M(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<Shiny90NumTested12M MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_Shiny90NumTested12MTag]

    row = modvarTagRow + 2
    for HIV in GBRange(DP_D_All, DP_D_HIVPos):
        for sex in GBRange(GB_BothSexes, GB_Female):
            for age in GBRange(DP_S90_15_24, DP_S90_15Plus):
                for dataType in GBRange(DP_Number, DP_UpperBound):
                    values = modvar[HIV][sex][age][dataType]
                    getRowOfYearVals(sheet, values, params, row)    
                    row += 1

def import_Shiny90TotalTests(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<Shiny90TotalTests MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_Shiny90TotalTestsTag]

    row = modvarTagRow + 2
    for HIV in GBRange(DP_D_All, DP_D_HIVPos):
        for sex in GBRange(GB_BothSexes, GB_Female):
            for age in GBRange(DP_S90_15_24, DP_S90_15Plus):
                for dataType in GBRange(DP_Number, DP_UpperBound):
                    values = modvar[HIV][sex][age][dataType]
                    getRowOfYearVals(sheet, values, params, row)    
                    row += 1

def import_Shiny90EverTested(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<Shiny90EverTested MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_Shiny90EverTestedTag]

    row = modvarTagRow + 2
    for HIV in GBRange(DP_D_All, DP_D_HIVPos):
        for sex in GBRange(GB_BothSexes, GB_Female):
            for age in GBRange(DP_S90_15_24, DP_S90_15Plus):
                for dataType in GBRange(DP_Number, DP_UpperBound):
                    values = modvar[HIV][sex][age][dataType]
                    getRowOfYearVals(sheet, values, params, row)    
                    row += 1

def import_Shiny90Diagnosed(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<Shiny90Diagnosed MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_Shiny90DiagnosedTag]

    row = modvarTagRow + 2
    for HIV in GBRange(DP_D_All, DP_D_HIVPos):
        for sex in GBRange(GB_BothSexes, GB_Female):
            for age in GBRange(DP_S90_15_24, DP_S90_15Plus):
                for dataType in GBRange(DP_Number, DP_UpperBound):
                    values = modvar[HIV][sex][age][dataType]
                    getRowOfYearVals(sheet, values, params, row)    
                    row += 1

def import_Shiny90NumAware(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<Shiny90NumberAware MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_Shiny90NumAwareTag]

    row = modvarTagRow + 2
    for HIV in GBRange(DP_D_All, DP_D_HIVPos):
        for sex in GBRange(GB_BothSexes, GB_Female):
            for age in GBRange(DP_S90_15_24, DP_S90_15Plus):
                for dataType in GBRange(DP_Number, DP_UpperBound):
                    values = modvar[HIV][sex][age][dataType]
                    getRowOfYearVals(sheet, values, params, row)    
                    row += 1

def import_Shiny90NumDiagnoses(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<Shiny90NumDiagnoses MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_Shiny90NumDiagnosesTag]

    row = modvarTagRow + 2
    for HIV in GBRange(DP_D_All, DP_D_HIVPos):
        for sex in GBRange(GB_BothSexes, GB_Female):
            for age in GBRange(DP_S90_15_24, DP_S90_15Plus):
                for dataType in GBRange(DP_Number, DP_UpperBound):
                    values = modvar[HIV][sex][age][dataType]
                    getRowOfYearVals(sheet, values, params, row)    
                    row += 1

def import_Shiny90NumDiagnosesMod(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<Shiny90NumDiagnosesMod MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_Shiny90NumDiagnosesModTag]

    row = modvarTagRow + 2
    for HIV in GBRange(DP_D_All, DP_D_HIVPos):
        for sex in GBRange(GB_BothSexes, GB_Female):
            for age in GBRange(DP_S90_15_24, DP_S90_15Plus):
                for dataType in GBRange(DP_Number, DP_UpperBound):
                    values = modvar[HIV][sex][age][dataType]
                    getRowOfYearVals(sheet, values, params, row)    
                    row += 1

def import_Shiny90NumLateDiagnoses(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<Shiny90NumLateDiagnoses MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_Shiny90NumLateDiagnosesTag]

    row = modvarTagRow + 2
    for HIV in GBRange(DP_D_All, DP_D_HIVPos):
        for sex in GBRange(GB_BothSexes, GB_Female):
            for age in GBRange(DP_S90_15_24, DP_S90_15Plus):
                for dataType in GBRange(DP_Number, DP_UpperBound):
                    values = modvar[HIV][sex][age][dataType]
                    getRowOfYearVals(sheet, values, params, row)    
                    row += 1

def import_Shiny90NotDiagHIV1Yr(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<Shiny90NotDiagHIV1Yr MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_Shiny90NotDiagHIV1YrTag]

    row = modvarTagRow + 2
    for HIV in GBRange(DP_D_All, DP_D_HIVPos):
        for sex in GBRange(GB_BothSexes, GB_Female):
            for age in GBRange(DP_S90_15_24, DP_S90_15Plus):
                for dataType in GBRange(DP_Number, DP_UpperBound):
                    values = modvar[HIV][sex][age][dataType]
                    getRowOfYearVals(sheet, values, params, row)    
                    row += 1

def import_Shiny90NumReTestHIVNeg(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<Shiny90NumReTestHIVNeg MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_Shiny90NumReTestHIVNeg_Tag]

    row = modvarTagRow + 2
    for HIV in GBRange(DP_D_All, DP_D_HIVPos):
        for sex in GBRange(GB_BothSexes, GB_Female):
            for age in GBRange(DP_S90_15_24, DP_S90_15Plus):
                for dataType in GBRange(DP_Number, DP_UpperBound):
                    values = modvar[HIV][sex][age][dataType]
                    getRowOfYearVals(sheet, values, params, row)    
                    row += 1

def import_Shiny90NumFirstTestHIVNeg(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<Shiny90NumFirstTestHIVNeg MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_Shiny90NumFirstTestHIVNeg_Tag]

    row = modvarTagRow + 2
    for HIV in GBRange(DP_D_All, DP_D_HIVPos):
        for sex in GBRange(GB_BothSexes, GB_Female):
            for age in GBRange(DP_S90_15_24, DP_S90_15Plus):
                for dataType in GBRange(DP_Number, DP_UpperBound):
                    values = modvar[HIV][sex][age][dataType]
                    getRowOfYearVals(sheet, values, params, row)    
                    row += 1


def import_Shiny90NumRetestPLHIVOnART(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<Shiny90NumRetestPLHIVOnART MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_Shiny90NumRetestPLHIVOnART_Tag]

    row = modvarTagRow + 2
    for HIV in GBRange(DP_D_All, DP_D_HIVPos):
        for sex in GBRange(GB_BothSexes, GB_Female):
            for age in GBRange(DP_S90_15_24, DP_S90_15Plus):
                for dataType in GBRange(DP_Number, DP_UpperBound):
                    values = modvar[HIV][sex][age][dataType]
                    getRowOfYearVals(sheet, values, params, row)    
                    row += 1


def import_Shiny90NumRetestPLHIVNoART(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<Shiny90NumRetestPLHIVNoART MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_Shiny90NumRetestPLHIVNoART_Tag]

    row = modvarTagRow + 2
    for HIV in GBRange(DP_D_All, DP_D_HIVPos):
        for sex in GBRange(GB_BothSexes, GB_Female):
            for age in GBRange(DP_S90_15_24, DP_S90_15Plus):
                for dataType in GBRange(DP_Number, DP_UpperBound):
                    values = modvar[HIV][sex][age][dataType]
                    getRowOfYearVals(sheet, values, params, row)    
                    row += 1


def import_Shiny90NumNewDiagnoses(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<Shiny90NumNewDiagnoses MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_Shiny90NumNewDiagnoses_Tag]

    row = modvarTagRow + 2
    for HIV in GBRange(DP_D_All, DP_D_HIVPos):
        for sex in GBRange(GB_BothSexes, GB_Female):
            for age in GBRange(DP_S90_15_24, DP_S90_15Plus):
                for dataType in GBRange(DP_Number, DP_UpperBound):
                    values = modvar[HIV][sex][age][dataType]
                    getRowOfYearVals(sheet, values, params, row)    
                    row += 1


def import_Shiny90PosRate(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<Shiny90PosRate MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_Shiny90PosRate_Tag]

    row = modvarTagRow + 2
    for HIV in GBRange(DP_D_All, DP_D_HIVPos):
        for sex in GBRange(GB_BothSexes, GB_Female):
            for age in GBRange(DP_S90_15_24, DP_S90_15Plus):
                for dataType in GBRange(DP_Number, DP_UpperBound):
                    values = modvar[HIV][sex][age][dataType]
                    getRowOfYearVals(sheet, values, params, row)    
                    row += 1


def import_Shiny90YieldNewDiagn(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<Shiny90YieldNewDiagn MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_Shiny90YieldNewDiagn_Tag]

    row = modvarTagRow + 2
    for HIV in GBRange(DP_D_All, DP_D_HIVPos):
        for sex in GBRange(GB_BothSexes, GB_Female):
            for age in GBRange(DP_S90_15_24, DP_S90_15Plus):
                for dataType in GBRange(DP_Number, DP_UpperBound):
                    values = modvar[HIV][sex][age][dataType]
                    getRowOfYearVals(sheet, values, params, row)    
                    row += 1

def import_Shiny90IsFitted(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<Shiny90IsFitted MV>')
    if (modvarTagRow < 0): return

    row = modvarTagRow + 2
    projection[AM_Shiny90IsFittedTag] = bool(int(sheet.values[row, GB_RW_DataStartCol]))

def import_KnowledgeOfStatusInputType(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<KnowledgeOfStatusInputType MV2>')
    if (modvarTagRow < 0): return
    # modvar = projection[AM_KnowledgeOfStatusInputTypeTag]

    row = modvarTagRow + 2
    projection[AM_KnowledgeOfStatusInputTypeTag] = int(sheet.values[row, GB_RW_DataStartCol])

def import_KnowledgeOfStatusInput(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<KnowledgeOfStatusInput MV4>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_KnowledgeOfStatusInputTag]

    row = modvarTagRow + 2
    for ageGroup in GBRange(DP_Cas_AG_Child, DP_Cas_AG_AdultFemale):
        values = modvar[ageGroup]
        getRowOfYearVals(sheet, values, params, row)    
        # for year in GBRange(DP_Cas_2010, DP_Cas_2025):
        #     modvar[ageGroup][year] = float(sheet.values[row, GB_RW_DataStartCol + year])
        row += 1

def import_KnowledgeOfStatusFileTitle(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<KnowledgeOfStatusFileTitle MV>')
    if (modvarTagRow < 0): return
    # modvar = projection[AM_KnowledgeOfStatusFileTitleTag]

    row = modvarTagRow + 2
    projection[AM_KnowledgeOfStatusFileTitleTag] = str(sheet.values[row, GB_RW_DataStartCol])

def import_ViralSuppressionInputType(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<ViralSuppressionInputType MV2>')
    if (modvarTagRow < 0): return
    # modvar = projection[AM_ViralSuppressionInputTypeTag]

    row = modvarTagRow + 2
    projection[AM_ViralSuppressionInputTypeTag] = int(sheet.values[row, GB_RW_DataStartCol])

def import_ViralSuppressionInput(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<ViralSuppressionInput MV4>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_ViralSuppressionInputTag]

    row = modvarTagRow + 2
    for ageGroup in GBRange(DP_Cas_AG_Child, DP_Cas_AG_AdultFemale):
        for dataType in GBRange(DP_VS_NumOnART, DP_VS_PLHIVSuppressed):
            values = modvar[ageGroup][dataType]
            getRowOfYearVals(sheet, values, params, row)    
            # for year in GBRange(DP_Cas_2010, DP_Cas_2025):
            #     modvar[ageGroup][dataType][year] = float(sheet.values[row, GB_RW_DataStartCol + year])
            row += 1

def import_ViralSuppressionThreshold(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<ViralSuppressionThreshold MV4>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_ViralSuppressionThresholdTag]

    row = modvarTagRow + 2
    values = modvar
    getRowOfYearVals(sheet, values, params, row)  
    # for year in GBRange(DP_Cas_2010, DP_Cas_2025):
    #     modvar[year] = float(sheet.values[row, GB_RW_DataStartCol + year])

def import_ChildAnnRateProgressLowerCD4(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<ChildAnnRateProgressLowerCD4 MV2>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_ChildAnnRateProgressLowerCD4Tag]

    row = modvarTagRow + 3
    for sex in GBRange(GB_Male, GB_Female):
        col = 0
        for a in GBRange(DP_A0t2, DP_A5t14):
            for c in GBRange(DP_CD4_Per_GT30, DP_CD4_Per_5_10):
                modvar[DP_Data][sex][a][c] = float(sheet.values[row, GB_RW_DataStartCol + col])
                col += 1
        row += 1

def import_ChildDistNewInfectionsCD4(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<ChildDistNewInfectionsCD4 MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_ChildDistNewInfectionsCD4Tag]

    row = modvarTagRow + 2
    col = 0
    for c in GBRange(DP_CD4_Per_GT30, DP_CD4_Per_LT5):
        modvar[DP_Data][c] = float(sheet.values[row, GB_RW_DataStartCol + col])
        col += 1

def import_ChildMortByCD4NoART(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<ChildMortByCD4NoART MV2>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_ChildMortByCD4NoARTTag]

    row = modvarTagRow + 2
    for a in GBRange(DP_A0t2, DP_A5t14):
        for b in GBRange(DP_P_Perinatal, DP_P_BF12):
            col = 0
            for c in GBRange(DP_CD4_Per_GT30, DP_CD4_Per_LT5):
                modvar[DP_Data][a][b][c] = float(sheet.values[row, GB_RW_DataStartCol + col])
                col += 1
            row += 1

def import_ChildMortalityRates(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<ChildMortalityRates MV2>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_ChildMortalityRatesTag]

    row = modvarTagRow + 2
    for age in GBRange(DP_CD4_0t4, DP_CD4_5t14):
        for timePeriod in GBRange(DP_MortRates_LT12Mo, DP_MortRates_GT12Mo):
            values = modvar[DP_Data][age][timePeriod]
            getRowOfYearVals(sheet, values, params, row)    
            row += 1

def import_ChildMortalityRatesMultiplier(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<ChildMortalityRatesMultiplier MV>')
    if (modvarTagRow < 0): return
    # modvar = projection[AM_ChildMortalityRatesMultiplierTag]

    row = modvarTagRow + 2
    projection[AM_ChildMortalityRatesMultiplierTag] = float(sheet.values[row, GB_RW_DataStartCol])

def import_ChildMortByCD4WithART0to6(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<ChildMortByCD4WithART0to6 MV2>')
    if (modvarTagRow < 0): return
    modvarCount = projection[AM_ChildMortByCD4WithART0to6Tag]
    modvarPerc = projection[AM_ChildMortByCD4WithART0to6PercTag]

    row = modvarTagRow + 2
    for sex in GBRange(GB_Male, GB_Female):
        col = 0
        for a in GBRange(DP_A0, DP_A3t4):
            for c in GBRange(DP_CD4_Per_GT30, DP_CD4_Per_LT5):
                modvarPerc[DP_Data][sex][a][c] = float(sheet.values[row, GB_RW_DataStartCol + col])
                col += 1
        for a in GBRange(DP_A5t9, DP_A10t14):
            for c in GBRange(DP_CD4_Ped_Top, DP_CD4_Ped_LT200):
                modvarCount[DP_Data][sex][a][c] = float(sheet.values[row, GB_RW_DataStartCol + col])
                col += 1
        row += 1


def import_ChildMortByCD4WithART7to12(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<ChildMortByCD4WithART7to12 MV>')
    if (modvarTagRow < 0): return
    modvarCount = projection[AM_ChildMortByCD4WithART7to12Tag]
    modvarPerc = projection[AM_ChildMortByCD4WithART7to12PercTag]

    row = modvarTagRow + 3
    for sex in GBRange(GB_Male, GB_Female):
        col = 0
        for a in GBRange(DP_A0, DP_A3t4):
            for c in GBRange(DP_CD4_Per_GT30, DP_CD4_Per_LT5):
                modvarPerc[DP_Data][sex][a][c] = float(sheet.values[row, GB_RW_DataStartCol + col])
                col += 1
        for a in GBRange(DP_A5t9, DP_A10t14):
            for c in GBRange(DP_CD4_Ped_Top, DP_CD4_Ped_LT200):
                modvarCount[DP_Data][sex][a][c] = float(sheet.values[row, GB_RW_DataStartCol + col])
                col += 1
        row += 1

def import_ChildMortByCD4WithARTGT12(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<ChildMortByCD4WithARTGT12 MV>')
    if (modvarTagRow < 0): return
    modvarCount = projection[AM_ChildMortByCD4WithARTGT12Tag]
    modvarPerc = projection[AM_ChildMortByCD4WithARTGT12PercTag]

    row = modvarTagRow + 3
    for sex in GBRange(GB_Male, GB_Female):
        col = 0
        for a in GBRange(DP_A0, DP_A3t4):
            for c in GBRange(DP_CD4_Per_GT30, DP_CD4_Per_LT5):
                modvarPerc[DP_Data][sex][a][c] = float(sheet.values[row, GB_RW_DataStartCol + col])
                col += 1
        for a in GBRange(DP_A5t9, DP_A10t14):
            for c in GBRange(DP_CD4_Ped_Top, DP_CD4_Ped_LT200):
                modvarCount[DP_Data][sex][a][c] = float(sheet.values[row, GB_RW_DataStartCol + col])
                col += 1
        row += 1

def import_ChildARTDist(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<ChildARTDist MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_ChildARTDistTag]

    row = modvarTagRow + 2
    for a in GBRange(0, 14):
        values = modvar[DP_Data][a]
        getRowOfYearVals(sheet, values, params, row)    
        row += 1

def import_EffectTreatChild(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<EffectTreatChild MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_EffectTreatChildTag]

    row = modvarTagRow + 2
    for eff in GBRange(DP_Cotrim, DP_ChildEffWithART):
        col = GB_RW_DataStartCol
        for t in GBRange(1, DP_MaxChildTreatmentYears):
            modvar[DP_Data][eff][t] = float(sheet.values[row, col])
            col += 1 
        row += 1

def import_ChildWeightBands(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<ChildWeightBands MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_ChildWeightBandsTag]

    row = modvarTagRow + 2
    for sex in GBRange(GB_Male, GB_Female):
        row += 1
        for a in GBRange(DP_A6Months, DP_A14):
            col = 0
            for b in GBRange(DP_Kgs_3_5pt9, DP_Kgs_35_Plus):
                modvar[DP_Data][sex][a][b] = float(sheet.values[row, GB_RW_DataStartCol + col])
                col += 1
            row += 1

def import_AdultAnnRateProgressLowerCD4(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<AdultAnnRateProgressLowerCD4 MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_AdultAnnRateProgressLowerCD4Tag]

    row = modvarTagRow + 3
    for sex in GBRange(GB_Male, GB_Female):
        col = 0
        for a in GBRange(DP_CD4_15_24, DP_CD4_45_54):
            for c in GBRange(DP_CD4_GT500, DP_CD4_LT50):
                modvar[DP_Data][sex][a][c] = float(sheet.values[row, GB_RW_DataStartCol + col])
                col += 1
        row += 1

def import_AdultDistNewInfectionsCD4(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<AdultDistNewInfectionsCD4 MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_AdultDistNewInfectionsCD4Tag]

    row = modvarTagRow + 3
    for sex in GBRange(GB_Male, GB_Female):
        col = 0
        for a in GBRange(DP_CD4_15_24, DP_CD4_45_54):
            for c in GBRange(DP_CD4_GT500, DP_CD4_LT50):
                modvar[DP_Data][sex][a][c] = float(sheet.values[row, GB_RW_DataStartCol + col])
                col += 1
        row += 1

def import_AdultMortByCD4NoART(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<AdultMortByCD4NoART MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_AdultMortByCD4NoARTTag]

    row = modvarTagRow + 3
    for sex in GBRange(GB_Male, GB_Female):
        col = 0
        for a in GBRange(DP_CD4_15_24, DP_CD4_45_54):
            for c in GBRange(DP_CD4_GT500, DP_CD4_LT50):
                modvar[DP_Data][sex][a][c] = float(sheet.values[row, GB_RW_DataStartCol + col])
                col += 1
        row += 1

def import_AdultInfectReduc(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<AdultInfectReduc MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_AdultInfectReducTag]

    row = modvarTagRow + 2 
    modvar[DP_Data] = float(sheet.values[row, GB_RW_DataStartCol])

def import_MortalityRates(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<MortalityRates MV2>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_MortalityRatesTag]

    row = modvarTagRow + 2
    for timePeriod in GBRange(DP_MortRates_LT12Mo, DP_MortRates_GT12Mo):
        values = modvar[DP_Data][timePeriod]
        getRowOfYearVals(sheet, values, params, row)    
        row += 1

def import_MortalityRatesMultiplier(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<MortalityRatesMultiplier MV>')
    if (modvarTagRow < 0): return
    # modvar = projection[AM_MortalityRatesMultiplierTag]

    row = modvarTagRow + 2
    projection[AM_MortalityRatesMultiplierTag] = float(sheet.values[row, GB_RW_DataStartCol])

def import_AdultMortByCD4WithART0to6(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<AdultMortByCD4WithART0to6 MV2>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_AdultMortByCD4WithART0to6Tag]

    row = modvarTagRow + 2
    for sex in GBRange(GB_Male, GB_Female):
        col = 0
        for a in GBRange(DP_CD4_15_24, DP_CD4_45_54):
            for c in GBRange(DP_CD4_GT500, DP_CD4_LT50):
                modvar[DP_Data][sex][a][c] = float(sheet.values[row, GB_RW_DataStartCol + col])
                col += 1
        row += 1

def import_AdultMortByCD4WithART7to12(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<AdultMortByCD4WithART7to12 MV2>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_AdultMortByCD4WithART7to12Tag]

    row = modvarTagRow + 2
    for sex in GBRange(GB_Male, GB_Female):
        col = 0
        for a in GBRange(DP_CD4_15_24, DP_CD4_45_54):
            for c in GBRange(DP_CD4_GT500, DP_CD4_LT50):
                modvar[DP_Data][sex][a][c] = float(sheet.values[row, GB_RW_DataStartCol + col])
                col += 1
        row += 1

def import_AdultMortByCD4WithARTGT12(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<AdultMortByCD4WithARTGt12 MV2>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_AdultMortByCD4WithARTGT12Tag]

    row = modvarTagRow + 2
    for sex in GBRange(GB_Male, GB_Female):
        col = 0
        for a in GBRange(DP_CD4_15_24, DP_CD4_45_54):
            for c in GBRange(DP_CD4_GT500, DP_CD4_LT50):
                modvar[DP_Data][sex][a][c] = float(sheet.values[row, GB_RW_DataStartCol + col])
                col += 1
        row += 1

def import_TFRRegion(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<TFRRegion MV>')
    if (modvarTagRow < 0): return
    # modvar = projection[AM_TFRRegionTag]

    row = modvarTagRow + 2
    if int(sheet.values[row, GB_RW_DataStartCol]) not in [0, DP_Custom]:
        projection[AM_TFRRegionTag] = int(sheet.values[row, GB_RW_DataStartCol])
            
def import_HIVTFRCustomFlag(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<HIVTFRCustomFlag MV>')
    if (modvarTagRow < 0): return
    # modvar = projection[AM_HIVTFRCustomFlagTag]
    
    row = modvarTagRow + 2
    projection[AM_HIVTFRCustomFlagTag] = bool(int(sheet.values[row, GB_RW_DataStartCol]))

def import_HIVTFR(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<HIVTFR MV4>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_HIVTFRTag]

    row = modvarTagRow + 2
    for a in GBRange(DP_A15_19, DP_A45_49):
        values = modvar[DP_Data][a]
        getRowOfYearVals(sheet, values, params, row)    
        row += 1

def import_TFRInputType(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<TFRInputType MV>')
    if (modvarTagRow < 0): return
    # modvar = projection[AM_TFRInputTypeTag]

    row = modvarTagRow + 2
    projection[AM_TFRInputTypeTag] = int(sheet.values[row, GB_RW_DataStartCol])
    
def import_FertCD4Discount(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<FertCD4Discount MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_FertCD4DiscountTag]

    row = modvarTagRow + 2
    for cd4 in GBRange(DP_CD4_GT500, DP_CD4_LT50):
        modvar[DP_Data][cd4] = float(sheet.values[row, GB_RW_DataStartCol + cd4 - 1])

def import_RatioWomenOnART(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<RatioWomenOnART MV2>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_RatioWomenOnARTTag]

    row = modvarTagRow + 2
    col = GB_RW_DataStartCol
    for a in GBRange(DP_A15_19, DP_A45_49):
        modvar[DP_Data][a] = float(sheet.values[row, col]) 
        col += 1

def import_FRRFitInput(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<FRRFitInput MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_FRRFitInputTag]

    row = modvarTagRow + 2
    for i in GBRange(DP_Number, DP_Percent):
        values = modvar[i]
        getRowOfYearVals(sheet, values, params, row)    
        row += 1

def import_FRRbyLocation(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<FRRbyLocation MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_FRRbyLocationTag]

    row = modvarTagRow + 2
    # modvar[DP_Data] = float(sheet.values[row, GB_RW_DataStartCol])
    modvar[DP_Data] = float(sheet.values[row, GB_RW_DataStartCol])

def import_TransEffAssump(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<TransEffAssump MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_TransEffAssumpTag]

    row = modvarTagRow + 2
    for regimen in GBRange(DP_NoProphExistInfCD4LT200, DP_ARTStartDurPreg_Late):
        for stage in GBRange(DP_Perinatal, DP_BreastfeedingGE350):
            modvar[DP_Data][regimen][stage] = float(sheet.values[row, GB_RW_DataStartCol + stage - 1])
        row += 1

def import_DALYDisabilityWeights(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<DALYDisabilityWeights MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_DALYDisabilityWeightsTag]

    row = modvarTagRow + 2
    for r in GBRange(DP_DALY_CD4CountGE200, DP_DALY_OnART):
        for c in GBRange(DP_Adult, DP_Child):
            modvar[r][c] = float(sheet.values[row, GB_RW_DataStartCol + c - 1])
        row += 1

def import_NewARTPatAlloc(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<NewARTPatAlloc MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_NewARTPatAllocTag]

    row = modvarTagRow + 2
    for i in GBRange(DP_AdvOpt_ART_ExpMort, DP_AdvOpt_ART_PropElig):
        modvar[i] = float(sheet.values[row, GB_RW_DataStartCol + i - DP_AdvOpt_ART_ExpMort])

def import_NewARTPatAllocationMethod(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<NewARTPatAllocationMethod MV2>')
    if (modvarTagRow < 0): return
    # modvar = projection[AM_NewARTPatAllocMethodTag]

    row = modvarTagRow + 2
    projection[AM_NewARTPatAllocMethodTag] = int(sheet.values[row, GB_RW_DataStartCol])

def import_RiskPopOrphans(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<RiskPopOrphans MV2>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_RiskPopOrphansTag]

    row = modvarTagRow + 2
    for c in GBRange(DP_PercAIDSDeaths, DP_PercMarried):
        col = GB_RW_DataStartCol
        for g in GBRange(DP_InjectingDrugUsers, DP_LowerRiskGenPop):
            modvar[g][c] = float(sheet.values[row, col])
            col += 1
        row += 1

def import_ECDCValues(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<ECDCValues MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_ECDCValuesTag]

    row = modvarTagRow + 2
    for i in GBRange(DP_Number, DP_UpperBound):
        values = modvar[i]
        getRowOfYearVals(sheet, values, params, row)    
        row += 1

def import_ECDCFQName(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<ECDCFQName MV>')
    if (modvarTagRow < 0): return
    # modvar = projection[AM_ECDCFQNameTag]

    row = modvarTagRow + 2
    projection[AM_ECDCFQNameTag] = str(sheet.values[row, GB_RW_DataStartCol])

def import_NosocomialInfectionsByAge(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<NosocomialInfectionsByAge MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_NosocomialInfectionsByAgeTag]

    row = modvarTagRow + 2
    for a in GBRange(DP_A0_4, DP_A10_14):
        values = modvar[a]
        getRowOfYearVals(sheet, values, params, row)    
        row += 1

def import_HIVMigrantsByAgeSex(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<HIVMigrantsByAgeSex MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_HIVMigrantsBySexAgeTag]

    row = modvarTagRow + 3
    for sex in GBRange(GB_Male, GB_Female):
        for a in GBRange(DP_A0_4, DP_MAX_AGE):
            values = modvar[sex][a]
            getRowOfYearVals(sheet, values, params, row)    
            row += 1

def import_IncidenceInput1970(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<IncidenceInput1970 MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_IncidenceInput1970Tag]

    row = modvarTagRow + 2
    values = modvar
    getRowOfYearVals(sheet, values, params, row)  

def import_CSAVRInputAIDSDeathsSource(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<CSAVRInputAIDSDeathsSource MV>')
    if (modvarTagRow < 0): return

    row = modvarTagRow + 2
    projection[AM_CSAVRInputAIDSDeathsSourceTag] = int(sheet.values[row, GB_RW_DataStartCol])

def import_CSAVRInputAIDSDeathsSourceName(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<CSAVRInputAIDSDeathsSourceName MV>')
    if (modvarTagRow < 0): return

    row = modvarTagRow + 2
    for i in GBRange(CSAVRSource1, CSAVRSource3):
        projection[AM_CSAVRInputAIDSDeathsSourceNameTag][i] = str(sheet.values[row, GB_RW_DataStartCol+i])

def import_CSAVRInputAIDSDeaths(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<CSAVRInputAIDSDeaths MV2>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_CSAVRInputAIDSDeathsTag]

    row = modvarTagRow + 2
    for i in GBRange(CSAVRSource1, CSAVRSource3):
        for j in GBRange(CSAVRNumReported, CSAVRNumNotReported):
            values = modvar[i][j]
            getRowOfYearVals(sheet, values, params, row)    
            row += 1

def import_CSAVRInputAIDSDeathsBySex(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<CSAVRInputAIDSDeathsBySex MV2>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_CSAVRInputAIDSDeathsBySexTag]

    row = modvarTagRow + 2
    for i in GBRange(CSAVRSource1, CSAVRSource3):
        for sex in GBRange(GB_Male, GB_Female):
            for j in GBRange(CSAVRNumReported, CSAVRNumNotReported):
                values = modvar[i][sex][j]
                getRowOfYearVals(sheet, values, params, row)    
                row += 1    

def import_CSAVRInputAIDSDeathsBySexAge(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<CSAVRInputAIDSDeathsBySexAge MV2>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_CSAVRInputAIDSDeathsBySexAgeTag]

    row = modvarTagRow + 2
    for i in GBRange(CSAVRSource1, CSAVRSource3):
        for sex in GBRange(GB_Male, GB_Female):
            for a in GBRange(DP_A15_19, DP_A50Plus):
                values = modvar[i][sex][a]
                getRowOfYearVals(sheet, values, params, row)    
                row += 1

def import_CSAVRInputNewDiagnoses(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<CSAVRInputNewDiagnoses MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_CSAVRInputNewDiagnosesTag]

    row = modvarTagRow + 2
    for i in GBRange(CSAVRNumReported, CSAVRNumNotReported):
        values = modvar[i]
        getRowOfYearVals(sheet, values, params, row)    
        row += 1

def import_CSAVRInputNewDiagnosesBySex(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<CSAVRInputNewDiagnosesBySex MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_CSAVRInputNewDiagnosesBySexTag]

    row = modvarTagRow + 2
    for sex in GBRange(GB_Male, GB_Female):
        for i in GBRange(CSAVRNumReported, CSAVRNumNotReported):
            values = modvar[sex][i]
            getRowOfYearVals(sheet, values, params, row)    
            row += 1    

def import_CSAVRInputNewDiagnosesBySexAge(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<CSAVRInputNewDiagnosesBySexAge MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_CSAVRInputNewDiagnosesBySexAgeTag]

    row = modvarTagRow + 2
    for sex in GBRange(GB_Male, GB_Female):
        for a in GBRange(DP_A15_19, DP_A50Plus):
            values = modvar[sex][a]
            getRowOfYearVals(sheet, values, params, row)    
            row += 1

def import_CSAVRInputNewDiagnosesBySexAgeCD4(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<CSAVRInputNewDiagnosesBySexAgeCD4 MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_CSAVRInputNewDiagnosesBySexAgeCD4Tag]

    row = modvarTagRow + 2
    for sex in GBRange(GB_Male, GB_Female):
        for a in GBRange(DP_A15_19, DP_A50Plus):
            for cd4 in GBRange(CSAVR_CD4_LT200, CSAVR_CD4_500Plus):
                values = modvar[sex][a][cd4]
                getRowOfYearVals(sheet, values, params, row)    
                row += 1

def import_CSAVRInputCD4DistAtDiag(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<CSAVRInputCD4DistAtDiag MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_CSAVRInputCD4DistAtDiagTag]

    row = modvarTagRow + 2
    for cd4 in GBRange(CSAVR_CD4_LT200, CSAVR_CD4_500Plus):
        values = modvar[cd4]
        getRowOfYearVals(sheet, values, params, row)    
        row += 1

def import_FitIncidencePopulationValue(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<FitIncidencePopulationValue_MV>')
    if (modvarTagRow < 0): return

    row = modvarTagRow + 2
    projection[AM_CSAVRPopulationValueTag] = int(sheet.values[row, GB_RW_DataStartCol])

def import_AIDSMortalityAllAges(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<AIDSMortalityAllAges MV2>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_AIDSMortalityAllAgesTag]

    row = modvarTagRow + 3
    for n in GBRange(DP_Median, DP_UnderCount):
        values = modvar[n]
        getRowOfYearVals(sheet, values, params, row)    
        row += 1

# dead on desktop (checked 2026-02-01)
def import_AnnualInterruptionRate(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<AnnualInterruptionRate MV>')
    if (modvarTagRow < 0): return

    row = modvarTagRow + 2
    projection[AM_AnnualInterruptionRateTag] = float(sheet.values[row, GB_RW_DataStartCol])

def import_IncreasedLikelihoodOfReinit(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<IncreasedLikelihoodOfReinit MV>')
    if (modvarTagRow < 0): return

    row = modvarTagRow + 2
    projection[AM_IncreasedLikelihoodOfReinitTag] = float(sheet.values[row, GB_RW_DataStartCol])

def import_OffARTMortRateMultiplier(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<OffARTMortRateMultiplier MV>')
    if (modvarTagRow < 0): return

    row = modvarTagRow + 2
    projection[AM_OffARTMortRateMultiplierTag] = float(sheet.values[row, GB_RW_DataStartCol])

# dead on desktop (checked 2026-02-01)
def import_ChildAnnualInterruptionRate(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<ChildAnnualInterruptionRate MV>')
    if (modvarTagRow < 0): return

    row = modvarTagRow + 2
    projection[AM_ChildAnnualInterruptionRateTag] = float(sheet.values[row, GB_RW_DataStartCol])

def import_ChildIncreasedLikelihoodOfReinit(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<ChildIncreasedLikelihoodOfReinit MV>')
    if (modvarTagRow < 0): return

    row = modvarTagRow + 2
    projection[AM_ChildIncreasedLikelihoodOfReinitTag] = float(sheet.values[row, GB_RW_DataStartCol])

def import_ChildOffARTMortRateMultiplier(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<ChildOffARTMortRateMultiplier MV>')
    if (modvarTagRow < 0): return

    row = modvarTagRow + 2
    projection[AM_ChildOffARTMortRateMultiplierTag] = float(sheet.values[row, GB_RW_DataStartCol])

def import_CSAVRFitOptions(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<CSAVRFitOptions MV3>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_CSAVRFitOptionsTag]

    row = modvarTagRow + 2
    for i in GBRange(DP_PLHIV, DP_CD4DistAtDiag):
        modvar[i] = bool(int(sheet.values[row, GB_RW_DataStartCol + i]))

def import_FitIncidenceParameters(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<FitIncidenceParameters MV7>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_CSAVRParametersTag]

    row = modvarTagRow + 3

    for fit in GBRange(DP_DoubleLogistic, DP_CSAVRMaxFit):
        col = GB_RW_DataStartCol
        count = int(sheet.values[row, col])                                  #count in the file
        row += 1
        for i in GBRange(1, count):
            for j, value in modvar[str(fit)].items():
                if modvar[str(fit)][j]['mstID'] == int(sheet.values[row, col]): #mstID
                    modvar[str(fit)][j]['value'] = float(sheet.values[row + 1, col])   #value
            col += 1
        row += 2

def import_FitIncidenceIncScaleParameters(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<FitIncidenceIncScaleParameters MV2>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_CSAVRIncScaleParametersTag]

    row = modvarTagRow + 3

    for fit in GBRange(DP_DoubleLogistic, DP_CSAVRMaxFit):
        col = GB_RW_DataStartCol
        count = int(sheet.values[row, col])                                   #count in the file
        row += 1
        for i in GBRange(1, count):
            for j, value in modvar[str(fit)].items():
                if modvar[str(fit)][j]['mstID'] == int(sheet.values[row, col]): #mstID
                    modvar[str(fit)][j]['value'] = float(sheet.values[row + 1, col])   #value
            col += 1
        row += 2

def import_FitIncidenceUncertaintyParams(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<FitIncidenceUncertaintyParams MV3>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_CSAVRUncertaintyParamsTag]

    row = modvarTagRow + 3
    for fit in GBRange(DP_DoubleLogistic, DP_rLogistic):
        for i in GBRange(CSAVR_Unc_BurnIn, CSAVR_Unc_NumSamples):
            if not (i == CSAVR_Unc_BurnIn):
                modvar[fit][i] = float(sheet.values[row, GB_RW_DataStartCol + i])
        row += 1
    
def import_CSAVRConstrainPLHIVGTNumART(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<CSAVRConstrainPLHIVGTNumART MV3>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_CSAVRConstrainPLHIVGTNumARTTag]

    row = modvarTagRow + 2
    for fit in GBRange(DP_DoubleLogistic, DP_CSAVRMaxFit):
        modvar[fit] = bool(int(sheet.values[row, GB_RW_DataStartCol + fit]))

def import_FitIncidenceTypeOfFit(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<FitIncidenceTypeOfFit MV2>')
    if (modvarTagRow < 0): return

    row = modvarTagRow + 2
    projection[AM_CSAVRTypeOfFitTag] = int(sheet.values[row, GB_RW_DataStartCol])

def import_CSAVRAdjustIRRs(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<CSAVRAdjustIRRs MV4>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_CSAVRAdjustIRRsTag]

    row = modvarTagRow + 2
    for fitType in GBRange(DP_DoubleLogistic, DP_CSAVRMaxFit):
        values = modvar[fitType]
        values[DP_CSAVR_SexRatio] = bool(int(sheet.values[row, GB_RW_DataStartCol]))
        values[DP_CSAVR_DistOfHIV] = bool(int(sheet.values[row, GB_RW_DataStartCol + 1]))
        row += 1

# def import_FitIncidenceFitMethod(sheet, params, projection):
#     modvarTagRow = findTagRow(sheet, '<FitIncidenceFitMethod MV2>')
#     if (modvarTagRow < 0): return
#     modvar = projection[AM_CSAVRFitMethodTag]

#     row = modvarTagRow + 2
#     for fitType in GBRange(DP_DoubleLogistic, DP_CSAVRMaxFit):
#         modvar[fitType] = int(sheet.values[row, GB_RW_DataStartCol + fitType])

def import_CSAVRMetaData(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<CSAVRMetaData MV2>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_CSAVRMetaDataTag]

    row = modvarTagRow + 2
    for fitType in GBRange(DP_DoubleLogistic, DP_CSAVRMaxFit):
        modvar[fitType]['AIC'] = float(sheet.values[row, GB_RW_DataStartCol])
        modvar[fitType]['isFitted'] =  bool(int(sheet.values[row, GB_RW_DataStartCol + 1]))
        if float(sheet.values[row, GB_RW_DataStartCol + 2]) > 0:
            modvar[fitType]['date'] = datetime.strftime(dateTime_fromDelphi(float(sheet.values[row, GB_RW_DataStartCol + 2])), GB_DateTime_Format)
        else:
            modvar[fitType]['date'] = float(sheet.values[row, GB_RW_DataStartCol + 2])
        row += 1

def import_MeanCD4atDiagnosis(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<MeanCD4atDiagnosis MV5>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_CSAVRMeanCD4atDiagnosisTag]

    row = modvarTagRow + 2
    for fitType in GBRange(DP_DoubleLogistic, DP_CSAVRMaxFit):
        for sex in GBRange(GB_BothSexes, GB_Female):
            for dataType in GBRange(DP_Number, DP_UpperBound):
                values = modvar[fitType][sex][dataType]
                getRowOfYearVals(sheet, values, params, row)      
                row += 1  

def import_MeanCD4atDiagnosisByAgeSex(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<MeanCD4atDiagnosisByAgeSex MV2>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_CSAVRMeanCD4atDiagnosisByAgeSexTag]

    row = modvarTagRow + 2
    for fitType in GBRange(DP_DoubleLogistic, DP_CSAVRMaxFit):
        for sex in GBRange(GB_BothSexes, GB_Female):
            for age in GBRange(DP_AllAges, DP_A50Plus):
                for dataType in GBRange(DP_Number, DP_UpperBound):
                    values = modvar[fitType][sex][age][dataType]
                    getRowOfYearVals(sheet, values, params, row)      
                    row += 1  

def import_TimeInfToDiag(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<TimeInfToDiag MV5>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_CSAVRTimeInfToDiagTag]

    row = modvarTagRow + 2
    for fitType in GBRange(DP_DoubleLogistic, DP_CSAVRMaxFit):
        for sex in GBRange(GB_BothSexes, GB_Female):
            for dataType in GBRange(DP_Number, DP_UpperBound):
                values = modvar[fitType][sex][dataType]
                getRowOfYearVals(sheet, values, params, row)      
                row += 1  

def import_PropOfDiagnosed(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<PropOfDiagnosed MV5>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_CSAVRPropOfDiagnosedTag]

    row = modvarTagRow + 2
    for fitType in GBRange(DP_DoubleLogistic, DP_CSAVRMaxFit):
        for sex in GBRange(GB_BothSexes, GB_Female):
            for dataType in GBRange(DP_Number, DP_UpperBound):
                values = modvar[fitType][sex][dataType]
                getRowOfYearVals(sheet, values, params, row)      
                row += 1  

def import_PropOfDiagnosedNoART(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<PropOfDiagnosedNoART MV2>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_CSAVRPropOfDiagnosedNoARTTag]

    row = modvarTagRow + 2
    for fitType in GBRange(DP_DoubleLogistic, DP_CSAVRMaxFit):
        for sex in GBRange(GB_BothSexes, GB_Female):
            for dataType in GBRange(DP_Number, DP_UpperBound):
                values = modvar[fitType][sex][dataType]
                getRowOfYearVals(sheet, values, params, row)      
                row += 1  

def import_PropofDiagnosedByAgeSexCD4(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<PropOfDiagnosedByAgeSexCD4 MV2>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_CSAVRPropOfDiagnosedByAgeSexCD4Tag]

    row = modvarTagRow + 2
    for fitType in GBRange(DP_DoubleLogistic, DP_CSAVRMaxFit):
        for sex in GBRange(GB_BothSexes, GB_Female):
            for age in GBRange(DP_AllAges, DP_A50Plus):
                for cd4 in GBRange(CSAVR_CD4_LT200, CSAVR_CD4_All):
                    for dataType in GBRange(DP_Number, DP_UpperBound):
                        values = modvar[fitType][sex][age][cd4][dataType]
                        getRowOfYearVals(sheet, values, params, row)      
                        row += 1  

def import_CSAVRNumPLHIV(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<CSAVRNumPLHIV MV3>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_CSAVRNumPLHIVTag]

    row = modvarTagRow + 2
    for fitType in GBRange(DP_DoubleLogistic, DP_CSAVRMaxFit):
        for sex in GBRange(GB_BothSexes, GB_Female):
            for dataType in GBRange(DP_Number, DP_UpperBound):
                values = modvar[fitType][sex][dataType]
                getRowOfYearVals(sheet, values, params, row)      
                row += 1  

def import_CSAVRNumPLHIVByAgeSexCD4(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<CSAVRNumPLHIVByAgeSexCD4 MV2>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_CSAVRNumPLHIVByAgeSexCD4Tag]

    row = modvarTagRow + 2
    for fitType in GBRange(DP_DoubleLogistic, DP_CSAVRMaxFit):
        for sex in GBRange(GB_BothSexes, GB_Female):
            for age in GBRange(DP_AllAges, DP_A50Plus):
                for cd4 in GBRange(CSAVR_CD4_LT200, CSAVR_CD4_All):
                    for dataType in GBRange(DP_Number, DP_UpperBound):
                        values = modvar[fitType][sex][age][cd4][dataType]
                        getRowOfYearVals(sheet, values, params, row)      
                        row += 1  

def import_CSAVRNumDiagnosed(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<CSAVRNumDiagnosed MV3>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_CSAVRNumDiagnosedTag]

    row = modvarTagRow + 2
    for fitType in GBRange(DP_DoubleLogistic, DP_CSAVRMaxFit):
        for sex in GBRange(GB_BothSexes, GB_Female):
            for dataType in GBRange(DP_Number, DP_UpperBound):
                values = modvar[fitType][sex][dataType]
                getRowOfYearVals(sheet, values, params, row)      
                row += 1  

def import_CSAVRNumDiagnosedByAgeSexCD4(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<CSAVRNumDiagnosedByAgeSexCD4 MV2>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_CSAVRNumDiagnosedByAgeSexCD4Tag]

    row = modvarTagRow + 2
    for fitType in GBRange(DP_DoubleLogistic, DP_CSAVRMaxFit):
        for sex in GBRange(GB_BothSexes, GB_Female):
            for age in GBRange(DP_AllAges, DP_A50Plus):
                for cd4 in GBRange(CSAVR_CD4_LT200, CSAVR_CD4_All):
                    for dataType in GBRange(DP_Number, DP_UpperBound):
                        values = modvar[fitType][sex][age][cd4][dataType]
                        getRowOfYearVals(sheet, values, params, row)      
                        row += 1    

def import_CSAVRAIDSDeaths(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<CSAVRAIDSDeaths MV3>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_CSAVRAIDSDeathsTag]

    row = modvarTagRow + 2
    for fitType in GBRange(DP_DoubleLogistic, DP_CSAVRMaxFit):
        for sex in GBRange(GB_BothSexes, GB_Female):
            for dataType in GBRange(DP_Number, DP_UpperBound):
                values = modvar[fitType][sex][dataType]
                getRowOfYearVals(sheet, values, params, row)      
                row += 1  

def import_CSAVRAIDSDeathsByAgeSex(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<CSAVRAIDSDeathsByAgeSex MV2>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_CSAVRAIDSDeathsByAgeSexTag]

    row = modvarTagRow + 2
    for fitType in GBRange(DP_DoubleLogistic, DP_CSAVRMaxFit):
        for sex in GBRange(GB_BothSexes, GB_Female):
            for age in GBRange(DP_AllAges, DP_A50Plus):
                for dataType in GBRange(DP_Number, DP_UpperBound):
                    values = modvar[fitType][sex][age][dataType]
                    getRowOfYearVals(sheet, values, params, row)      
                    row += 1 

def import_CSAVRNumNewInfections(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<CSAVRNumNewInfections MV3>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_CSAVRNumNewInfectionsTag]

    row = modvarTagRow + 2
    for fitType in GBRange(DP_DoubleLogistic, DP_CSAVRMaxFit):
        for sex in GBRange(GB_BothSexes, GB_Female):
            for dataType in GBRange(DP_Number, DP_UpperBound):
                values = modvar[fitType][sex][dataType]
                getRowOfYearVals(sheet, values, params, row)      
                row += 1   

def import_CSAVRIncidenceByFit(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<CSAVRIncidenceByFit MV2>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_CSAVRIncidenceByFitTag]

    row = modvarTagRow + 2
    for fitType in GBRange(DP_DoubleLogistic, DP_CSAVRMaxFit):
        row += 1   
        values = modvar[fitType]
        getRowOfYearVals(sheet, values, params, row)      
                
def import_HIVSexRatio(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<HIVSexRatio MV>')
    if (modvarTagRow < 0): return
    getRowOfYearVals(sheet, projection[AM_HIVSexRatioTag], params, modvarTagRow + 3)
                
def import_CSAVRHIVSexRatio(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<CSAVRHIVSexRatio MV3')
    if (modvarTagRow < 0): return
    modvar = projection[AM_CSAVRHIVSexRatioTag]

    row = modvarTagRow + 3
    for fitType in GBRange(DP_DoubleLogistic, DP_CSAVRMaxFit):
        values = modvar[fitType]
        getRowOfYearVals(sheet, values, params, row)     
        row += 1
                
# def import_HIVSexRatioFittingValues(sheet, params, projection):
#     modvarTagRow = findTagRow(sheet, '<HIVSexRatioFittingValues MV>')
#     if (modvarTagRow < 0): return
#     modvar = projection[AM_HIVSexRatioFittingValuesTag]

#     row = modvarTagRow + 3
#     for i in GBRange(DP_SAP_FixedIROverTime, DP_SAP_TimeDependentIR):
#         values = modvar[i]
#         getRowOfYearVals(sheet, values, params, row)     
#         row += 1   
                
# def import_ARTTreatFitHIVSexRatio(sheet, params, projection):
#     modvarTagRow = findTagRow(sheet, '<ARTTreatFitHIVSexRatio MV>')
#     if (modvarTagRow < 0): return
#     modvar = projection[AM_ARTTreatFitHIVSexRatioTag]

#     row = modvarTagRow + 3
#     values = modvar
#     getRowOfYearVals(sheet, values, params, row)

def import_SAPFittingValues(sheet, params, projection):

    projection[AM_CustomSAPDataTag] = []

    # CSAVR
    distOfHIVRow = findTagRow(sheet, '<CSAVRDistOfHIV MV2>')
    typeOfFitRow = findTagRow(sheet, '<FitIncidenceTypeOfFit MV2>')
    CSAVRSexRatioRow = findTagRow(sheet, '<CSAVRHIVSexRatio MV3')
    CSAVRMetaRow = findTagRow(sheet, '<CSAVRMetaData MV2>')

    typeOfFit = int(sheet.values[typeOfFitRow + 2, GB_RW_DataStartCol])
    csavr_sex_ratio = []
    
    csavr_sex_ratio = projection[AM_CSAVRHIVSexRatioTag].copy()

    row = CSAVRSexRatioRow + 3
    for fitType in GBRange(DP_DoubleLogistic, DP_CSAVRMaxFit):
        getRowOfYearVals(sheet, csavr_sex_ratio[fitType], params, row)     
        row += 1
                
    
    csavr_dist_of_hiv = projection[AM_CSAVRDistOfHIVTag].copy()

    row = distOfHIVRow + 3
   
    for fitType in GBRange(DP_DoubleLogistic, DP_CSAVRMaxFit): 
        for sex in GBRange(GB_Male, GB_Female):
            for age in GBRange(DP_A0_4, DP_MAX_AGE):
                getRowOfYearVals(sheet, csavr_dist_of_hiv[fitType][sex][age], params, row)    
                row += 1             
        row += 1
    
    csavr_meta = projection[AM_CSAVRMetaDataTag].copy()

    row = CSAVRMetaRow + 2
    for fitType in GBRange(DP_DoubleLogistic, DP_CSAVRMaxFit):
        csavr_meta[fitType]['AIC'] = float(sheet.values[row, GB_RW_DataStartCol])
        csavr_meta[fitType]['isFitted'] =  bool(int(sheet.values[row, GB_RW_DataStartCol + 1]))
        if float(sheet.values[row, GB_RW_DataStartCol + 2]) > 0:
            csavr_meta[fitType]['date'] = datetime.strftime(dateTime_fromDelphi(float(sheet.values[row, GB_RW_DataStartCol + 2])), GB_DateTime_Format)
        else:
            csavr_meta[fitType]['date'] = float(sheet.values[row, GB_RW_DataStartCol + 2])
        row += 1
    
    dataDict = getCustomSAPDataDict(getYearIdx(params.finalYear, params.firstYear) + 1)
    dataDict['id'] =  DP_PatternFromCSAVR_Index
    dataDict['dataSource'] = DP_PatternFromCSAVR_Index
    dataDict['name'] = "Pattern from CSAVR"
    dataDict['HIVSexRatio'] = csavr_sex_ratio[typeOfFit]
    dataDict['DistOfHIV'] = csavr_dist_of_hiv[typeOfFit]
    dataDict['AIC'] = csavr_meta[typeOfFit]['AIC']

    projection[AM_CustomSAPDataTag].append(dataDict)



    # HIV Prev
    fittingTagRow = findTagRow(sheet, '<FittingAICData MV>')
    distOfHIVTagRow = findTagRow(sheet, '<IRRFittingValues MV>')
    sexRatioTagRow = findTagRow(sheet, '<HIVSexRatioFittingValues MV>')


    if (fittingTagRow >= 0):
        fittingRow = fittingTagRow + 2

        sexRatioTagFound = sexRatioTagRow > 0
        sexRatioRow = sexRatioTagRow + 3

        distOfHIVTagFound = distOfHIVTagRow > 0
        distOfHIVRow = distOfHIVTagRow + 3
        
        for prevModel in GBRange(DP_SAP_FixedIROverTime, DP_SAP_TimeDependentIR):
            isFitted = bool(int(sheet.values[fittingRow, GB_RW_DataStartCol + 1]))

            if isFitted:
                dataDict = getCustomSAPDataDict(getYearIdx(params.finalYear, params.firstYear) + 1)
                dataDict['name'] = 'HIV prevalence by age'
                if prevModel == DP_SAP_FixedIROverTime:
                    dataDict['name'] += ': Fixed incidence ratios over time'
                else:
                    dataDict['name'] += ': Time dependent incidence ratios'
                dataDict['fitType'] = DP_SAP_HIVPrevByAge
                dataDict['HIVPrevModel'] = prevModel
                dataDict['AIC'] = float(sheet.values[fittingRow, GB_RW_DataStartCol])
                
                HIVSexRatio = np.zeros(getYearIdx(params.finalYear, params.firstYear) + 1).tolist()
                if sexRatioTagFound:
                    getRowOfYearVals(sheet, HIVSexRatio, params, sexRatioRow)       
                dataDict['HIVSexRatio'] = HIVSexRatio

                DistOfHIV = np.zeros((GB_Female + 1, DP_MAX_AGE + 1, getYearIdx(params.finalYear, params.firstYear) + 1))
                if distOfHIVTagFound:
                    for sex in GBRange(GB_Male, GB_Female):
                        for age in GBRange(DP_A0_4, DP_MAX_AGE):
                            values = DistOfHIV[sex][age]
                            getRowOfYearVals(sheet, values, params, distOfHIVRow)    
                            distOfHIVRow += 1
                dataDict['DistOfHIV'] = DistOfHIV.tolist()
                if prevModel == DP_SAP_FixedIROverTime:
                    dataDict['dataSource'] = DP_HIVPrevFixed_Index 
                else:
                    dataDict['dataSource'] = DP_HIVPrevTime_Index
                projection[AM_CustomSAPDataTag].append(dataDict)
            
            fittingRow += 1
            sexRatioRow += 1 
            distOfHIVRow += 1
            
    # ART
    fittingTagRow = findTagRow(sheet, '<ARTTreatFittingData MV>')
    distOfHIVTagRow = findTagRow(sheet, '<ARTTreatFit MV>')
    sexRatioTagRow = findTagRow(sheet, '<ARTTreatFitHIVSexRatio MV>')

    if (fittingTagRow >= 0):
        fittingRow = fittingTagRow + 2

        sexRatioTagFound = sexRatioTagRow > 0
        sexRatioRow = sexRatioTagRow + 3

        distOfHIVTagFound = distOfHIVTagRow > 0
        distOfHIVRow = distOfHIVTagRow + 3

        isFitted = bool(int(sheet.values[fittingRow, GB_RW_DataStartCol + 1]))

        if isFitted:
            dataDict = getCustomSAPDataDict(getYearIdx(params.finalYear, params.firstYear) + 1)
            dataDict['name'] = 'ART by age'
            dataDict['fitType'] = DP_SAP_ARTByAge
            dataDict['HIVPrevModel'] = 'N/A'
            dataDict['AIC'] = float(sheet.values[fittingRow, GB_RW_DataStartCol])
                
            HIVSexRatio = np.zeros(getYearIdx(params.finalYear, params.firstYear) + 1).tolist()
            if sexRatioTagFound:
                getRowOfYearVals(sheet, HIVSexRatio, params, sexRatioRow)       
            dataDict['HIVSexRatio'] = HIVSexRatio

            DistOfHIV = np.zeros((GB_Female + 1, DP_MAX_AGE + 1, getYearIdx(params.finalYear, params.firstYear) + 1))
            if distOfHIVTagFound:
                for sex in GBRange(GB_Male, GB_Female):
                    for age in GBRange(DP_A0_4, DP_MAX_AGE):
                        values = DistOfHIV[sex][age]
                        getRowOfYearVals(sheet, values, params, distOfHIVRow)    
                        distOfHIVRow += 1
            dataDict['DistOfHIV'] = DistOfHIV.tolist()
            dataDict['dataSource'] = DP_FittedToART_Index
            projection[AM_CustomSAPDataTag].append(dataDict)
            
    # index things
    SAPFitTypeTagRow = findTagRow(sheet, '<SAPFitType MV>')
    HIVPrevModelTagRow = findTagRow(sheet, '<HIVPrevModel MV>')
    if (SAPFitTypeTagRow >= 0) and (HIVPrevModelTagRow >= 0):
        SAPFitTypeRow = SAPFitTypeTagRow + 2
        HIVPrevModelRow = HIVPrevModelTagRow + 2
        SAPFitType = int(sheet.values[SAPFitTypeRow, GB_RW_DataStartCol])
        HIVPrevModel = int(sheet.values[HIVPrevModelRow, GB_RW_DataStartCol])

        for i, dataDict in enumerate(projection[AM_CustomSAPDataTag]):    
            if dataDict['fitType'] == SAPFitType:
                if (SAPFitType == DP_SAP_HIVPrevByAge):
                    if (dataDict['HIVPrevModel'] == HIVPrevModel):
                        projection[AM_CustomSAPDataIndexTag] = i
                else:
                    projection[AM_CustomSAPDataIndexTag] = i
    pass

    # if len(projection[AM_CustomSAPDataTag]) == 0:
    #     dataDict = getCustomSAPDataDict(getYearIdx(params.finalYear, params.firstYear) + 1)
    #     projection[AM_CustomSAPDataTag].append(dataDict)


# def import_FittingAICData(sheet, params, projection):
#     modvarTagRow = findTagRow(sheet, '<FittingAICData MV>')
#     if (modvarTagRow < 0): return
#     modvar = projection[AM_FittingDataTag]

#     row = modvarTagRow + 2
#     for i in GBRange(DP_SAP_FixedIROverTime, DP_SAP_TimeDependentIR):
#         modvar[i]['AIC'] = float(sheet.values[row, GB_RW_DataStartCol])
#         modvar[i]['isFitted'] = bool(int(sheet.values[row, GB_RW_DataStartCol + 1]))
#         row += 1

# def import_ARTTreatFittingData(sheet, params, projection):
#     modvarTagRow = findTagRow(sheet, '<ARTTreatFittingData MV>')
#     if (modvarTagRow < 0): return
#     modvar = projection[AM_ARTTreatFittingDataTag]

#     row = modvarTagRow + 2
#     modvar['AIC'] = float(sheet.values[row, GB_RW_DataStartCol])
#     modvar['isFitted'] = bool(int(sheet.values[row, GB_RW_DataStartCol + 1]))

def import_DistOfHIV(sheet, params, projection):    
    modvarTagRow = findTagRow(sheet, '<DistOfHIV MV2>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_DistOfHIVTag]

    row = modvarTagRow + 3
    
    for sex in GBRange(GB_Male, GB_Female):
        for age in GBRange(DP_A0_4, DP_MAX_AGE):
            values = modvar[sex][age]
            getRowOfYearVals(sheet, values, params, row)    
            row += 1
    pass

def import_CSAVRDistOfHIV(sheet, params, projection):    
    modvarTagRow = findTagRow(sheet, '<CSAVRDistOfHIV MV2>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_CSAVRDistOfHIVTag]

    row = modvarTagRow + 3
   
    for fitType in GBRange(DP_DoubleLogistic, DP_CSAVRMaxFit): 
        for sex in GBRange(GB_Male, GB_Female):
            for age in GBRange(DP_A0_4, DP_MAX_AGE):
                values = modvar[fitType][sex][age]
                getRowOfYearVals(sheet, values, params, row)    
                row += 1             
        row += 1

# def import_IRRFittingValues(sheet, params, projection):    
#     modvarTagRow = findTagRow(sheet, '<IRRFittingValues MV>')
#     if (modvarTagRow < 0): return
#     modvar = projection[AM_IRRFittingValuesTag]

#     row = modvarTagRow + 3
    
#     for i in GBRange(DP_SAP_FixedIROverTime, DP_SAP_TimeDependentIR):
#         for sex in GBRange(GB_Male, GB_Female):
#             for age in GBRange(DP_A0_4, DP_MAX_AGE):
#                 values = modvar[i][sex][age]
#                 getRowOfYearVals(sheet, values, params, row)    
#                 row += 1
#         row += 1

# def import_ARTTreatFitDistOfHIV(sheet, params, projection):    
#     modvarTagRow = findTagRow(sheet, '<ARTTreatFit MV>')
#     if (modvarTagRow < 0): return
#     modvar = projection[AM_ARTTreatFitDistOfHIVTag]

#     row = modvarTagRow + 3
    
#     for sex in GBRange(GB_Male, GB_Female):
#         for age in GBRange(DP_A0_4, DP_MAX_AGE):
#             values = modvar[sex][age]
#             getRowOfYearVals(sheet, values, params, row)    
#             row += 1

def import_AIDS45q15(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<AIDS45q15 MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_AIDS45q15Tag]

    row = modvarTagRow + 2
    values = modvar
    getRowOfYearVals(sheet, values, params, row)

def import_NonAIDS45q15(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<NonAIDS45q15 MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_NonAIDS45q15Tag]

    row = modvarTagRow + 2
    values = modvar
    getRowOfYearVals(sheet, values, params, row)

def import_Total45q15(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<Total45q15 MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_Total45q15Tag]

    row = modvarTagRow + 2
    values = modvar
    getRowOfYearVals(sheet, values, params, row)

def import_Under5MortRate(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<Under5MortRate MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_Under5MortRateTag]

    row = modvarTagRow + 2
    values = modvar
    getRowOfYearVals(sheet, values, params, row)

def import_PMTCTProgEstNeed(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<PMTCTProgEstNeed MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_PMTCTProgEstNeedTag]

    row = modvarTagRow + 2
    values = modvar
    getRowOfYearVals(sheet, values, params, row)

def import_NumberOnART(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<NumberOnART MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_NumberOnARTTag]

    row = modvarTagRow + 2
    values = modvar
    getRowOfYearVals(sheet, values, params, row)

def import_ARTCovByAge(sheet, params, projection):    
    modvarTagRow = findTagRow(sheet, '<ARTCovByAge MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_ARTCovByAgeTag]

    row = modvarTagRow + 3
    
    for sex in GBRange(GB_BothSexes, GB_Female):
        for age in GBRange(DP_A0_4, DP_MAX_AGE):
            values = modvar[sex][age]
            getRowOfYearVals(sheet, values, params, row)    
            row += 1

def import_KeyPops(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<KeyPops MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_KeyPopsTag]
    
    row = modvarTagRow + 2
    for ind in GBRange(DP_KP_PSE, DP_KP_NewInfs):
        for pop in GBRange(DP_KP_FSW, DP_KP_TG):
            modvar['data'][ind][pop] = float(sheet.values[row, GB_RW_DataStartCol + pop])
        row += 1

def import_KeyPopsYear(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<KeyPopsYear MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_KeyPopsTag]

    row = modvarTagRow + 2
    modvar['year'] = int(sheet.values[row, GB_RW_DataStartCol])

def import_KeyPopsFName(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<KeyPopsFName MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_KeyPopsTag]

    row = modvarTagRow + 2
    modvar['fName'] = str(sheet.values[row, GB_RW_DataStartCol])

def import_PregWomenPrevRoutineTest(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<PregWomenPrevRoutineTest MV>')
    if (modvarTagRow < 0): return
    # modvar = projection[AM_PregWomenPrevRoutineTestTag]

    row = modvarTagRow + 2
    projection[AM_PregWomenPrevRoutineTestTag] = float(sheet.values[row, GB_RW_DataStartCol])

def import_PregWomenPrev(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<PregWomenPrev MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_PregWomenPrevTag]

    row = modvarTagRow + 2
    values = modvar
    getRowOfYearVals(sheet, values, params, row)

def import_PrevSurveyData(sheet, params, projection):    
    modvarTagRow = findTagRow(sheet, '<PrevSurveyData MV5>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_PrevSurveyTag]

    row = modvarTagRow + 4
    
    for survey in GBRange(DP_PrevSurvey1, DP_PrevSurvey8):
        for sex in GBRange(GB_BothSexes, GB_Female):
            for age in GBRange(DP_A2_4, DP_MAX_AGE):
                for dt in GBRange(DP_Number, DP_WeightedSampleSize):
                    modvar[survey]['data'][sex][dt][age] = float(sheet.values[row, GB_RW_DataStartCol + dt])
                row += 1
        row += 1

def import_PrevSurveyUsed(sheet, params, projection):    
    modvarTagRow = findTagRow(sheet, '<PrevSurveyUsed MV3>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_PrevSurveyTag]

    row = modvarTagRow + 2
    
    for survey in GBRange(DP_PrevSurvey1, DP_PrevSurvey8):
        modvar[survey]['used'] = bool(int(sheet.values[row, GB_RW_DataStartCol + survey - 1]))

def import_PrevSurveyName(sheet, params, projection):    
    modvarTagRow = findTagRow(sheet, '<PrevSurveyName MV3>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_PrevSurveyTag]

    row = modvarTagRow + 2
    
    for survey in GBRange(DP_PrevSurvey1, DP_PrevSurvey8):
        modvar[survey]['name'] = str(sheet.values[row, GB_RW_DataStartCol + survey - 1])

def import_PrevSurveyYear(sheet, params, projection):    
    modvarTagRow = findTagRow(sheet, '<PrevSurveyYear MV3>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_PrevSurveyTag]

    row = modvarTagRow + 2
    
    for survey in GBRange(DP_PrevSurvey1, DP_PrevSurvey8):
        modvar[survey]['year'] = int(sheet.values[row, GB_RW_DataStartCol + survey - 1])

def import_ARTCovSurveyData(sheet, params, projection):    
    modvarTagRow = findTagRow(sheet, '<ARTCovSurveyData MV2>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_ARTCovSurveyTag]

    row = modvarTagRow + 4
    
    for survey in GBRange(DP_PrevSurvey1, DP_PrevSurvey8):
        for sex in GBRange(GB_BothSexes, GB_Female):
            for age in GBRange(DP_A0_4, DP_Val_A50Plus):
                for dt in GBRange(DP_Number, DP_WeightedSampleSize):
                    modvar[survey]['data'][sex][dt][age] = float(sheet.values[row, GB_RW_DataStartCol + dt])
                row += 1
        row += 1

def import_ARTCovSurveyUsed(sheet, params, projection):    
    modvarTagRow = findTagRow(sheet, '<ARTCovSurveyUsed MV2>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_ARTCovSurveyTag]

    row = modvarTagRow + 2
    
    for survey in GBRange(DP_PrevSurvey1, DP_PrevSurvey8):
        modvar[survey]['used'] = bool(int(sheet.values[row, GB_RW_DataStartCol + survey - 1]))

def import_ARTCovSurveyName(sheet, params, projection):    
    modvarTagRow = findTagRow(sheet, '<ARTCovSurveyName MV2>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_ARTCovSurveyTag]

    row = modvarTagRow + 2
    
    for survey in GBRange(DP_PrevSurvey1, DP_PrevSurvey8):
        modvar[survey]['name'] = str(sheet.values[row, GB_RW_DataStartCol + survey - 1])

def import_ARTCovSurveyYear(sheet, params, projection):    
    modvarTagRow = findTagRow(sheet, '<ARTCovSurveyYear MV2>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_ARTCovSurveyTag]

    row = modvarTagRow + 2
    
    for survey in GBRange(DP_PrevSurvey1, DP_PrevSurvey8):
        modvar[survey]['year'] = int(sheet.values[row, GB_RW_DataStartCol + survey - 1])

def import_MortRateByAge(sheet, params, projection):    
    modvarTagRow = findTagRow(sheet, '<MortRateByAge MV2>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_MortRateByAgeTag]

    row = modvarTagRow + 3
    
    for sex in GBRange(GB_Male, GB_Female):
        for age in GBRange(DP_A0_4, DP_MAX_AGE):
            values = modvar[sex][age]
            getRowOfYearVals(sheet, values, params, row)    
            row += 1

def import_AllCauseMortality(sheet, params, projection):    
    modvarTagRow = findTagRow(sheet, '<AllCauseMortality MV2>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_AllCauseMortalityTag]

    row = modvarTagRow + 3
    
    for sex in GBRange(GB_Male, GB_Female):
        for age in GBRange(DP_A0_4, DP_MAX_AGE):
            values = modvar[sex][age]
            getRowOfYearVals(sheet, values, params, row)    
            row += 1

def import_AIDSMortality(sheet, params, projection):    
    modvarTagRow = findTagRow(sheet, '<AIDSMortality MV2>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_AIDSMortalityTag]

    row = modvarTagRow + 3
    
    for sex in GBRange(GB_Male, GB_Female):
        for age in GBRange(DP_A0_4, DP_MAX_AGE):
            values = modvar[sex][age]
            getRowOfYearVals(sheet, values, params, row)    
            row += 1

def import_NumberOnARTByAge(sheet, params, projection):    
    modvarTagRow = findTagRow(sheet, '<NumberOnARTByAge MV2>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_NumberOnARTByAgeTag]

    row = modvarTagRow + 3
    
    for sex in GBRange(GB_BothSexes, GB_Female):
        for age in GBRange(DP_A0_4, DP_MAX_AGE):
            values = modvar[sex][age]
            getRowOfYearVals(sheet, values, params, row)    
            row += 1

def import_NewlyStartingART(sheet, params, projection):    
    modvarTagRow = findTagRow(sheet, '<NewlyStartingART MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_NewlyStartingARTTag]

    row = modvarTagRow + 3
    
    for sex in GBRange(GB_BothSexes, GB_Female):
        for age in GBRange(DP_A0_4, DP_MAX_AGE):
            values = modvar[sex][age]
            getRowOfYearVals(sheet, values, params, row)    
            row += 1

def import_AdultsChildrenStartingART(sheet, params, projection):    
    modvarTagRow = findTagRow(sheet, '<AdultsChildrenStartingART MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_AdultsChildrenStartingARTTag]

    row = modvarTagRow + 3
    
    for sex in GBRange(GB_Male, GB_Female):
        for age in GBRange(DP_AllAges, DP_MAX_AGE):
            values = modvar[sex][age]
            getRowOfYearVals(sheet, values, params, row)    
            row += 1

    for age in GBRange(DP_AllAges, DP_MAX_AGE):
        for year in GBRange(params.firstYear, params.finalYear):
            t = getYearIdx(year, params.firstYear)
            modvar[GB_BothSexes][age][t] = modvar[GB_Male][age][t] + modvar[GB_Female][age][t]

def import_PercentOfPop(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<PercentOfPop MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_PercentOfPopTag]

    row = modvarTagRow + 2
    values = modvar
    getRowOfYearVals(sheet, values, params, row)

def import_FirstYearOfEpidemic(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<FirstYearOfEpidemic MV>')
    if (modvarTagRow < 0): return

    row = modvarTagRow + 2
    epidemic_start_year = int(sheet.values[row, GB_RW_DataStartCol])

    # Need to reset the Sex ratio defaults  to the new first year of epidemic
    if epidemic_start_year != projection[AM_FirstYearOfEpidemicTag]: 
        AMGlobalData = GB_get_db_json(environ[GB_SPECT_MOD_DATA_CONN_ENV], 
                                      'aim', 
                                      formatCountryFName('AM_Global', AMDatabaseVersion)) 
        sr_defaults = HIVSexRatio_Meta_Init({
            'firstYr': params.firstYear,
            'finalYr': params.finalYear,
            'finalYrIdx': getYearIdx(params.finalYear, params.firstYear),
            'epidemicStartYr': epidemic_start_year,
        }, AMGlobalData)
        projection[AM_HIVSexRatio_MetaTag] = {'default': sr_defaults} 

    projection[AM_FirstYearOfEpidemicTag]   = epidemic_start_year
   

def import_ARTCoverageSelection(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<ARTCoverageSelection MV>')
    if (modvarTagRow < 0): return
    # modvar = projection[AM_ARTCoverageSelectionTag]

    row = modvarTagRow + 2
    projection[AM_ARTCoverageSelectionTag] = int(sheet.values[row, GB_RW_DataStartCol])

def import_BFYearsRGIdx(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<BFYearsRGIdx MV>')
    if (modvarTagRow < 0): return
    # modvar = projection[AM_BFYearsRGIdxTag]

    row = modvarTagRow + 2
    projection[AM_BFYearsRGIdxTag] = int(sheet.values[row, GB_RW_DataStartCol])

def import_BFArvRGIdx(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<BFArvRGIdx MV>')
    if (modvarTagRow < 0): return
    # modvar = projection[AM_BFArvRGIdxTag]

    row = modvarTagRow + 2
    projection[AM_BFArvRGIdxTag] = int(sheet.values[row, GB_RW_DataStartCol])

def import_ChildHIVMortARTRegion(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<ChildHIVMortARTRegion MV>')
    if (modvarTagRow < 0): return
    # modvar = projection[AM_ChildHIVMortARTRegionTag]

    row = modvarTagRow + 2
    if int(sheet.values[row, GB_RW_DataStartCol]) not in [0, DP_Custom]:
        projection[AM_ChildHIVMortARTRegionTag] = int(sheet.values[row, GB_RW_DataStartCol])
            
def import_ChildHIVMortARTCustomFlag(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<ChildHIVMortARTCustomFlag MV>')
    if (modvarTagRow < 0): return
    # modvar = projection[AM_ChildHIVMortARTCustomFlagTag]
    
    row = modvarTagRow + 2
    projection[AM_ChildHIVMortARTCustomFlagTag] = bool(int(sheet.values[row, GB_RW_DataStartCol]))

def import_ChildARTDistRegion(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<ChildARTDistRegion MV2>')
    if (modvarTagRow < 0): return
    # modvar = projection[AM_ChildARTDistRegionTag]

    row = modvarTagRow + 2
    if int(sheet.values[row, GB_RW_DataStartCol]) not in [0, DP_Custom]:
        projection[AM_ChildARTDistRegionTag] = int(sheet.values[row, GB_RW_DataStartCol])
            
def import_ChildARTDistCustomFlag(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<ChildARTDistCustomFlag MV>')
    if (modvarTagRow < 0): return
    # modvar = projection[AM_ChildARTDistCustomFlagTag]
    
    row = modvarTagRow + 2
    projection[AM_ChildARTDistCustomFlagTag] = bool(int(sheet.values[row, GB_RW_DataStartCol]))

def import_AdultProgressRatesRegion(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<AdultProgressRatesRegion MV2>')
    if (modvarTagRow < 0): return
    # modvar = projection[AM_AdultProgressRatesRegionTag]

    row = modvarTagRow + 2
    if int(sheet.values[row, GB_RW_DataStartCol]) not in [0, DP_Custom]:
        projection[AM_AdultProgressRatesRegionTag] = int(sheet.values[row, GB_RW_DataStartCol])
            
def import_AdultProgressRatesCustomFlag(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<AdultProgressRatesCustomFlag MV>')
    if (modvarTagRow < 0): return
    # modvar = projection[AM_AdultProgressRatesCustomFlagTag]
    
    row = modvarTagRow + 2
    projection[AM_AdultProgressRatesCustomFlagTag] = bool(int(sheet.values[row, GB_RW_DataStartCol]))

def import_AdultHIVMortNoARTRegion(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<AdultHIVMortNoARTRegion MV2>')
    if (modvarTagRow < 0): return
    # modvar = projection[AM_AdultHIVMortNoARTRegionTag]

    row = modvarTagRow + 2
    if int(sheet.values[row, GB_RW_DataStartCol]) not in [0, DP_Custom]:
        projection[AM_AdultHIVMortNoARTRegionTag] = int(sheet.values[row, GB_RW_DataStartCol])
            
def import_AdultHIVMortNoARTCustomFlag(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<AdultHIVMortNoARTCustomFlag MV>')
    if (modvarTagRow < 0): return
    # modvar = projection[AM_AdultHIVMortNoARTCustomFlagTag]
    
    row = modvarTagRow + 2
    projection[AM_AdultHIVMortNoARTCustomFlagTag] = bool(int(sheet.values[row, GB_RW_DataStartCol]))

def import_AdultHIVMortARTRegion(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<HIV Mortality with ART Country or Region MV>')
    if (modvarTagRow < 0): return
    # modvar = projection[AM_AdultHIVMortARTRegionTag]

    row = modvarTagRow + 2
    if int(sheet.values[row, GB_RW_DataStartCol]) not in [0, DP_Custom]:
        projection[AM_AdultHIVMortARTRegionTag] = int(sheet.values[row, GB_RW_DataStartCol])
            
def import_AdultHIVMortARTCustomFlag(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<AdultHIVMortARTCustomFlag MV>')
    if (modvarTagRow < 0): return
    # modvar = projection[AM_AdultHIVMortARTCustomFlagTag]
    
    row = modvarTagRow + 2
    projection[AM_AdultHIVMortARTCustomFlagTag] = bool(int(sheet.values[row, GB_RW_DataStartCol]))

def import_DALYBaseYear(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<DALYBaseYear MV>')
    if (modvarTagRow < 0): return
    # modvar = projection[AM_DALYBaseYearTag]

    row = modvarTagRow + 2
    projection[AM_DALYBaseYearTag] = int(sheet.values[row, GB_RW_DataStartCol])

def import_DALYDiscountRate(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<DALYDiscountRate MV>')
    if (modvarTagRow < 0): return
    # modvar = projection[AM_DALYDiscountRateTag]

    row = modvarTagRow + 2
    projection[AM_DALYDiscountRateTag] = float(sheet.values[row, GB_RW_DataStartCol])
            
def import_DALYUseStandardLifeTable(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<DALYUseStandardLifeTable MV>')
    if (modvarTagRow < 0): return
    # modvar = projection[AM_DALYUseStandardLifeTableTag]
    
    row = modvarTagRow + 2
    projection[AM_DALYUseStandardLifeTableTag] = bool(int(sheet.values[row, GB_RW_DataStartCol]))

def import_OrphansRegionalPattern(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<OrphansRegionalPattern MV>')
    if (modvarTagRow < 0): return
    # modvar = projection[AM_OrphansRegionalPatternTag]

    row = modvarTagRow + 2
    projection[AM_OrphansRegionalPatternTag] = int(sheet.values[row, GB_RW_DataStartCol])
            
def import_IncidenceInput1970Bool(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<IncidenceInput1970Bool MV>')
    if (modvarTagRow < 0): return
    # modvar = projection[AM_IncidenceInput1970BoolTag]
    
    row = modvarTagRow + 2
    projection[AM_IncidenceInput1970BoolTag] = bool(int(sheet.values[row, GB_RW_DataStartCol]))

def import_IncidenceOptions(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<IncidenceOptions MV>')
    if (modvarTagRow < 0): return
    # modvar = projection[AM_IncidenceOptionsTag]

    row = modvarTagRow + 2
    projection[AM_IncidenceOptionsTag] = int(sheet.values[row, GB_RW_DataStartCol])

def import_IncidenceByFit(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<IncidenceByFit MV4>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_IncidenceByFitTag]

    row = modvarTagRow + 2
    for i in GBRange(DP_DirectIncidenceInputOpt, DP_ECDCOpt):
        values = modvar[i]
        getRowOfYearVals(sheet, values, params, row)    
        row += 1

def import_FourDecPlaceID(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<FourDecPlaceID MV2>')
    if (modvarTagRow < 0): return
    # modvar = projection[AM_FourDecPlaceIDTag]

    row = modvarTagRow + 3
    projection[AM_FourDecPlaceIDTag] = bool(int(sheet.values[row, GB_RW_DataStartCol]))
            
def import_EPPPrevAdj(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<EPPPrevAdj MV>')
    if (modvarTagRow < 0): return
    # modvar = projection[AM_EPPPrevAdjTag]
    
    row = modvarTagRow + 2
    projection[AM_EPPPrevAdjTag] = bool(int(sheet.values[row, GB_RW_DataStartCol]))
            
def import_EPPMaxAdjFactor(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<EPPMaxAdjFactor MV>')
    if (modvarTagRow < 0): return
    # modvar = projection[AM_EPPMaxAdjFactorTag]
    
    row = modvarTagRow + 2
    projection[AM_EPPMaxAdjFactorTag] = float(sheet.values[row, GB_RW_DataStartCol])
            
def import_EPPPopulationAges(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<EPPPopulationAges MV>')
    if (modvarTagRow < 0): return
    # modvar = projection[AM_EPPPopulationAgesTag]
    
    row = modvarTagRow + 2
    projection[AM_EPPPopulationAgesTag] = int(sheet.values[row, GB_RW_DataStartCol])
            
def import_CustomSAPDataIndex(sheet, params, projection):
    DP_FittedPattern            = 6
    DP_CSAVRPattern             = 7

    modvarTagRow = findTagRow(sheet, '<IncEpidemicRGIdx MV>')
    if (modvarTagRow < 0): return
    # modvar = projection[AM_IncEpidemicRGIdxTag]
    
    row = modvarTagRow + 2
    projection[AM_CustomSAPDataIndexTag] = int(sheet.values[row, GB_RW_DataStartCol])

    if projection[AM_CustomSAPDataIndexTag] == DP_FittedPattern:
        # index things
        SAPFitTypeTagRow = findTagRow(sheet, '<SAPFitType MV>')
        HIVPrevModelTagRow = findTagRow(sheet, '<HIVPrevModel MV>')
        if (SAPFitTypeTagRow >= 0) and (HIVPrevModelTagRow >= 0):
            SAPFitTypeRow = SAPFitTypeTagRow + 2
            HIVPrevModelRow = HIVPrevModelTagRow + 2
            SAPFitType = int(sheet.values[SAPFitTypeRow, GB_RW_DataStartCol])
            HIVPrevModel = int(sheet.values[HIVPrevModelRow, GB_RW_DataStartCol])

            if (SAPFitType == DP_SAP_HIVPrevByAge):
                if (HIVPrevModel == DP_SAP_FixedIROverTime):
                    projection[AM_CustomSAPDataIndexTag] = DP_HIVPrevFixed_Index
                else:
                    projection[AM_CustomSAPDataIndexTag] = DP_HIVPrevTime_Index
            else:
                projection[AM_CustomSAPDataIndexTag] = DP_FittedToART_Index
    elif projection[AM_CustomSAPDataIndexTag] == DP_CSAVRPattern:
        projection[AM_CustomSAPDataIndexTag] = DP_PatternFromCSAVR_Index



            
def import_IncEpidemicCustomFlagIdx(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<IncEpidemicCustomFlagIdx MV>')
    if (modvarTagRow < 0): return
    # modvar = projection[AM_IncEpidemicCustomFlagTag]
    
    row = modvarTagRow + 2
    projection[AM_IncEpidemicCustomFlagTag] = bool(int(sheet.values[row, GB_RW_DataStartCol]))
            
def import_SexRatioFromEPP(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<SexRatioFromEPP MV>')
    if (modvarTagRow < 0): return
    # modvar = projection[AM_SexRatioFromEPPTag]
    
    row = modvarTagRow + 2
    projection[AM_SexRatioFromEPPTag] = bool(int(sheet.values[row, GB_RW_DataStartCol]))

def import_HIVSexRatioFromEPP(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<HIVSexRatioFromEPP MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_HIVSexRatioFromEPPTag]

    row = modvarTagRow + 2
    values = modvar
    getRowOfYearVals(sheet, values, params, row)  
            
def import_EpidemicTypeFromEPP(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<EpidemicTypeFromEPP MV>')
    if (modvarTagRow < 0): return
    # modvar = projection[AM_EpidemicTypeFromEPPTag]
    
    row = modvarTagRow + 2
    projection[AM_EpidemicTypeFromEPPTag] = str(sheet.values[row, GB_RW_DataStartCol])

def import_AdultPrevalence(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<AdultPrevalence MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_AdultPrevalenceTag]

    row = modvarTagRow + 2
    values = modvar
    getRowOfYearVals(sheet, values, params, row)  
    
            
def import_NumOfEPPEpidemics(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<NumOfEPPEpidemics MV>')
    if (modvarTagRow < 0): return
    # modvar = projection[AM_NumOfEPPEpidemicsTag]
    
    row = modvarTagRow + 2
    projection[AM_NumOfEPPEpidemicsTag] = int(sheet.values[row, GB_RW_DataStartCol])
            
def import_EPPCountryName(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<EPPCountryName MV>')
    if (modvarTagRow < 0): return
    # modvar = projection[AM_EPPCountryNameTag]
    
    row = modvarTagRow + 2
    projection[AM_EPPCountryNameTag] = str(sheet.values[row, GB_RW_DataStartCol])
            
def import_EPPEpiName(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<EPPEpiName MV>')
    if (modvarTagRow < 0): return
    epi_name_mv = ['']# np.full((projection[AM_NumOfEPPEpidemicsTag]+1,getYearIdx(params.finalYear, params.firstYear)+1), '')
    
    numEpidemics = projection[AM_NumOfEPPEpidemicsTag]
    
    row = modvarTagRow + 2
    for epi in GBRange(DP_MinEpidemic, numEpidemics):
        epi_name = str(sheet.values[row, GB_RW_DataStartCol])
        if epi_name != '':
            epi_name_mv.append(epi_name)
        row += 1
    projection[AM_EPPEpiNameTag] = epi_name_mv
    pass
            
def import_EPPEpidemic(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<EPPEpidemic MV>')
    if (modvarTagRow < 0): return
    projection[AM_EPPEpidemicTag] = ['']
    modvar = projection[AM_EPPEpidemicTag]

    numEpidemics = projection[AM_NumOfEPPEpidemicsTag]
    
    row = modvarTagRow + 2
    for epi in GBRange(DP_MinEpidemic, numEpidemics):
        modvar.append(sheet.values[row, GB_RW_DataStartCol])
        row += 1
    pass
            
def import_EPPPrevData(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<EPPPrevData MV>')
    if (modvarTagRow < 0): return
    projection[AM_EPPPrevDataTag] = np.zeros((projection[AM_NumOfEPPEpidemicsTag]+1,getYearIdx(params.finalYear, params.firstYear)+1))
    modvar = projection[AM_EPPPrevDataTag]

    numEpidemics = projection[AM_NumOfEPPEpidemicsTag]
    
    row = modvarTagRow + 2
    for epi in GBRange(DP_MinEpidemic, numEpidemics):
        values = modvar[epi]
        getRowOfYearVals(sheet, values, params, row)  
        row += 1
            
def import_EPPIncData(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<EPPIncData MV>')
    if (modvarTagRow < 0): return
    projection[AM_EPPIncDataTag] = np.zeros((projection[AM_NumOfEPPEpidemicsTag]+1,getYearIdx(params.finalYear, params.firstYear)+1))
    modvar = projection[AM_EPPIncDataTag]

    numEpidemics = projection[AM_NumOfEPPEpidemicsTag]
    
    row = modvarTagRow + 2
    for epi in GBRange(DP_MinEpidemic, numEpidemics):
        values = modvar[epi]
        getRowOfYearVals(sheet, values, params, row)  
        row += 1
            
def import_EPPPopData(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<EPPPopData MV>')
    if (modvarTagRow < 0): return
    projection[AM_EPPPopDataTag] = np.zeros((projection[AM_NumOfEPPEpidemicsTag]+1,getYearIdx(params.finalYear, params.firstYear)+1))
    modvar = projection[AM_EPPPopDataTag]

    numEpidemics = projection[AM_NumOfEPPEpidemicsTag]
    
    row = modvarTagRow + 2
    for epi in GBRange(DP_MinEpidemic, numEpidemics):
        values = modvar[epi]
        getRowOfYearVals(sheet, values, params, row)  
        row += 1
            
def import_EPPSexRatio(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<EPPSexRatio MV>')
    if (modvarTagRow < 0): return
    projection[AM_EPPSexRatioTag] = np.zeros((projection[AM_NumOfEPPEpidemicsTag]+1,getYearIdx(params.finalYear, params.firstYear)+1))
    modvar = projection[AM_EPPSexRatioTag]
    
    row = modvarTagRow + 3
    for epi in GBRange(DP_MinEpidemic, projection[AM_NumOfEPPEpidemicsTag]):
        values = modvar[epi]
        getRowOfYearVals(sheet, values, params, row)  
        row += 1
            
def import_EPPBaseYrPop(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<EPPBaseYrPop MV>')
    if (modvarTagRow < 0): return
    projection[AM_EPPBaseYrPopTag] = np.zeros((projection[AM_NumOfEPPEpidemicsTag]+1))
    modvar = projection[AM_EPPBaseYrPopTag]

    numEpidemics = projection[AM_NumOfEPPEpidemicsTag]
    
    row = modvarTagRow + 2
    if numEpidemics>0:
        for epi in GBRange(DP_CountryID, numEpidemics):
            modvar[epi] = float(sheet.values[row, GB_RW_DataStartCol + epi - DP_CountryID])
    pass
            
def import_EPPIDUMortality(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<EPPIDUMortality MV>')
    if (modvarTagRow < 0): return
    projection[AM_EPPIDUMortalityTag] = np.zeros(projection[AM_NumOfEPPEpidemicsTag]+1)
    modvar = projection[AM_EPPIDUMortalityTag]

    numEpidemics = projection[AM_NumOfEPPEpidemicsTag]
    
    row = modvarTagRow + 2
    if numEpidemics>0:
        for epi in GBRange(DP_CountryID, numEpidemics):
            modvar[epi] = float(sheet.values[row, GB_RW_DataStartCol + epi - DP_CountryID])
            
def import_EPPPathInfo(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<EPPPathInfo MV>')
    if (modvarTagRow < 0): return
    projection[AM_EPPPathInfoTag] = np.full(projection[AM_NumOfEPPEpidemicsTag]+1, getPathInfoDict(False, ''))
    modvar = projection[AM_EPPPathInfoTag]

    numEpidemics = projection[AM_NumOfEPPEpidemicsTag]
    
    row = modvarTagRow + 2
    if numEpidemics>0:
        for epi in GBRange(DP_MinEpidemic, numEpidemics):
            modvar[epi]['IsTotal'] = bool(int(sheet.values[row, GB_RW_DataStartCol]))
            modvar[epi]['FullName'] = str(sheet.values[row, GB_RW_DataStartCol + 1])
            row += 1

def import_EppAgeRange(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<EppAgeRange MV>')
    if (modvarTagRow < 0): return
    # modvar = projection[AM_EppAgeRangeTag]

    row = modvarTagRow + 2
    projection[AM_EPPAgeRangeTag] = int(sheet.values[row, GB_RW_DataStartCol])

def import_YrPtPrevalence_WB(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<YrPtPrevalence_WB MV2>')
    if (modvarTagRow < 0): return
    # modvar = projection[AM_YrPtPrevalence_WBTag]

    row = modvarTagRow + 2
    value = str(sheet.values[row, GB_RW_DataStartCol])
    projection[AM_YrPtPrevalence_WBTag] = value if value != 'None' else ''

def import_AIDSDeathsAmongIDU(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<AIDSDeathsAmongIDU MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_AIDSDeathsAmongIDUTag]

    row = modvarTagRow + 2
    values = modvar
    getRowOfYearVals(sheet, values, params, row)  
            
def import_PropIDU_WB(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<PropIDU_WB MV>')
    if (modvarTagRow < 0): return
    projection[AM_PropIDU_WBTag] = np.zeros((projection[AM_NumOfEPPEpidemicsTag]+1,getYearIdx(params.finalYear, params.firstYear)+1))
    modvar = projection[AM_PropIDU_WBTag]

    numEpidemics = projection[AM_NumOfEPPEpidemicsTag]
    
    row = modvarTagRow + 3
    if numEpidemics>0:
        for epi in GBRange(DP_CountryID, projection[AM_NumOfEPPEpidemicsTag]):
            values = modvar[epi]
            getRowOfYearVals(sheet, values, params, row)  
            row += 1
            
def import_NonAIDSDeathsAmongIDU(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<NonAIDSDeathsAmongIDU MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_NonAIDSDeathsAmongIDUTag]
    
    row = modvarTagRow + 2
    values = modvar
    getRowOfYearVals(sheet, values, params, row)  

def import_SexuallyActive15to19(sheet, params, projection):    
    modvarTagRow = findTagRow(sheet, '<SexuallyActive15to19 MV2>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_SexuallyActive15to19Tag]

    row = modvarTagRow + 3
    
    modvar['value'] = float(sheet.values[row, GB_RW_DataStartCol])
    modvar['str'] = str(sheet.values[row, GB_RW_DataStartCol + 1])
            
def import_AIDSMortAllAgesFYrAdjIdx(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<AIDSMortAllAgesFYrAdjIdx MV>')
    if (modvarTagRow < 0): return
    # modvar = projection[AM_AIDSMortAllAgesFYrAdjIdxTag]

    row = modvarTagRow + 2
    projection[AM_AIDSMortAllAgesFYrAdjIdxTag] = int(sheet.values[row, GB_RW_DataStartCol])

def import_ValidationAllCauseDeathsART(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<AllCauseDeathsARTValidation MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_ValidationAllCauseDeathsARTTag]

    row = modvarTagRow + 2
    values = modvar
    getRowOfYearVals(sheet, values, params, row)  

def import_AdvOptsMeningitis(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<AdvOptsMeningitis MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_AdvOptsMeningitis_Tag]

    row = modvarTagRow + 2
    modvar['progInCare'] = float(sheet.values[row, GB_RW_DataStartCol])
    modvar['progNotInCare'] = float(sheet.values[row, GB_RW_DataStartCol + 1])
    modvar['progWithFluconazole'] = float(sheet.values[row, GB_RW_DataStartCol + 2])
    modvar['mortRateCMInCare'] = float(sheet.values[row, GB_RW_DataStartCol + 3])
    modvar['mortRateCMNotInCare'] = float(sheet.values[row, GB_RW_DataStartCol + 4])
    

def import_PrevNeedFirstTime(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<PreventionNeeds_FirstTime MV>')
    if (modvarTagRow < 0): return

    row = modvarTagRow + 2
    projection[AM_PreventionNeedsFirstTimeTag] = bool(int(sheet.values[row, GB_RW_DataStartCol]))
    pass

def import_PrevNeedShowVMMC(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<PreventionNeeds_ShowVMMCTab MV>')
    if (modvarTagRow < 0): return

    row = modvarTagRow + 2
    projection[AM_PreventionNeedsShowVMMCTabTag] = bool(int(sheet.values[row, GB_RW_DataStartCol]))
    pass
    # modvar['showVMMC'] = bool(int(sheet.values[row, GB_RW_DataStartCol + 1]))
    pass


def import_PrevNeedKeyPop(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<PreventionNeeds_KeyPops MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_PreventionNeedsKeyPopsTag]

    row = modvarTagRow + 3
    
    # populations
    for kp in range(len(DP_TKeyPopType)):
        modvar['data'][kp]['population'] = float(sheet.values[row, GB_RW_DataStartCol])
        row += 1

    # coverages
    for kp in range(len(DP_TKeyPopType)):
        modvar['data'][kp]['coverage'] = float(sheet.values[row, GB_RW_DataStartCol])
        row += 1

    # ratio
    modvar['ratio'] = float(sheet.values[row, GB_RW_DataStartCol])
    row += 1

    # sources
    for kp in range(len(DP_TKeyPopType)):
        modvar['data'][kp]['source'] = sheet.values[row, GB_RW_DataStartCol]
        row += 1

    # user coverages
    for kp in range(len(DP_TKeyPopType)):
        modvar['data'][kp]['userCoverage'] = float(sheet.values[row, GB_RW_DataStartCol])
        row += 1
    pass


def import_PrevNeedVMMC(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<PreventionNeeds_VMMC MV>')
    if (modvarTagRow < 0): return
    # modvar = projection[AM_PreventionNeedsVMMCTag]

    row = modvarTagRow + 3
    areas = []
    while not (sheet.values[row, GB_RW_TagCol] == '<End>'):

        regionName = sheet.values[row, GB_RW_DescriptCol]
        areaName   = sheet.values[row, GB_RW_NotesCol]

        # Skip completely empty rows (no region, no area, no data)
        if( (regionName == '') and (areaName == '') ):
            row += 1
            continue
        # Fill area data
        newArea={}
        newArea['name'] = areaName
        newArea['region'] = regionName
        newArea['popFirstYear'] = float(sheet.values[row, GB_RW_DataStartCol])
        newArea['popFinalYear'] = float(sheet.values[row, GB_RW_DataStartCol+1])
        newArea['covFirstYear'] = float(sheet.values[row, GB_RW_DataStartCol+2])
        newArea['targetCov'] = float(sheet.values[row, GB_RW_DataStartCol+3])
        newArea['tradCircum'] = float(sheet.values[row, GB_RW_DataStartCol+4])
        newArea['percAged15'] = float(sheet.values[row, GB_RW_DataStartCol+5])
        newArea['percAged29'] = float(sheet.values[row, GB_RW_DataStartCol+6])


        # Only create a new region if the regionName is not empty
        # if (regionName <> '') and
        # ((Length(vValue.Regions) = 0) or
        #     (vValue.Regions[High(vValue.Regions)].Name <> regionName)) then
        # begin
        #     newRegion.Name := regionName;
        #     SetLength(newRegion.Areas, 0);
        #     SetLength(vValue.Regions, Length(vValue.Regions)+1);
        #     vValue.Regions[High(vValue.Regions)] := newRegion;
        # end;

        # Append area to the last region if there is a region
        # if Length(vValue.Regions) > 0 then
        # begin
        # SetLength(vValue.Regions[High(vValue.Regions)].Areas,
        #             Length(vValue.Regions[High(vValue.Regions)].Areas)+1);
        # vValue.Regions[High(vValue.Regions)].Areas[
        #     High(vValue.Regions[High(vValue.Regions)].Areas)
        # ] := newArea;
        # end;
        areas.append(newArea)
        row += 1
    projection[AM_PreventionNeedsVMMCTag] = areas
    # pass


def import_PrevNeedCondoms(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<PreventionNeeds_Condoms MV>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_PreventionNeedsCondomsTag]

    row = modvarTagRow + 3
    # Population first year
    for condom in range(len(DP_TCondomType)):
      modvar['data'][condom]['popFirstYear'] = float(sheet.values[row, GB_RW_DataStartCol])
      row += 1

    # Population final year
    for condom in range(len(DP_TCondomType)):
      modvar['data'][condom]['popFinalYear'] = float(sheet.values[row, GB_RW_DataStartCol])
      row += 1

    # Baseline coverage
    for condom in range(len(DP_TCondomType)):
      modvar['data'][condom]['baselineCov'] = float(sheet.values[row, GB_RW_DataStartCol])
      row += 1

    # Target coverage
    for condom in range(len(DP_TCondomType)):
      modvar['data'][condom]['targetCov'] = float(sheet.values[row, GB_RW_DataStartCol])
      row += 1

    # Sex acts
    for condom in range(len(DP_TCondomType)):
      modvar['data'][condom]['sexActs'] = float(sheet.values[row, GB_RW_DataStartCol])
      row += 1

    # Wastage
    for condom in range(len(DP_TCondomType)):
      modvar['data'][condom]['wastage'] = float(sheet.values[row, GB_RW_DataStartCol])
      row += 1
    pass


def import_PrevNeedPrEP_V2(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<PreventionNeeds_PrEP MV2>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_PreventionNeedsPrEPTag]

    row = modvarTagRow + 3
    
    # Population first year
    for PP in range(len(DP_TPrEPType)):
        modvar['data'][PP]['PopFirstYear'] = float(sheet.values[row, GB_RW_DataStartCol+2])
        row += 1

    # Population final year
    for PP in range(len(DP_TPrEPType)):
        modvar['data'][PP]['PopFinalYear'] = float(sheet.values[row, GB_RW_DataStartCol+2])
        row += 1

    # PrEP coverage
    for PP in range(len(DP_TPrEPType)):
        modvar['data'][PP]['PrEPCov'] = float(sheet.values[row, GB_RW_DataStartCol+2])
        row += 1

    # Target coverage
    for PP in range(len(DP_TPrEPType)):
        modvar['data'][PP]['TargetCov'] = float(sheet.values[row, GB_RW_DataStartCol+2])
        row += 1

    # Oral
    for pr in range(DP_PreventionNeeds_PrEPYearLen):
        for PP in range(len(DP_TPrEPType)):
            modvar['data'][PP]['Oral'][pr] = float(sheet.values[row, GB_RW_DataStartCol+3])
            row += 1

    # Ring
    for pr in range(DP_PreventionNeeds_PrEPYearLen):
        for PP in range(len(DP_TPrEPType)):
            modvar['data'][PP]['Ring'][pr] = float(sheet.values[row, GB_RW_DataStartCol+3])
            row += 1

    # Two month
    for pr in range(DP_PreventionNeeds_PrEPYearLen):
        for PP in range(len(DP_TPrEPType)):
            modvar['data'][PP]['TwoMonth'][pr] = float(sheet.values[row, GB_RW_DataStartCol+3])
            row += 1

    # Six month
    for pr in range(DP_PreventionNeeds_PrEPYearLen):
        for PP in range(len(DP_TPrEPType)):
            modvar['data'][PP]['SixMonth'][pr] = float(sheet.values[row, GB_RW_DataStartCol+3])
            row += 1
    pass

def import_PrevNeedPrEP_V3(sheet, params, projection):   
    modvarTagRow = findTagRow(sheet, '<PreventionNeeds_PrEP MV3>')
    if (modvarTagRow < 0): return
    modvar = projection[AM_PreventionNeedsPrEPTag]

    row = modvarTagRow + 3
    
    # Population first year
    for PP in range(len(DP_TPrEPType)):
        modvar['data'][PP]['PopFirstYear'] = float(sheet.values[row, GB_RW_DataStartCol+2])
        row += 1

    # Population final year
    for PP in range(len(DP_TPrEPType)):
        modvar['data'][PP]['PopFinalYear'] = float(sheet.values[row, GB_RW_DataStartCol+2])
        row += 1

    # Prevalence 
    for PP in range(len(DP_TPrEPType)):
        modvar['data'][PP]['Prev'] = float(sheet.values[row, GB_RW_DataStartCol+2])
        row += 1

    # PrEP coverage
    for PP in range(len(DP_TPrEPType)):
        modvar['data'][PP]['PrEPCov'] = float(sheet.values[row, GB_RW_DataStartCol+2])
        row += 1

    # Target coverage
    for PP in range(len(DP_TPrEPType)):
        modvar['data'][PP]['TargetCov'] = float(sheet.values[row, GB_RW_DataStartCol+2])
        row += 1

    # Oral
    for pr in range(DP_PreventionNeeds_PrEPYearLen):
        for PP in range(len(DP_TPrEPType)):
            modvar['data'][PP]['Oral'][pr] = float(sheet.values[row, GB_RW_DataStartCol+3])
            row += 1

    # Ring
    for pr in range(DP_PreventionNeeds_PrEPYearLen):
        for PP in range(len(DP_TPrEPType)):
            modvar['data'][PP]['Ring'][pr] = float(sheet.values[row, GB_RW_DataStartCol+3])
            row += 1

    # Two month
    for pr in range(DP_PreventionNeeds_PrEPYearLen):
        for PP in range(len(DP_TPrEPType)):
            modvar['data'][PP]['TwoMonth'][pr] = float(sheet.values[row, GB_RW_DataStartCol+3])
            row += 1

    # Six month
    for pr in range(DP_PreventionNeeds_PrEPYearLen):
        for PP in range(len(DP_TPrEPType)):
            modvar['data'][PP]['SixMonth'][pr] = float(sheet.values[row, GB_RW_DataStartCol+3])
            row += 1
    pass


def import_PrEPParameters(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<PrEPParameters MV>')
    if (modvarTagRow < 0): return

    row = modvarTagRow + 3 
    modvar = projection[AM_PMTCTPrEPParametersTag]
    modvar['adherence']['oral'] = float(sheet.values[row, GB_RW_DataStartCol])
    modvar['adherence']['injectable'] = float(sheet.values[row+1, GB_RW_DataStartCol])
    modvar['selection']['incidenceRatio'] = float(sheet.values[row+2, GB_RW_DataStartCol])
    modvar['personYearsPrEP']['oral'] = float(sheet.values[row+3, GB_RW_DataStartCol])
    modvar['personYearsPrEP']['injectable'] = float(sheet.values[row+4, GB_RW_DataStartCol])
    pass
        
def import_PrEPForPregnantWomen(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<PrEPForPregnantWomen MV>')
    if (modvarTagRow < 0): return

    row = modvarTagRow + 2 
    getRowOfYearVals(sheet, projection[AM_PMTCTReceivingOralPrEPTag], params, row)  
    getRowOfYearVals(sheet, projection[AM_PMTCTReceivingInjectablePrEPTag], params, row+1)  
    pass


def import_KOSNewDiagnosesAdults15Plus(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<KOSNewDiagnosesAdults15Plus MV>')
    if (modvarTagRow < 0): return

    row = modvarTagRow + 2 
    getRowOfYearVals(sheet, projection[AM_KOSNewDiagnosesAdults15PlusTag], params, row)  
    pass


def import_KOSNewDiagnosesChildren0to14(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<KOSNewDiagnosesChildren0_14 MV>')
    if (modvarTagRow < 0): return

    row = modvarTagRow + 2 
    getRowOfYearVals(sheet, projection[AM_KOSNewDiagnosesChildren0t14Tag], params, row)  
    pass


def import_KOSNewDiagnosesRecCD4Test(sheet, params, projection):
    modvarTagRow = findTagRow(sheet, '<KOSNewDiagnosesRecCD4Test MV>')
    if (modvarTagRow < 0): return

    row = modvarTagRow + 2 
    getRowOfYearVals(sheet, projection[AM_KOSNewDiagnosesRecCD4TestTag], params, row)  
    pass
