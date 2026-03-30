
#  HV_MAX_LINE = 80 #

# Read Write determines size of numbers in file #
HV_FileNumSpace = 20
HV_FileRDec = 5

# Error Messages #
HV_NOERROR           = 0
HV_ERROR             = 1

# Default constants #
HV_Default  = 1
HV_Data     = 2

# Used for CustomEasyData imported from projection #
HV_ImportedProj  = 1

# Space #
HV_Space = '   '

# Special constants #
HV_DataFileTitle     = 'HIV Vaccine data file  - The POLICY Project'
HV_Version10         = 1.0
HV_Version11         = 1.1
HV_Version12         = 1.2
HV_Version13         = 1.3
HV_Version14         = 1.4

# Sex constants #
HV_BothSexes = 0
HV_Male      = 1
HV_Female    = 2

# Indicator Constants #
HV_SEXIND            = 1
HV_SERV_IND          = 2
HV_SINGLE_SERV_IND   = 3
HV_Summary_IND       = 4
HV_DISPLAYVALUES_IND = 5
HV_NO_SCALE_TABLE    = 6
HV_CD4Distribution   = 7
HV_ONLY_ONE_PROJ     = 8
HV_METHODIND         = 9
HV_max_services      = 10

# Display Chart Types #
HV_DispLine2d   = 0
HV_DispBar2d    = 1
HV_DispBar3d    = 2
HV_DispHBar2d   = 3
HV_DispHBar3d   = 4
HV_DispTable    = 5

# Display constants #
HV_Number = 0
HV_Percent = 1

# Time constants #
HV_FIRST_INDEX   = 1
HV_min_year      = 1

# Time step #
HV_TimeStep = 10

# Age Constats #
HV_A15_19  = 1
HV_A20_24  = 2
HV_A25_29  = 3
HV_A30_34  = 4
HV_A35_39  = 5
HV_A40_44  = 6
HV_A45_49  = 7
HV_A50_54  = 8
HV_A55_59  = 9
HV_A60_64  = 10

# Impact Matrix constants #
HV_Average        = 0
HV_UpperQuartile  = 1
HV_LowerQuartile  = 2

# Projection constants#
HV_max_proj = 10
GB_FirstProj = 1

# Scale constants #
HV_units             = 1
HV_thousands         = 2
HV_millions          = 3
HV_thousand_millions = 4

HV_Table           = 101
HV_PyramidPer      = 102
HV_PyramidNum      = 103
HV_SummaryTable    = 104
HV_Stacked2D       = 105
HV_Stacked3D       = 106

# Regions #
HV_ALL_REGION         = 0
HV_URBAN              = 1
HV_RURAL              = 2

# Married #
HV_ALL_WOMEN          = 0
HV_MARRIED            = 1
HV_UNMARRIED          = 2

# Condom Use constants #
HV_UseLogisticsCurve     = 0
HV_UseInterpolatedValues = 1

# Should be set to the Max of either Edit Services or Edit Sectors or PrEP Methods#
#  HV_max_DisAg          = 23

# Variable Parameters #
HV_YEAR_DIM          = 1
HV_ALL_SERVICES      = 0

HV_MAX_EDIT_SEC      = 13
HV_MAXSEC            = 14
HV_ModelFittingSec   = 1
HV_PopSec            = 2
HV_NewInfectionsSec  = 3
HV_HIVPosSec         = 4
HV_ART               = 5
HV_DeathsSec         = 6
HV_VaccsSec          = 7
HV_PrEPSec           = 8
HV_BenefitsSec       = 9
HV_CostSec           = 10
HV_SummarySec        = 11
HV_GoalsVsAIMSec     = 12
HV_MultiplierSec     = 13
HV_InputsSec         = 14

