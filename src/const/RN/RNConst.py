
# Used for CustomEasyData imported from projection #
RN_ImportedProj  = 1

# Constants for writing to file #
RN_Version       = 1.0
RN_DataFileTitle = 'Resource Needs Model'

GB_FirstProj = 1

# Time constants #
RN_Min_Year         = 1

# Region constant #
RN_Total            = 0

# Sex constants #
RN_BothSexes        = 0
RN_Male             = 1
RN_Female           = 2

# Display constants #

# Sectors #
RN_GeneralSect  = 1
RN_ResourcesRequiredSect       = 1
RN_NumberPeopleReachedSect     = 2
RN_AdultTreatmentCostsSect     = 3
RN_ChildPMTCTandTreatCostsSect = 4
RN_NUM_SECT                    = 4
RN_MAXSEC                      = 4

# Indicators #
RN_FirstInd                       = 1
RN_SummaryResourcesRequiredInd    = 1
RN_SummaryNumberPeopleReachedInd  = 2
# Adult Treatment Costs #
RN_FirstLineARVInd                = 3
RN_SecondLineARVInd               = 4
RN_TBArvInd                       = 5
RN_LabTestInd                     = 6
RN_OItreatmentInd                 = 7
RN_CotrimoxazoleInd               = 8
RN_TBProphylaxisInd               = 9
RN_NutritionInd                   = 10
RN_FirstlineDeliveryCostsInd      = 11
RN_SecondlineDeliveryCostsInd     = 12
RN_OITreatmentDeliveryCostsInd    = 13
RN_TotalAdultTreatmentCostsInd    = 14
RN_SummaryCostsInd                = 15

# Child PMTCT and Treatment Costs #
RN_PMTCTCostsInd                  = 16
RN_ChildTreatmentCostsInd         = 17
RN_TotalChildTreatmentCostsInd    = 18
RN_PMTCTBenefitCostRatioInd       = 19
RN_SummaryPMTCTTableInd           = 20
RN_NUM_IND                        = 20

# Indicator constants #
RN_SEXIND       = 1
RN_SUMIND       = 2

RN_Indent1  = '    '          # 4 spaces
RN_Indent2  = '        '      # 8 spaces
RN_Indent3  = '            '  #12 spaces

# Graphical constants #
RN_ofTable           = 101
RN_OfPyramidPer      = 102
RN_OfPyramidNum      = 103
RN_OfSummaryTable    = 104
RN_OfStacked2D       = 105
RN_OfStacked3D       = 106

# Editor constants for getting and setting source data. #
RN_FirstEd     = 1
RN_NUM_EDITORS = 1

RN_USD           = 'USD'
RN_USCurrency    = 0
RN_LocalCurrency = 1

RN_DefaultProgramSupport   = 0
RN_UserAddedProgramSupport = 1

RN_BaseYear = 2015  #this will be updated to reflect current values in the database once they are avaialble

# Program support constants #
RN_PS_EnablingEnvironment             = 1
RN_PS_ProgramManagement               = 2
RN_PS_Research                        = 3
RN_PS_MonitoringAndEvaluation         = 4
RN_PS_StrategicCommunication          = 5
RN_PS_Logistics                       = 6
RN_PS_ProgramLevelHR                  = 7
RN_PS_Training                        = 8
RN_PS_LaboratoryEquipment             = 9
RN_PS_MaxProgramSupport               = 9
RN_PS_FirstRowUserAddedProgramSupport = 10

# Population sizes constants #
# General populations #
RN_POP_SexuallyActive15_49            = 1
RN_POP_Males15_49RegPartners          = 2
RN_POP_Males15_49NonRegPartners       = 3
RN_POP_NumSexActsRegPartners          = 4
RN_POP_NumSexActsNonRegPartners       = 5
RN_POP_CommercialSexActsFSW           = 6
RN_POP_CommercialSexActsMSW           = 7
RN_POP_CondomWastage                  = 8
RN_POP_PrimarySchoolMale              = 9
RN_POP_PrimarySchoolFemale            = 10
RN_POP_PrimaryPupilTeacher            = 11
RN_POP_SecondarySchoolMale            = 12
RN_POP_SecondarySchoolFemale          = 13
RN_POP_SecondaryPupilTeacher          = 14
RN_POP_TeacherRetraining              = 15
RN_POP_FormalSectorEmployees          = 16
RN_POP_Rapes                          = 17
# Most At-Risk populations #
RN_POP_FemaleSexWorkers               = 18
RN_POP_MaleSexWorkers                 = 19
RN_POP_MSM                            = 20
RN_POP_IDU                            = 21
RN_POP_IDUOpiodDependent              = 22
RN_POP_NumInjectionsPerYear           = 23
# Male circumcision #
RN_POP_AdultMalesCircum               = 24
# Medical Services #
RN_POP_NewCasesSTIsMale               = 25
RN_POP_NewCasesSTIsFemale             = 26
RN_POP_STIsSymptomaticMale            = 27
RN_POP_STIsSymptomaticFemale          = 28
RN_POP_BloodUnitsRequired             = 29
RN_POP_PEPKitsRequired                = 30
RN_POP_NumImmunChild0_23Mths          = 31
RN_POP_NumAdultInjections             = 32
RN_POP_InjectionsUnsafe               = 33
RN_POP_HospitalBeds                   = 34
# Max populations constants #
RN_POP_MaxPopulations                 = 34
RN_POP_MaxGeneralPop                  = 17
RN_POP_MaxRowGeneralPop               = 21
RN_POP_FirstRowUserAddedGeneralPop    = 22
RN_POP_MaxMostAtRiskPop               = 6
RN_POP_MaxRowMostAtRiskPop            = 6
RN_POP_FirstRowUserAddedMostAtRiskPop = 7
RN_POP_MaxRowNumPreSetKeyPops         = 7
RN_POP_FirstRowNumAddedKeyPops        = 8