#Indicators#
HV_cmNewInfections          = 1
HV_cmNumHIVPos              = 2
HV_cmAIDSDeaths             = 3
HV_cmNumVaccs               = 4
HV_cmNumVaccinated          = 5
HV_cmIncidence              = 6
HV_cmPrevalence             = 7
HV_cmPrevRG                 = 8
HV_cmNewInfectionsRG        = 9
HV_cmAIDSDeathsRG           = 10
HV_cmPopbyRG                = 11
HV_cmHIVPosRG               = 12
HV_cmModelFitting           = 13
HV_cmHIV                    = 14
HV_cmIA                     = 15
HV_cmCumIA                  = 16
HV_cmDA                     = 17
HV_cmCumDA                  = 18
HV_cmTotalCost              = 19
HV_cmCumCostIA              = 20
HV_cmCumCostDA              = 21
HV_cmTotalCostByInt         = 22
HV_cmPopAR                  = 23
HV_cmNewInfectionsAR        = 24
HV_cmPrevAR                 = 25
HV_cmHIVPosAR               = 26
HV_cmDistCD4NoART           = 27
HV_cmDistCD4ART             = 28
HV_cmAIDSDeathsAR           = 29
HV_cmSummary                = 30
HV_cmNumVaccsAR             = 31
HV_cmNumVaccsRG             = 32
HV_cmNumART                 = 33
HV_cmTotalCosts2            = 34
HV_cmAIDSDeathsART          = 35
HV_cmARTCoveragebyRG        = 36
HV_cmTotalARTCoverageAR     = 37
HV_cmARTCoverageCD4         = 38
HV_cmNewlyOnARTCD4          = 39
HV_cmNewlyOnARTTotal        = 40
HV_cmNewlyEligibleARTCD4    = 41
HV_cmNewlyEligibleARTTotal  = 42
HV_cmIncidenceRG            = 43
HV_cmIncidenceAR            = 44
# GVA = Goals vs AIM.  These indicators are only visible in developer's mode #
HV_cmGVAIncidence           = 45
HV_cmGVAPrevalence          = 46
HV_cmGVAHIVPopulation       = 47
HV_cmGVATotalPopulation     = 48
HV_cmGVANewInfections       = 49
HV_cmGVANumReceivingART     = 50
HV_cmGVAAIDSDeaths          = 51
# Multiplier is only visible in developer's mode #
HV_cmMultiplier             = 52
HV_cmMultiplierbyRG         = 53
HV_cmMultiplierAR           = 54
# for PrEP #
HV_cmTotalPrEP              = 55
HV_cmPrEPSingleMethod       = 56
HV_cmPrEPAllMethods         = 57
HV_cmPrEPRG                 = 58
HV_cmPrEPAR                 = 59
# Editor input indicators for Extract #
HV_exConfiguration          = 60
HV_exEpidemiology           = 61
HV_exBehavior               = 62
HV_exImpactMatrix           = 63

HV_MAXIND                   = 63

HV_OneMSMRiskGroup   = 0
HV_FourMSMRiskGroups = 1

# Condom use constants for logistics curve #
 # Logistics curve parameters #
HV_CU_A = 1         #Initial value
HV_CU_K = 2         #Final value
HV_CU_B = 3         #Growth rate
HV_CU_V = 4         #Growth location
HV_CU_M = 5         #Years to final value
HV_CU_Q = 6

# These female risk groups are used when AllRisk and MSM are needed for females.
#    MSM is usually used to round out the loop #
#  HV_AllRisk_F3      = 11
#  HV_None_F3         = 12
#  HV_LRH_F3          = 13
#  HV_MRH_F3          = 14
#  HV_HRH_F3          = 15
#  HV_IDU_F3          = 16
#  HV_MSM_F3          = 17

# These female risk groups are used when AllRisk and MSM are not needed for females
#   and HV_MSMIDU_M IS NOT part of the male risk groups #
#  HV_None_F1         = 10
#  HV_LRH_F1          = 11
#  HV_MRH_F1          = 12
#  HV_HRH_F1          = 13
#  HV_IDU_F1          = 14

# These female risk groups are used when AllRisk and MSM are not needed for females
#   and HV_MSMIDU_M IS part of the male risk groups #
#  HV_None_F2          = 11
#  HV_LRH_F2           = 12
#  HV_MRH_F2           = 13
#  HV_HRH_F2           = 14
#  HV_IDU_F2           = 15

# These risk groups are used when there is no differentiation between males and females. They
#   are also used where there are only males or part of the loop dedicated to males. #
HV_AllRisk         = 0
HV_None            = 1
HV_LRH             = 2
HV_MRH             = 3
HV_HRH             = 4
HV_IDU             = 5
HV_MSM             = 6
HV_MSMLR           = 7
HV_MSMMR           = 8
HV_MSMHR           = 9
HV_MSMIDU          = 10
HV_Total           = 11   #NOTE: HV_Total IS USED IN CALCULATIONS FOR MALE/FEMALE OFFSET
#  HV_Adults          = 12
#  HV_AllRisk_F3      = 11
HV_None_F3         = 12
HV_LRH_F3          = 13
HV_MRH_F3          = 14
HV_HRH_F3          = 15
HV_IDU_F3          = 16
HV_MSM_F3          = 17

HV_PercPop           = 1
HV_AvgDur            = 2