RN_UserGeneralPop     = 1
RN_UserMostAtRiskPop  = 2

RN_Number  = 0
RN_Percent = 1

# Intervention constants #
# General Populations #
RN_ComMob                = 1
RN_MassMedia             = 2
RN_VCT                   = 3
RN_Condom                = 4
RN_PrimaryTeachers       = 5
RN_SecondaryTeachers     = 6
RN_OutOfSchoolYouth      = 7
RN_EconomicStrengthening = 8
RN_WorkplaceSTI          = 9
# Most At-Risk populations #
RN_FSW              = 10
RN_MSW              = 11
RN_MSMOutreach      = 12
RN_MSMLub           = 13
RN_IDUHarmRed       = 14
RN_IDUCandT         = 15
RN_IDUOutreach      = 16
RN_IDUNSEP          = 17
RN_IDUDrugSub       = 18
# Male circumcision #
RN_MC15_49          = 19
RN_MCInfant         = 20
# PrEP #
#  RN_PrEPOral         = 21
#  RN_PrEPInject       = 22
#  RN_PrEPGel          = 23
#  RN_PrEPRing         = 24
RN_PrEPOralDaily    = 21
RN_PrEPOralMonthly  = 22
RN_PrEPOralPlusCon  = 23
RN_PrEPInject1Mo    = 24
RN_PrEPInject2Mo    = 25
RN_PrEPInject6Mo    = 26
RN_PrEPRing         = 27
RN_PrEPbNABs        = 28
RN_PrEPImplant      = 29
RN_PrEP_PEP         = 30
# Medical services for Coverage#
RN_MalesSTITx       = 31
RN_FemalesSTITx     = 32
RN_BloodSafety      = 33
RN_PEP              = 34
RN_ADSyringes       = 35
RN_ReduceInjects    = 36
RN_UniversalPrec    = 37
# Vaccines #
RN_Vaccines         = 38
RN_Cure             = 39
RN_AHDTreatment     = 40
RN_POC_CD4_Int      = 41
RN_POC_VL_Int       = 42

RN_MaxInterventions = 42

RN_PrepInterventions = [i for i in range(RN_PrEPOralDaily, RN_PrEP_PEP + 1)]
RN_PrepInterventions_Male = [i for i in range(RN_PrEPOralDaily, RN_PrEPInject6Mo + 1)] + [RN_PrEPbNABs, RN_PrEPImplant, RN_PrEP_PEP]
RN_PrepInterventions_Female = [i for i in range(RN_PrEPOralDaily, RN_PrEP_PEP + 1)]


#  RN_MaxCovConstants  = 27

# Max coverge constants #
RN_MaxGeneralPopCoverage    = 8
RN_MaxMostAtRiskPopCoverage = 9
RN_MaxMedServicesCoverage   = 7

# Max unit costs constants #
RN_MaxGeneralPopUnitCosts       = 8
RN_MaxMostAtRiskPopUnitCosts    = 9
RN_MaxMedicalServicesUnitCosts  = 5
RN_MaxMaleCircumcisionUnitCosts = 2
RN_MaxCureUnitCosts             = 1
RN_MaxAHDTreatmentUnitCosts     = 1
RN_MaxTestingUnitCosts          = 2
#  RN_MaxPrEPUnitCosts             = 4
RN_MaxVaccinesUnitCosts         = 1
RN_MaxPMTCTUnitCosts            = 14

# Point of care #
RN_POC_CD4 = 1
RN_POC_VL  = 2

# Breakdown of PrEP coverage for CEA interpolation#
RN_CEA_PrEPLRH      = 20
RN_CEA_PrEPMRH      = 21
RN_CEA_PrEPHRH      = 22
RN_CEA_PrEPIDU      = 23
RN_CEA_PrEPMSM      = 24
RN_CEA_ART_Male     = 25
RN_CEA_ART_Female   = 26
RN_MaxCEA           = 26
# Baseline projection for CEA #
RN_BaseLineProj_CEA = 0

# ART unit costs #
RN_CostPerCD4Test              = 1
RN_CostPerViralLoadTest        = 2
RN_CostPerBloodChemistry       = 3
RN_CostPerEIDTest              = 4
RN_CostPerVisit                = 5
RN_CostOfFirstLineARVs         = 6
RN_CostOfSecondLineARVs        = 7
RN_CostOfThirdLineARVs         = 8

# Percent on ART #
RN_PercentPatientsSecondLine   = 1
RN_PercentPatientsThirdLine    = 2

# Test and Visit Schedule #
# Population #
RN_PatientsInitiatingART        = 1
RN_StablePatients               = 2
RN_PatientsNotVirallySuppressed = 3
RN_PregnantWomen                = 4
# Test/Visit #
RN_CD4Test                      = 1
RN_ViralLoadTests               = 2
RN_BloodChemistries             = 3
RN_MedicalConsultations         = 4
RN_DrugDelivAdherenceVisits     = 5
RN_EID                          = 6

# Constants for RNM Summary Tables #
RN_ST_ComMob              = 1
RN_ST_MassMedia           = 2
RN_ST_VCT                 = 3
RN_ST_Condom              = 4
RN_ST_PrimaryTeachers     = 5
RN_ST_SecondaryTeachers   = 6
RN_ST_OutOfSchoolYouth    = 7
RN_ST_CashTransfers       = 8
RN_ST_WorkplaceSTI        = 9
RN_ST_FSW                 = 10
RN_ST_MSW                 = 11
RN_ST_MSMOutreach         = 12
RN_ST_MSMLub              = 13
RN_ST_IDUHarmRed          = 14
RN_ST_IDUCandT            = 15
RN_ST_IDUOutreach         = 16
RN_ST_IDUNSEP             = 17
RN_ST_IDUDrugSub          = 18
RN_ST_MC                  = 19
#  RN_ST_PrEPOral            = 20
#  RN_ST_PrEPInject          = 21
#  RN_ST_PrEPGel             = 22
#  RN_ST_PrEPRing            = 23
RN_ST_PrEPOralDaily       = 20
RN_ST_PrEPOralMonthly     = 21
RN_ST_PrEPOralPlusCon     = 22
RN_ST_PrEPInject1Mo       = 23
RN_ST_PrEPInject2Mo       = 24
RN_ST_PrEPInject6Mo       = 25
RN_ST_PrEPRing            = 26
RN_ST_PrEPbNABs           = 27
RN_ST_PrEPImplant         = 28
RN_ST_PrEP_PEP            = 29
RN_ST_MalesSTITx          = 30
RN_ST_FemalesSTITx        = 31
RN_ST_BloodSafety         = 32
RN_ST_PEP                 = 33
RN_ST_ADSyringes          = 34
RN_ST_ReduceInjects       = 35
RN_ST_UniversalPrec       = 36
RN_ST_Vaccines            = 37
RN_ST_PMTCT               = 38
RN_ST_ARVTherapy          = 39
RN_ST_NonARTCare          = 40
RN_ST_Cure                = 41
RN_ST_AHDTreatment        = 42
RN_ST_POC_CD4_Int         = 43
RN_ST_POC_VL_Int          = 44
RN_ST_MaxSummaryTable     = 44

# Total number of items displayed in Resources Required table (not including
#   the Program Support or user entered pops #
RN_MaxSumTableDisplay    = 28
RN_RowNumBeforeUserPops  = 15  # not sure what this value should be yet


# Sets to exclude intervention constants for specific areas #
RN_NotInCEAorIM = [RN_PrimaryTeachers,RN_WorkplaceSTI, RN_MSW,RN_IDUHarmRed,RN_IDUCandT]

RN_NotInOptimize = [RN_VCT,RN_MSMLub,RN_CEA_PrEPLRH,RN_CEA_PrEPIDU]

RN_NotInCov     = [RN_PrEPOralDaily, RN_PrEPOralMonthly, RN_PrEPOralPlusCon,
RN_PrEPInject1Mo, RN_PrEPInject2Mo, RN_PrEPInject6Mo,
RN_PrEPRing, RN_PrEPbNABs, RN_PrEPImplant, RN_PrEP_PEP, RN_Vaccines]

RN_NumIntervExcludedFromCov = 5

RN_NotInUC    = [RN_FemalesSTITx, RN_ReduceInjects]

RN_NumIntervExcludedFromUC = 2

RN_NotUsedWhenOnlyRNActive = [RN_MCInfant, RN_PrEPOralDaily, RN_PrEPOralMonthly, RN_PrEPOralPlusCon,
RN_PrEPInject1Mo, RN_PrEPInject2Mo, RN_PrEPInject6Mo,
RN_PrEPRing, RN_PrEPbNABs, RN_PrEPImplant, RN_PrEP_PEP, RN_Vaccines, RN_FemalesSTITx, RN_ReduceInjects]
RN_NotUsedWhenGoalsAndRNActive = [RN_MCInfant, RN_FemalesSTITx, RN_ReduceInjects]

# ART Selection constant #
RN_NumOrPercent       = 0
RN_CD4Category        = 1

# Vaccine sheets #
RN_Efficacy          = 1
RN_Infectiousness    = 2
RN_Progression       = 3
RN_Duration          = 4
RN_Type              = 5

RN_Single            = 0
RN_Diff              = 1

RN_OneMSM            = 1
RN_FourMSM           = 4

# Type of vaccine #
RN_TakeAction        = 1
RN_DegreeAction      = 2

#Vaccines Behavioral Effects#
RN_AmongVacc         = 1
RN_AmongAdults       = 2

#Vaccination Status#
RN_AllVacc            = 0
RN_UnV                = 1
RN_Take               = 2
RN_Partial            = 3
RN_NoProt             = 4

# Vaccines Males, PrEP Males and Females #
RN_AllRisk       = 0
RN_None          = 1
RN_LRH           = 2
RN_MRH           = 3
RN_HRH           = 4
RN_IDU           = 5
RN_MSM           = 6
RN_MSMLR         = 7
RN_MSMMR         = 8
RN_MSMHR         = 9
RN_MSMIDU        = 10

# Vaccines and secnario generator Females #
RN_AllRisk_F     = 11
RN_None_F        = 12
RN_LRH_F         = 13
RN_MRH_F         = 14
RN_HRH_F         = 15
RN_IDU_F         = 16
RN_MSM_F         = 17

# Effectiveness Constants #
RN_Effectiveness  = 1
RN_Adherence      = 2
RN_Substitution   = 3
RN_DurationMonths = 4

RN_MethodMixDistanceFromEditor = 60