#Force Of Infection Sheet#
#  HV_Risk_I            = 1
#  HV_Male_I            = 2
#  HV_LRH_M_I           = 3
#  HV_MRH_M_I           = 4
#  HV_HRH_M_I           = 5
#  HV_IDU_M_I           = 6
#  HV_MSM_M_I           = 7
#  HV_Female_I          = 8
#  HV_LRH_F_I           = 9
#  HV_MRH_F_I           = 10
#  HV_HRH_F_I           = 11
#  HV_IDU_F_I           = 12

# Relative Infectiousness Sheet#
HV_PrimaryInf        = 1
HV_Asymptomatic      = 2
HV_SympNoART         = 3
HV_SympART           = 4

HV_Susceptibility    = 1
HV_Infect            = 2

HV_Neg               = 0
HV_Pos               = 1

# Prevalence by risk group Sheet#
HV_Males_P            = 1
HV_NotSexAct_M_P      = 2
HV_LRH_M_P            = 3
HV_MRH_M_P            = 4
HV_HRH_M_P            = 5
HV_IDU_M_P            = 6
HV_MSM_M_P            = 7
HV_MSMLR_M_P          = 8
HV_MSMMR_M_P          = 9
HV_MSMHR_M_P          = 10
HV_MSMIDU_M_P         = 11
HV_Total_M_P          = 12
HV_Females_P          = 13
HV_NotSexAct_F_P      = 14
HV_LRH_F_P            = 15
HV_MRH_F_P            = 16
HV_HRH_F_P            = 17
HV_IDU_F_P            = 18
HV_Total_F_P          = 19
HV_Adults_P           = 20

# MSM constants #
HV_OneMSM_P           = 1
HV_ThreeMSM_P         = 3
HV_FourMSM_P          = 4

#HIV Status#
HV_Negative           = 0
HV_Primary            = 1
HV_CD4_GT500          = 2
HV_CD4_350_500        = 3
HV_CD4_250_349        = 4
HV_CD4_200_249        = 5
HV_CD4_100_199        = 6
HV_CD4_50_99          = 7
HV_CD4_LT50           = 8
HV_CD4_GT500_ART      = 12
HV_CD4_350_500_ART    = 13
HV_CD4_250_349_ART    = 14
HV_CD4_200_249_ART    = 15
HV_CD4_100_199_ART    = 16
HV_CD4_50_99_ART      = 17
HV_CD4_LT50_ART       = 18
HV_AllHIV             = 19


# ART Selection constant #
#  HV_NumOrPercent       = 0
#  HV_CD4Category        = 1

#Progression Periods#
HV_YearsInPrimary       = 1

#Vaccine Start Year#
HV_VaccineStartYear     = 2015

#Initial Pulse#
HV_InitialPulse         = 0.01

# Risk Group Constants #
HV_RGReducCondomNonUse_High         = 1
HV_RGReducCondomNonUse_Med          = 2
HV_RGReducCondomNonUse_Low          = 3
HV_RGReducCondomNonUse_MSM          = 4
HV_RGReducCondomNonUse_IDU          = 5
HV_RGReducCondomNonUse_MSM_High     = 6
HV_RGReducCondomNonUse_MSM_Med      = 7
HV_RGReducCondomNonUse_MSM_Low      = 8
HV_RGReducCondomNonUse_MSM_IDU      = 9
HV_RGReducInNumPartners_High        = 10
HV_RGReducInNumPartners_Med         = 11
HV_RGReducInNumPartners_Low         = 12
HV_RGReducInNumPartners_MSM         = 13
HV_RGReducInNumPartners_IDU         = 14
HV_RGReducInNumPartners_MSM_High    = 15
HV_RGReducInNumPartners_MSM_Med     = 16
HV_RGReducInNumPartners_MSM_Low     = 17
HV_RGReducInNumPartners_MSM_IDU     = 18
HV_RGIncreaseAgeFirstSex            = 19
HV_RGReducUnsafeInjectBehavior      = 20
HV_RGReducNeedleSharing_IDU         = 21
HV_RGReducNeedleSharing_MSM_IDU     = 22
HV_RGReducNumSharingPartners        = 23
HV_MaxRiskGroups                    = 23

# Cost Effectiveness Analysis constants #
HV_MaxTargetYear  = 2500

# Sheets in HVModData file #
HV_EasyGoalsData              = 'EasyGoalsData'