# Help constants #
RN_Help_Configuration         = 'Configuration_tutorial_RN'
RN_Help_PopSizeGenPop         = 'General_population_Population_Sizes'
RN_Help_PopSizeMARPop         = 'Most_at_risk_populations_Population_Sizes'
RN_Help_PopSizeMedServ        = 'Medical_services_Population_Sizes'
RN_Help_PopSizeMaleCircum     = 'Male_circumcision_Population_Sizes'
RN_Help_CoverageGenPop        = 'General_population_Coverage'
RN_Help_CoverageMARPop        = 'Most_at_risk_populations_Coverage'
RN_Help_CoverageMedServ       = 'Medical_services_Coverage'
RN_Help_CoverageMaleCircum    = 'Male_circumcision_Coverage'
RN_Help_CoverageTreatment     = 'Treatment_Coverage'
RN_Help_UnitCostsGenPop       = 'General_population_Unit_Costs'
RN_Help_UnitCostsMARPop       = 'Most_at_risk_populations_Unit_Costs'
RN_Help_UnitCostsMedServ      = 'Medical_services_Unit_Costs'
RN_Help_UnitCostsMaleCircum   = 'Male_circumcision_Unit_Costs'
RN_Help_UnitCostsPMTCT        = 'PMTCT_Unit_Costs'
RN_Help_UnitCostsTreatment    = 'Treatment_Unit_Costs'
RN_Help_ProgramSupport        = 'Program_support_RNM'
RN_Help_Mitigation            = 'Mitigation_RNM'
RN_Help_CEA                   = 'Cost-effectiveness-and-optimiz'
RN_Help_Optimize              = 'Optimization'

#***** Constants for the Prevention Technologies Scenario tool ******#
RN_PT_DataFileTitle = 'Prevention Technologies scenario file'
RN_PT_Version1      = 1.0

RN_PT_EXT_WILDCARD  = '*.PT'
RN_PT_EXT           = 'PT'
RN_PT_DOTEXT        = '.PT'

#****************   Scenario Generator (SG) constants   ******************#

# .SG file constants #
RN_SG_DataFileTitle = 'Scenario Generator (RNM) Data File'
RN_SG_Version1       = 1.0
RN_SG_Version2       = 2.0
RN_SG_Version3       = 3.0
RN_SG_FileNumSpace  = 20
RN_SG_FileRDec      = 4

RN_SG_EXT_WILDCARD = '*.SGRN'
RN_SG_EXT          = 'SGRN'
RN_SG_DOTEXT       = '.SGRN'

# Constants for the CSV file that the user can read data in from. #
RN_SG_CSVFileVersion = 'RNM Scenario Generator CSV - Version 1'

# Minimum year that the user can enter as the base year in the SG form. #
RN_SG_MinBaseYear = 2008

#   Abbreviations used in the constants below:
#
#       MSM = Men who have sex with men
#       LRH = Low risk heterosexual
#       MRH = Medium risk heterosexual
#       HRH = High risk heterosexual
#       LR = Low risk
#       MR = Medium risk
#       HR = High risk
#       CSRG = Coverage by sex and risk group
#       NSA = Not sexually active
#       IDU = Injecting drug user
#       F = Female
#       M = Male
#

# Intervention current IDs. #
# General population #
RN_SG_ComMob                 = 1
RN_SG_MassMedia              = 2
RN_SG_VCT                    = 3
RN_SG_Condom                 = 4
RN_SG_PrimaryTeachers        = 5
RN_SG_SecondaryTeachers      = 6
RN_SG_OutOfSchoolYouth       = 7
RN_SG_CashTransfers          = 8
RN_SG_WorkplaceSTI           = 9
# Most at risk populations #
RN_SG_FSW                    = 10
RN_SG_MSW                    = 11
RN_SG_MSMOutreach            = 12
RN_SG_MSMLub                 = 13
RN_SG_IDUHarmRed             = 14
RN_SG_IDUCandT               = 15
RN_SG_IDUOutreach            = 16
RN_SG_IDUNSEP                = 17
RN_SG_IDUDrugSub             = 18
# Medical services #
RN_SG_MalesSTITx             = 19
RN_SG_FemalesSTITx           = 20
RN_SG_BloodSafety            = 21
RN_SG_PEP                    = 22
RN_SG_ADSyringes             = 23
RN_SG_ReduceInjects          = 24
RN_SG_UniversalPrec          = 25
# Male circumcision #
RN_SG_MC_15_49               = 26
# PrEP Coverage Male#
RN_SG_PrEP_M_LRH             = 27
RN_SG_PrEP_M_MRH             = 28
RN_SG_PrEP_M_HRH             = 29
RN_SG_PrEP_M_IDU             = 30
RN_SG_PrEP_M_MSM             = 31
RN_SG_PrEP_M_MSM_LR          = 32
RN_SG_PrEP_M_MSM_MR          = 33
RN_SG_PrEP_M_MSM_HR          = 34
RN_SG_PrEP_M_MSM_IDU         = 35
# PrEP Coverage Female#
RN_SG_PrEP_F_LRH             = 36
RN_SG_PrEP_F_MRH             = 37
RN_SG_PrEP_F_HRH             = 38
RN_SG_PrEP_F_IDU             = 39
# PrEP Efficacy #
RN_SG_PrEP_Eff_Oral          = 40
RN_SG_PrEP_Eff_Inject        = 41
RN_SG_PrEP_Eff_Gel           = 42
RN_SG_PrEP_Eff_Ring          = 43
#PrEP Adherence #
RN_SG_PrEP_Adh_Oral          = 44
RN_SG_PrEP_Adh_Inject        = 45
RN_SG_PrEP_Adh_Gel           = 46
RN_SG_PrEP_Adh_Ring          = 47
# Treatment - ART by number or percent #
RN_SG_AdultsNeedRecART_M     = 48
RN_SG_AdultsNeedRecART_F     = 49
RN_SG_MigrLine1To2           = 50
# Treatment - CD4 threshold #
RN_SG_CD4ThreshElig          = 51
# Treatment - Children #
RN_SG_ChildCotrim            = 52
RN_SG_ChildART               = 53
# Treatment - ART by CD4 category #
RN_SG_CD4_GT500              = 54
RN_SG_CD4_350_500            = 55
RN_SG_CD4_250_349            = 56
RN_SG_CD4_200_249            = 57
RN_SG_CD4_100_199            = 58
RN_SG_CD4_50_99              = 59
RN_SG_CD4_LT50               = 60
# Populations eligible for treatment #
RN_SG_EligPregnantWomen      = 61
RN_SG_EligTBHIBCoInfected    = 62
RN_SG_EligDiscordantCouples  = 63
RN_SG_EligSexWorkers         = 64
RN_SG_EligMSM                = 65
RN_SG_EligIDU                = 66
RN_SG_EligOtherPopulation    = 67
# PMTCT #
RN_SG_PMTCT_Pre_Single       = 68
RN_SG_PMTCT_Pre_Dual         = 69
RN_SG_PMTCT_Pre_OptA         = 70
RN_SG_PMTCT_Pre_OptB         = 71
RN_SG_PMTCT_Pre_TripBef      = 72
RN_SG_PMTCT_Pre_TripDur      = 73
RN_SG_PMTCT_Post_OptA        = 74
RN_SG_PMTCT_Post_OptB        = 75
# Vaccines #
RN_SG_CovPercVacc            = 76
# Vaccines by sex and risk group #
RN_SG_CSRG_M_NSA             = 77
RN_SG_CSRG_M_LRH             = 78
RN_SG_CSRG_M_MRH             = 79
RN_SG_CSRG_M_HRH             = 80
RN_SG_CSRG_M_IDU             = 81
RN_SG_CSRG_MSM               = 82
RN_SG_CSRG_MSM_LR            = 83
RN_SG_CSRG_MSM_MR            = 84
RN_SG_CSRG_MSM_HR            = 85
RN_SG_CSRG_MSM_IDU           = 86
RN_SG_CSRG_F_NSA             = 87
RN_SG_CSRG_F_LRH             = 88
RN_SG_CSRG_F_MRH             = 89
RN_SG_CSRG_F_HRH             = 90
RN_SG_CSRG_F_IDU             = 91
# Vaccines - Effectiveness #
RN_SG_ReductSuscept          = 92
RN_SG_ReductInfect           = 93
RN_SG_IncProgression         = 94
RN_SG_VaccineDuration        = 95