# Help constants #
HV_Help_Configuration         = 'Configuration_for_Goals'
HV_Help_Epidemiology          = 'Epidemiology'
HV_Help_HIVPrevalence         = 'HIV_prevalence'
HV_Help_STIPrevalence         = 'STI_prevalence'
HV_Help_BloodTransfusion      = 'Blood_transfusion'
HV_Help_Behavior              = 'Behavior'
HV_Help_InjectingDrugUser     = 'Injecting_drug_user'
HV_Help_CondomUse             = 'Condom_use'
HV_Help_NumberOfPartners      = 'Number_of_partners'
HV_Help_SexActsPerPartner     = 'Sex_acts_per_partner'
HV_Help_AgeAtFirstSex         = 'Age_at_first_sex'
HV_Help_IncreasedRecruitment  = 'Increased_recruitment'
HV_Help_PercentMarried        = 'Percent_married'
HV_Help_Coverage              = 'Coverage'
HV_Help_ImpactMatrix          = 'Impact_matrix'
HV_Help_MaleCircumcision      = 'Male_circumcision'
HV_Help_PrEP                  = 'PrEP'
HV_Help_ART                   = 'ART'
HV_Help_Vaccines              = 'Vaccines'
HV_Help_FittingTheEpidemic    = 'Fitting_the_epidemic'

HV_DistanceFromEditor = 10

#**** Constants for Goals Express data generator ****#
HV_GE_DataFileTitle = 'Goals Express data generator file'

HV_GE_Version1      = 1.0
HV_GE_FileNumSpace  = 10
HV_GE_FileRDec      = 4

HV_GE_DefaultNumInterations = '500'

HV_GE_EXT_WILDCARD = '*.GE'
HV_GE_EXT          = 'GE'
HV_GE_CSV_EXT      = '_GE1.csv'

HV_GE_Delimeter   = '-1'

HV_GE_FinalYearOutput = 2050
HV_GE_YearIncrement   = 5

# Coverages used by the GE tool #
HV_GE_ART_M             = 1
HV_GE_ART_F             = 2
HV_GE_MC15_49           = 3
HV_GE_Condoms           = 4
HV_GE_MassMedia         = 5
HV_GE_YouthInSchool     = 6
HV_GE_SexWorkerOutreach = 7
HV_GE_MSMOutreach       = 8
HV_GE_IDUOutreach       = 9
HV_GE_MaxCoverages      = 9

# Output constants #
HV_GE_NewInfections_Out     = 1
HV_GE_AIDSDeaths_Out        = 2
HV_GE_NumReceivingART_Out   = 3
HV_GE_Males15_49_Out        = 4
HV_GE_Males15_Out           = 5
HV_GE_Condoms_Out           = 6
HV_GE_MassMedia_Out         = 7
HV_GE_YouthInSchool_Out     = 8
HV_GE_SexWorkerOutreach_Out = 9
HV_GE_MSMOutreach_Out       = 10
HV_GE_IDUOutreach_Out       = 11
HV_GE_MaxOutputs            = 11

# HVEdFM glow button constants #
HV_ConfigBtn        = 1
HV_EpidemiologyBtn  = 2
HV_BehaviorBtn      = 3
HV_CoverageBtn      = 4
HV_ImpactMatrixBtn  = 5
HV_UnitCostsBtn     = 6
HV_ResultsBtn       = 7
HV_FittingBtn       = 8

# Prior distribution indices, used for model fitting #
HV_PriorNormal = 0
HV_PriorGamma  = 1
HV_PriorBeta   = 2

# Fitting parameter indices #
HV_FitTransmitBase         =  0
HV_FitTransmitMtoF         =  1
HV_FitTransmitSTI          =  2
HV_FitTransmitMSM          =  3
HV_FitStageDurPrimary      =  4
HV_FitStageInfPrimary      =  5
HV_FitStageInfSymptomatic  =  6
HV_FitInitialPulse         =  7
HV_FitCoitalFreqLRH        =  8
HV_FitCoitalFreqMRH        =  9
HV_FitCoitalFreqHRH        = 10
HV_FitCoitalFreqMSM        = 11
HV_FitNeedleSharing        = 12
HV_FitSTIGrowthRate        = 13
HV_FitSTIGrowthLocation    = 14
HV_FitSTIYearstoFinalValue = 15
HV_MaxFitParams            = 16

# Size of the table used for fitting. TODO: make this dynamic #
HV_MaxFitData          = 31