RN_SG_MaxInterventions       = 95

# SG intervention current ID sets by common setter methods. #
RN_SG_PopulationsSet  = [RN_SG_ComMob, RN_SG_MassMedia, RN_SG_VCT,
RN_SG_Condom, RN_SG_PrimaryTeachers, RN_SG_SecondaryTeachers,
RN_SG_OutOfSchoolYouth, RN_SG_CashTransfers, RN_SG_WorkplaceSTI,
RN_SG_FSW, RN_SG_MSW, RN_SG_MSMOutreach, RN_SG_MSMLub, RN_SG_IDUHarmRed,
RN_IDUCandT, RN_SG_IDUOutreach, RN_SG_IDUNSEP, RN_SG_IDUDrugSub,
RN_SG_MalesSTITx, RN_SG_FemalesSTITx, RN_SG_BloodSafety, RN_SG_PEP,
RN_SG_ADSyringes, RN_SG_ReduceInjects, RN_SG_UniversalPrec]

RN_SG_PrEPSet_M       = [RN_SG_PrEP_M_LRH, RN_SG_PrEP_M_MRH, RN_SG_PrEP_M_HRH,
RN_SG_PrEP_M_IDU, RN_SG_PrEP_M_MSM, RN_SG_PrEP_M_MSM_LR, RN_SG_PrEP_M_MSM_MR,
RN_SG_PrEP_M_MSM_HR, RN_SG_PrEP_M_MSM_IDU]

RN_SG_PrEPSet_F       = [RN_SG_PrEP_F_LRH, RN_SG_PrEP_F_MRH, RN_SG_PrEP_F_HRH, RN_SG_PrEP_F_IDU]

RN_SG_PrEPSet_Eff     = [RN_SG_PrEP_Eff_Oral, RN_SG_PrEP_Eff_Inject, RN_SG_PrEP_Eff_Gel,
RN_SG_PrEP_Eff_Ring]

RN_SG_PrEPSet_Adh     = [RN_SG_PrEP_Adh_Oral, RN_SG_PrEP_Adh_Inject, RN_SG_PrEP_Adh_Gel,
RN_SG_PrEP_Adh_Ring]

RN_SG_CSRG_Set        = [RN_SG_CSRG_M_NSA, RN_SG_CSRG_M_LRH, RN_SG_CSRG_M_MRH,
RN_SG_CSRG_M_HRH, RN_SG_CSRG_M_IDU, RN_SG_CSRG_MSM, RN_SG_CSRG_MSM_LR,
RN_SG_CSRG_MSM_MR, RN_SG_CSRG_MSM_HR, RN_SG_CSRG_MSM_IDU, RN_SG_CSRG_F_NSA,
RN_SG_CSRG_F_LRH, RN_SG_CSRG_F_MRH, RN_SG_CSRG_F_HRH, RN_SG_CSRG_F_IDU]

RN_SG_ParamSet        = [RN_SG_ReductSuscept, RN_SG_ReductInfect, RN_SG_IncProgression,RN_SG_VaccineDuration]

RN_SG_EligPopSet      = [RN_SG_EligPregnantWomen, RN_SG_EligTBHIBCoInfected, RN_SG_EligDiscordantCouples,
RN_SG_EligSexWorkers, RN_SG_EligMSM, RN_SG_EligIDU, RN_SG_EligOtherPopulation]

RN_SG_CD4Set          = [RN_SG_CD4_GT500, RN_SG_CD4_350_500, RN_SG_CD4_250_349, RN_SG_CD4_200_249,
RN_SG_CD4_100_199, RN_SG_CD4_50_99, RN_SG_CD4_LT50]

RN_SG_PMTCTSet_Pre    = [RN_SG_PMTCT_Pre_Single, RN_SG_PMTCT_Pre_Dual, RN_SG_PMTCT_Pre_OptA, RN_SG_PMTCT_Pre_OptB,
RN_SG_PMTCT_Pre_TripBef, RN_SG_PMTCT_Pre_TripDur]