# Constants for reading and writing EasyGoalsData #
HV_FileYearCol            = 0
HV_CountryCodeCol         = 0
HV_CountryNameCol         = 1
HV_EpidemiologyCol        = 2
HV_ARTEffectCol           = 15
HV_HIVPrevNoSexMaleCol    = 16
HV_HIVPrevLRHMaleCol      = 97
HV_HIVPrevMRHMaleCol      = 178
HV_HIVPrevHRHMaleCol      = 259
HV_HIVPrevIDUMaleCol      = 340
HV_HIVPrevMSMCol          = 421
HV_HIVPrevTotalMaleCol    = 502
HV_HIVPrevNoSexFemaleCol  = 583
HV_HIVPrevLRHFemaleCol    = 664
HV_HIVPrevMRHFemaleCol    = 745
HV_HIVPrevHRHFemaleCol    = 826
HV_HIVPrevIDUFemaleCol    = 907
HV_HIVPrevTotalFemaleCol  = 988
HV_HIVPrevAdultsCol       = 1069
HV_STIPrevalenceCol       = 1150
HV_BehaviorCol            = 1195
HV_AveDurBehaviorCol      = 1206
HV_IDUMalesCol            = 1213
HV_IDUFemalesCol          = 1294
HV_IDUShareCol            = 1375
HV_CondomUseCol           = 1456
HV_NumPartLRHMaleCol      = 1476
HV_NumPartMRHMaleCol      = 1557
HV_NumPartHRHMaleCol      = 1638
HV_NumPartMSMCol          = 1719
HV_NumPartLRHFemaleCol    = 1800
HV_NumPartMRHFemaleCol    = 1881
HV_NumPartHRHFemaleCol    = 1962
HV_SexActsLRHCol          = 2043
HV_SexActsMRHCol          = 2124
HV_SexActsHRHCol          = 2205
HV_SexActsLMSMCol         = 2286
HV_AgeFirstSexCol         = 2367
HV_IncreasedRecruitCol    = 2369
HV_PercentMarriedCol      = 2375
HV_MaxDatabaseCol         = 2384

# EasyGoalsData tags #
HV_CountryCodeTag         = '<Country Code>'
HV_CountryNameTag         = '<Country Name>'
HV_EpidemiologyTag        = '<Epidemiology>'
HV_ARTEffectTag           = '<ART effect for all t>'
HV_HIVPrevNoSexMaleTag    = '<HIV Prevalence-Not sexually active: Males>'
HV_HIVPrevLRHMaleTag      = '<HIV Prevalence-LRH: Males>'
HV_HIVPrevMRHMaleTag      = '<HIV Prevalence-MRH: Males>'
HV_HIVPrevHRHMaleTag      = '<HIV Prevalence-HRH: Males>'
HV_HIVPrevIDUMaleTag      = '<HIV Prevalence-IDU: Males>'
HV_HIVPrevMSMTag          = '<HIV Prevalence-MSM>'
HV_HIVPrevTotalMaleTag    = '<HIV Prevalence-Total: Males>'
HV_HIVPrevNoSexFemaleTag  = '<HIV Prevalence-Not sexually active: Females>'
HV_HIVPrevLRHFemaleTag    = '<HIV Prevalence-LRH: Females>'
HV_HIVPrevMRHFemaleTag    = '<HIV Prevalence-MRH: Females>'
HV_HIVPrevHRHFemaleTag    = '<HIV Prevalence-HRH: Females>'
HV_HIVPrevIDUFemaleTag    = '<HIV Prevalence-IDU: Females>'
HV_HIVPrevTotalFemaleTag  = '<HIV Prevalence-Total: Females>'
HV_HIVPrevAdultsTag       = '<HIV Prevalence-Adults>'
HV_STIPrevalenceTag       = '<STI Prevalence>'
HV_BehaviorTag            = '<Behavior>'
HV_AveDurBehaviorTag      = '<Average duration of behavior>'
HV_IDUMalesTag            = '<IDU-force of infection: Males>'
HV_IDUFemalesTag          = '<IDU-force of infection: Females>'
HV_IDUShareTag            = '<IDU-Sharing needles>'
HV_CondomUseTag           = '<Condom use>'
HV_NumPartLRHMaleTag      = '<Number of partners LRH Males>'
HV_NumPartMRHMaleTag      = '<Number of partners MRH Males>'
HV_NumPartHRHMaleTag      = '<Number of partners HRH Males>'
HV_NumPartMSMTag          = '<Number of partners MSM>'
HV_NumPartLRHFemaleTag    = '<Number of partners LRH Females>'
HV_NumPartMRHFemaleTag    = '<Number of partners MRH Females>'
HV_NumPartHRHFemaleTag    = '<Number of partners HRH Females>'
HV_SexActsLRHTag          = '<Sex acts per partner LRH>'
HV_SexActsMRHTag          = '<Sex acts per partner MRH>'
HV_SexActsHRHCTag         = '<Sex acts per partner HRH>'
HV_SexActsLMSMTag         = '<Sex acts per partner MSM>'
HV_AgeFirstSexTag         = '<Age ate first sex>'
HV_IncreasedRecruitTag    = '<Increased recruitment>'
HV_PercentMarriedTag      = '<Percent married>'