RN_SG_PMTCTSet_Post   = [RN_SG_PMTCT_Post_OptA, RN_SG_PMTCT_Post_OptB]

RN_SG_VacEffSet       = [RN_SG_ReductSuscept, RN_SG_ReductInfect, RN_SG_IncProgression,RN_SG_VaccineDuration]

# Constants for reading and writing EasyRNMData #
RN_FileYearCol                       = 0
RN_CodeCol                             = 0
RN_CountryCol                           = 1
RN_NumFemaleSWCol                       = 2
RN_NumMaleSWCol                         = 3
RN_NumMSMCol                           = 4
RN_NumIDUCol                           = 5
RN_PercOpioidDepCol                     = 6
RN_InjPerYearCol                       = 7
RN_PrimaryGrEnrRateMaleCol             = 8
RN_PrimaryGrEnrRateFemaleCol           = 9
RN_PrimaryPupTeachRatioCol             = 10
RN_SecondaryGrEnrRateMaleCol           = 11
RN_SecondaryGrEnrRateFemaleCol         = 12
RN_SecondaryPupTeachRatioCol           = 13
RN_FreqTeachRetrainingCol               = 14
RN_FormalSectorEmpWorkProgramsCol       = 15
RN_PercSexuallyActive15_49Col           = 16
RN_PercMalesRegPartnerships15_49Col     = 17
RN_PercMalesNonregPartners15_49Col     = 18
RN_NumSexActsCasualPartnersCol         = 19
RN_NumSexActsRegularPartnersCol         = 20
RN_NumCommSexActsFSWCol                 = 21
RN_NumCommSexActsMSWCol                 = 22
RN_CondomWastageCol                     = 23
RN_NumNewSTIsMaleCol                   = 24
RN_NumNewSTIsFemaleCol                 = 25
RN_PercSymptSTIsMaleCol                 = 26
RN_PercSymptSTIsFemaleCol               = 27
RN_BloodUnitsPer1000Col                 = 28
RN_PEPKitsPerMillionCol                 = 29
RN_AvgNumImmunPerChildCol               = 30
RN_AdultInjectionsCol                   = 31
RN_PercUnsafeInjectionsCol             = 32
RN_HospitalBedsPer1000Col               = 33
RN_RapesPer1000Col                     = 34
RN_CovFSWCol                           = 35
RN_CovMSWCol                           = 36
RN_CovMSMCol                           = 37
RN_CovIDUHarmReductionCol               = 38
RN_CovIDUCandTCol                       = 39
RN_CovIDUOutreachCol                   = 40
RN_CovIDUNSEPCol                       = 41
RN_CovIDUDrugSubCol                     = 42
RN_CovCommMobCol                       = 43
RN_CovPrimStudentsCol                   = 44
RN_CovSecStudentsCol                   = 45
RN_CovOutOfSchoolCol                   = 46
RN_CovCashTransfersCol                 = 47
RN_CovWorkForceSTICol                   = 48
RN_CovCasualCondomsCol                 = 49
RN_CovMSMLubCol                         = 50
RN_CovSTIMalesCol                       = 51
RN_CovSTIFemalesCol                     = 52
RN_CovVCTCol                           = 53
RN_CovMassMediaCol                     = 54
RN_CovUnitsBloodTestedCol               = 55
RN_CovPEPNeedMetCol                     = 56
RN_CovUnsafeInjADSyringesCol           = 57
RN_CovReductionInjCol                   = 58
RN_CovHospitalBedsCol                   = 59
RN_CovMalesCircumcisedCol               = 60
RN_CostFSWCol                           = 61
RN_CostMSWCol                           = 62
RN_CostMSMCol                           = 63
RN_CostIDUHarmRedCol                   = 64
RN_CostIDUCandTCol                     = 65
RN_CostIDUOutreachCol                   = 66
RN_CostIDUNSEPCol                       = 67
RN_CostIDUDrugSubCol                   = 68
RN_CostCommMobCol                       = 69
RN_CostPrimaryCol                       = 70
RN_CostSecondCol                       = 71
RN_CostOutOfSchoolCol                   = 72
RN_CostCashTransfersCol                 = 73
RN_CostSTIWorkplaceCol                 = 74
RN_CostCondomPubCol                     = 75
RN_CostSTICol                           = 76
RN_CostVCTCol                           = 77
RN_CostMassMediaCol                     = 78
RN_CostUnitsBloodTestedCol             = 79
RN_CostPEPKitCol                       = 80
RN_CostADSyringeCol                     = 81
RN_CostHospBedCol                       = 82
RN_CostCircumCol                       = 83
RN_CostCD4Col                        = 84
RN_CostVLCol                         = 85
RN_CostEIDCol                        = 86
RN_CostBloodChemCol                  = 87
RN_CostVisitCol                      = 88
RN_CostFLARVCol                      = 89
RN_CostSLARVCol                      = 90
RN_CostTLARVCol                      = 91
RN_PercSecondLineCol                 = 92
RN_PercThirdLineCol                  = 93
RN_EasyRNMData_MaxCol                = 93

# EasyRNMData year for data in the database #
RN_EasyRNMData_Year = 2016

# String constants for tag column headers. Used for EasyRNMData file. #
RN_CodeTag                           = 'Code'
RN_CountryTag                        = 'Country'
RN_NumFemaleSWTag                    = 'NumFemaleSW'
RN_NumMaleSWTag                      = 'NumMaleSW'
RN_NumMSMTag                         = 'NumMSM'
RN_NumIDUTag                         = 'NumIDU'
RN_PercOpioidDepTag                  = 'PercOpioidDep'
RN_InjPerYearTag                     = 'InjPerYear'
RN_PrimaryGrEnrRateToMaleTag         = 'PrimaryGrEnrRateMale'
RN_PrimaryGrEnrRateToFemaleTag       = 'PrimaryGrEnrRateFemale'
RN_PrimaryPupTeachRatioTag           = 'PrimaryPupTeachRatio'
RN_SecondaryGrEnrRateToMaleTag       = 'SecondaryGrEnrRateMale'
RN_SecondaryGrEnrRateToFemaleTag     = 'SecondaryGrEnrRateFemale'
RN_SecondaryPupTeachRatioTag         = 'SecondaryPupTeachRatio'
RN_FreqTeachRetrainingTag            = 'FreqTeachRetraining'
RN_FormalSectorEmpWorkProgramsTag    = 'FormalSectorEmpWorkPrograms'
RN_15to49PercSexuallyActiveTag       = 'PercSexuallyActive15_49'
RN_15to49MalesPercRegPartnershipsTag = 'PercMalesRegPartnerships15_49'
RN_15to49PercMalesNonregPartnersTag  = 'PercMalesNonregPartners15_49'
RN_NumSexActsCasualPartnersTag       = 'NumSexActsCasualPartners'
RN_NumSexActsRegularPartnersTag      = 'NumSexActsRegularPartners'
RN_NumCommSexActsFSWTag              = 'NumCommSexActsFSW'
RN_NumCommSexActsMSWTag              = 'NumCommSexActsMSW'
RN_CondomWastageTag                  = 'CondomWastage'
RN_NumNewSTIsMaleTag                 = 'NumNewSTIsMale'
RN_NumNewSTIsFemaleTag               = 'NumNewSTIsFemale'
RN_PercSymptSTIsMaleTag              = 'PercSymptSTIsMale'
RN_PercSymptSTIsFemaleTag            = 'PercSymptSTIsFemale'
RN_BloodUnitsPerThousTag             = 'BloodUnitsPer1000'
RN_PEPKitsPerMillionTag              = 'PEPKitsPerMillion'
RN_AvgNumImmunPerChildTag            = 'AvgNumImmunPerChild'
RN_AdultInjectionsTag                = 'AdultInjections'
RN_PercUnsafeInjectionsTag           = 'PercUnsafeInjections'
RN_HospitalBedsPerThousTag           = 'HospitalBedsPer1000'
RN_PercAdultMalesCircumcisedTag      = 'PercAdultMalesCircumcised'
RN_RapesPerThousTag                  = 'RapesPer1000'
RN_CovFSWTag                         = 'CovFSW'
RN_CovMSWTag                         = 'CovMSW'
RN_CovMSMTag                         = 'CovMSM'
RN_CovIDUHarmReductionTag            = 'CovIDUHarmReduction'
RN_CovIDUCAndTTag                    = 'CovIDUCandT'
RN_CovIDUOutreachTag                 = 'CovIDUOutreach'
RN_CovIDUNSEPTag                     = 'CovIDUNSEP'
RN_CovIDUDrugSubTag                  = 'CovIDUDrugSub'
RN_CovCommMobTag                     = 'CovCommMob'
RN_CovPrimStudentsTag                = 'CovPrimStudents'
RN_CovSecStudentsTag                 = 'CovSecStudents'
RN_CovOutOfSchoolTag                 = 'CovOutOfSchool'
RN_CovCashTransfersTag               = 'CovCashTransfers'
RN_CovWorkForceSTITag                = 'CovWorkForceSTI'
RN_CovCasualCondomsTag               = 'CovCasualCondoms'
RN_CovMSMLubTag                      = 'CovMSMLub'
RN_CovSTIMalesTag                    = 'CovSTIMales'
RN_CovSTIFemalesTag                  = 'CovSTIFemales'
RN_CovVCTTag                         = 'CovVCT'
RN_CovMassMediaTag                   = 'CovMassMedia'
RN_CovUnitsBloodTestedTag            = 'CovUnitsBloodTested'
RN_CovPEPNeedMetTag                  = 'CovPEPNeedMet'
RN_CovUnsafeInjADSyringesTag         = 'CovUnsafeInjADSyringes'
RN_PercReductionInjTag               = 'CovReductionInj'
RN_CovHospitalBedsTag                = 'CovHospitalBeds'
RN_CovMalesCircumcisedTag            = 'CovMalesCircumcised'
RN_CostFSWTag                        = 'CostFSW'
RN_CostMSWTag                        = 'CostMSW'
RN_CostMSMTag                        = 'CostMSM'
RN_CostIDUHarmRedTag                 = 'CostIDUHarmRed'
RN_CostIDUCAndTTag                   = 'CostIDUCandT'
RN_CostIDUOutreachTag                = 'CostIDUOutreach'
RN_CostIDUNSEPTTag                   = 'CostIDUNSEP'
RN_CostIDUDrugSubTag                 = 'CostIDUDrugSub'
RN_CostCommMobTag                    = 'CostCommMob'
RN_CostPrimaryTag                    = 'CostPrimary'
RN_CostSecondTag                     = 'CostSecond'
RN_CostOutOfSchoolTag                = 'CostOutOfSchool'
RN_CostCashTransfersTag              = 'CostCashTransfers'
RN_CostSTIWorkplaceTag               = 'CostSTIWorkplace'
RN_CostCondomPubTag                  = 'CostCondomPub'
RN_CostSTITag                        = 'CostSTI'
RN_CostVCTTag                        = 'CostVCT'
RN_CostMassMediaTag                  = 'CostMassMedia'
RN_CostUnitsBloodTestedTag           = 'CostUnitsBloodTested'
RN_CostPEPKitTag                     = 'CostPEPKit'
RN_CostADSyringeTag                  = 'CostADSyringe'
RN_CostHospBedTag                    = 'CostHospBed'
RN_CostCircumTag                     = 'CostCircum'
RN_CostCD4Tag                        = 'CostCD4'
RN_CostVLTag                         = 'CostVL'
RN_CostEIDTag                        = 'CostEID'
RN_CostBloodChemTag                  = 'CostBloodChem'
RN_CostVisitTag                      = 'CostVisit'
RN_CostFLARVTag                      = 'CostFLARV'
RN_CostSLARVTag                      = 'CostSLARV'
RN_CostTLARVTag                      = 'CostTLARV'
RN_PercSecondLineTag                 = 'PercSecondLn'
RN_PercThirdLineTag                  = 'PercThirdLine'

#**** Constants for Impact Express data generator ****#
RN_IE_DataFileTitle = 'Impact Express data generator file'

RN_IE_Version1      = 1.0
RN_IE_FileNumSpace  = 10
RN_IE_FileRDec      = 4

RN_IE_DefaultNumInterations  = '500'
RN_IE_DefaultTargetYear      = '2018'
RN_IE_DefaultFinalYearOutput = '2025'

RN_IE_EXT_WILDCARD = '*.IE'
RN_IE_EXT          = 'IE'
RN_IE_CSV_EXT      = '_IE1.csv'

RN_IE_Delimeter = '-1'

RN_IE_YearIncrement = 1

# Coverages used by the IE tool #
RN_IE_ART_M                   = 1
RN_IE_ART_F                   = 2
RN_IE_ART_Child               = 3
RN_IE_PMTCT                   = 4
RN_IE_TB_CaseDet              = 5
RN_IE_Goals_MC15_49           = 6
RN_IE_Goals_Condoms           = 7
RN_IE_Goals_VCT               = 8
RN_IE_Goals_ComMob            = 9
RN_IE_Goals_SexWorkerOutreach = 10
RN_IE_Goals_MSMOutreach       = 11
RN_IE_Goals_IDUOutreach       = 12
RN_IE_MaxCoverages            = 12

RN_IE_PMTCT_None              = 13
RN_IE_PMTCT_Single            = 14
RN_IE_PMTCT_Dual              = 15
RN_IE_PMTCT_OptA              = 16
RN_IE_PMTCT_OptB              = 17
RN_IE_PMTCT_Before            = 18
RN_IE_PMTCT_During            = 19
RN_IE_NumPMTCTConstants       = 7

RN_IE_TB_Noti                 = 20
RN_IE_TB_Inc                  = 21
RN_IE_NumTBConstants          = 2

# Output constants #
RN_IE_NewInfections_Adult_Out     = 1
RN_IE_NewInfections_Child_Out     = 2
RN_IE_AIDSDeaths_Adult_Out        = 3
RN_IE_AIDSDeaths_Child_Out        = 4
RN_IE_NumReceivingART_Adult_Out   = 5
RN_IE_NumReceivingART_Child_Out   = 6
RN_IE_NumReceivingPMTCT_Out       = 7
RN_IE_Males15_49_Out              = 8
RN_IE_Males15_Out                 = 9
RN_IE_QALYs_Out                   = 10
RN_IE_TB_TotalMortality_Out       = 11
RN_IE_TB_Notification_Out         = 12
RN_IE_Condoms_Out                 = 13
RN_IE_VCT_Out                     = 14
RN_IE_ComMob_Out                  = 15
RN_IE_SexWorkerOutreach_Out       = 16
RN_IE_MSMOutreach_Out             = 17
RN_IE_IDUOutreach_Out             = 18
RN_IE_MaxOutputs                  = 18

# Iteration type #
RN_IE_Random      = 0
RN_IE_Ordered     = 1

# Form that is calling the CEA tool #
RN_ToolsForm      = 1
RN_OptimizeForm   = 2

# For Optimize tool #
RN_OP_ART_Male             = 0
RN_OP_ART                  = 1    #this constant is used for Female and BothSexes (for editor and cost)
RN_OP_VMMC                 = 2
RN_OP_CondomPromotion      = 3
RN_OP_SWOutreach           = 4
RN_OP_MSMOutreach          = 5
RN_OP_PWIDOutreach         = 6
RN_OP_PWIDNSEP             = 7
RN_OP_PWIDOST              = 8
RN_OP_PrEPAdolescents      = 9
RN_OP_PrEPSW               = 10
RN_OP_PrEPMSM              = 11
RN_OP_CommunityMobil       = 12
RN_OP_MediaCommunications  = 13
RN_OP_YouthInSchool        = 14
RN_OP_YouthOutOfSchool     = 15
RN_OP_CashTransfers        = 16
RN_OP_MaxOptimize          = 16

# Optimizer Constants #
RN_MinCov                  = 2
RN_MaxCov                  = 3

# Goal options for Optimize tool #
RN_OP_NewInfections = 0
RN_OP_AIDSDeaths    = 1
RN_OP_DALYs         = 2

# Projections for Optimize tool #
RN_OP_MinimumProj     = '_Minimum'
RN_OP_MaximumProj     = '_Maximum'
RN_OP_OptimizedProj   = '_Optimized'

# RNEdFM Glow button constants #
RN_ConfigBtn          = 1
RN_PopSizesBtn        = 2
RN_CoverageBtn        = 3
RN_TreatmentBtn       = 4
RN_UnitCostsBtn       = 5
RN_ProgramSupportBtn  = 6
RN_MitigationBtn      = 7
RN_ResultsBtn         = 8

# Sheets in RNModData file #
RN_EasyRNMData             = 'EasyRNMData'#'EasyRNMData2016'
RN_EasyRNMOldData          = 'EasyRNMOldData'
RN_PreventionTechnologies  = 'PreventionTechnologies'
