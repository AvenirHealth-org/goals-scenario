import numpy as np

from SpectrumCommon.Const.AM.AMTags import (
    AM_AdultAnnRateProgressLowerCD4Tag,
    AM_AdultDistNewInfectionsCD4Tag,
    AM_AdultMortByCD4NoARTTag,
    AM_AdultMortByCD4WithART0to6Tag,
    AM_AdultMortByCD4WithART7to12Tag,
    AM_AdultMortByCD4WithARTGT12Tag,
    AM_AdultNonAIDSExcessMortTag,
    AM_AgeHIVChildOnTreatmentTag,
    AM_AIDSDeathsARTSingleAgeTag,
    AM_AIDSDeathsByAgeTag,
    AM_AIDSDeathsNoARTSingleAgeTag,
    AM_ARVRegimenTag,
    AM_CD4Distribution15_49Tag,
    AM_CD4DistributionChildTag,
    AM_CD4DistributionTag,
    AM_CD4ThreshHoldAdultsTag,
    AM_CD4ThreshHoldTag,
    AM_ChAged14ByCD4CatTag,
    AM_ChildAnnRateProgressLowerCD4Tag,
    AM_ChildARTByAgeGroupPerNumTag,
    AM_ChildARTDistTag,
    AM_ChildCTXNeed1To4Tag,
    AM_ChildDistNewInfectionsCD4Tag,
    AM_ChildMortalityRatesTag,
    AM_ChildMortByCD4NoARTTag,
    AM_ChildMortByCD4WithART0to6PercTag,
    AM_ChildMortByCD4WithART0to6Tag,
    AM_ChildMortByCD4WithART7to12PercTag,
    AM_ChildMortByCD4WithART7to12Tag,
    AM_ChildMortByCD4WithARTGT12PercTag,
    AM_ChildMortByCD4WithARTGT12Tag,
    AM_ChildNeedCotrimTag,
    AM_ChildNeedPMTCTTag,
    AM_ChildOnCotrimTag,
    AM_ChildOnPMTCTTag,
    AM_ChildTreatInputsTag,
    AM_DistOfHIVTag,
    AM_EffectTreatChildTag,
    AM_EPPPopulationAgesTag,
    AM_FertCD4DiscountTag,
    AM_FRRbyLocationTag,
    AM_HAARTBySexPerNumTag,
    AM_HAARTBySexTag,
    AM_HIVBySingleAgeTag,
    AM_HIVMigrantsBySingleAgeTag,
    AM_HIVPosBFWomen3MonthsTag,
    AM_HIVPosBFWomen12MonthsTag,
    AM_HIVPregWomenTag,
    AM_HIVSexRatioTag,
    AM_HIVTFRTag,
    AM_IncidenceByFitTag,
    AM_IncidenceOptionsTag,
    AM_InfantFeedingOptionsTag,
    AM_MortalityRatesMultiplierTag,
    AM_MortalityRatesTag,
    AM_MTCTRate6WksTag,
    AM_NeedARTTag,
    AM_NewARTPatAllocTag,
    AM_NewInfantInfectionsTag,
    AM_NewInfectionsBySingleAgeTag,
    AM_NewlyStartingARTTag,
    AM_NonAIDSExcessDeathsSingleAgeTag,
    AM_NosocomialInfectionsByAgeTag,
    AM_OnARTBySingleAgeTag,
    AM_PatientsReallocatedTag,
    AM_PercentARTDeliveryTag,
    AM_PercInterruptedChildTag,
    AM_PercInterruptedTag,
    AM_PerinatalTransmissionTag,
    AM_PMTCTEffRegTag,
    AM_PopAdjAmountTag,
    AM_PopAdjTag,
    AM_PregTermAbortionPerNumTag,
    AM_PregTermAbortionTag,
    AM_RatioWomenOnARTTag,
    AM_ResMTCTBySourceTag,
    AM_ResOnARTgt1Yr15PlusTag,
    AM_ResOnARTlt1Yr15PlusTag,
    AM_TransEffAssumpTag,
)
from SpectrumCommon.Const.DP.DPConst import (
    DP_A0,
    DP_A14,
    DP_CD4_15_24,
    DP_CD4_25_34,
    DP_CD4_35_44,
    DP_CD4_45_54,
    DP_CD4_50_99,
    DP_CD4_100_199,
    DP_CD4_200_249,
    DP_CD4_250_349,
    DP_CD4_350_500,
    DP_CD4_GT500,
    DP_CD4_LT50,
    DP_A0t2,
    DP_A1t2,
    DP_A3t4,
    DP_A5t9,
    DP_A5t14,
    DP_A10t14,
    DP_AdvOpt_ART_ExpMort,
    DP_Age12to35Mths,
    DP_Age35to59Mths,
    DP_AgeGT5Years,
    DP_AgeLT11Mths,
    DP_AnnDropPostnatalProph,
    DP_ART0_12MthsBF,
    DP_ARTGT12MthsBF,
    DP_ARTStartDurPreg,
    DP_ARTStartDurPreg_Late,
    DP_ARTStartPrePreg,
    DP_BreastfeedingGE350,
    DP_BreastfeedingLT350,
    DP_CD4_0t4,
    DP_CD4_5t14,
    DP_CD4_Ped_200_349,
    DP_CD4_Ped_350_499,
    DP_CD4_Ped_500_749,
    DP_CD4_Ped_750_999,
    DP_CD4_Ped_GT1000,
    DP_CD4_Ped_LT200,
    DP_CD4_Per_5_10,
    DP_CD4_Per_11_15,
    DP_CD4_Per_16_20,
    DP_CD4_Per_21_25,
    DP_CD4_Per_26_30,
    DP_CD4_Per_GT30,
    DP_CD4_Per_LT5,
    DP_ChildEffNoART,
    DP_ChildEffWithART,
    DP_D_ARTlt6m,
    DP_Data,
    DP_DualARV,
    DP_EPP_15t49,
    DP_InPMTCT,
    DP_MortRates_GT12Mo,
    DP_MortRates_LT12Mo,
    DP_NoProphExistInfCD4GT350,
    DP_NoProphExistInfCD4LT200,
    DP_NoProphExistInfCD4200_350,
    DP_NoProphIncidentInf,
    DP_NotInPMTCT,
    DP_NoTreat,
    DP_Number,
    DP_NumFertileAges,
    DP_OnART,
    DP_OnARTAtDelivery,
    DP_OptA,
    DP_OptB,
    DP_OptionA,
    DP_OptionB,
    DP_P_Perinatal,
    DP_Percent,
    DP_PerChildHIVPosCot,
    DP_PerChildHIVRecART,
    DP_PerChildHIVRecART0_4,
    DP_PerChildHIVRecART10_14,
    DP_Perinatal,
    DP_PrenatalProphylaxis,
    DP_SingleDoseNev,
    DP_SingleDoseNevir,
    DP_StartingARTAtDelivery,
    DP_TotalTreat,
    DP_TripleARTBefPreg,
    DP_TripleARTDurPreg,
    DP_TripleARTDurPreg_Late,
    DP_WHO2006DualARV,
    MTCT_Ind_ARVBeforeBF,
    MTCT_Ind_ARVBeforePerinatal,
    MTCT_Ind_ARVDuringBF,
    MTCT_Ind_ARVDuringDropoutChildInf,
    MTCT_Ind_ARVDuringPerinatal,
    MTCT_Ind_ARVLateBF,
    MTCT_Ind_ARVLatePerinatal,
    MTCT_Ind_DroppedARTDurBF,
    MTCT_Ind_IncidentBF,
    MTCT_Ind_IncidentPerinatal,
    MTCT_Ind_NoARVBF,
    MTCT_Ind_NoARVPerinatal,
    MTCT_Ind_NumWomen_ARVBeforeDropout,
    MTCT_Ind_NumWomen_ARVBeforePreg,
    MTCT_Ind_NumWomen_ARVDuringDropout,
    MTCT_Ind_NumWomen_ARVDuringPreg,
    MTCT_Ind_NumWomen_ARVLate,
    MTCT_Ind_NumWomen_IncidentPerinatal,
    MTCT_Ind_NumWomen_NoARV,
    PMTCT_NewChildInfections,
    PMTCT_NumberOfWomen,
    PMTCT_TransmissionRate,
)
from SpectrumCommon.Const.DP.DPTags import (
    DP_ASFRTag,
    DP_BigPopTag,
    DP_BirthsTag,
    DP_DeathsByAgeTag,
    DP_MigrAgeDistTag,
    DP_MigrRateTag,
    DP_SurvRateTag,
    DP_TFRTag,
)
from SpectrumCommon.Const.GB.GBConst import (
    GB_A0_4,
    GB_A15_19,
    GB_A45_49,
    GB_MAX_AGE,
    GB_AllAges,
    GB_BothSexes,
    GB_Female,
    GB_Male,
    GB_MaxSingleAges,
    GB_NumSexes,
)
from SpectrumCommon.Const.PJ.PJNTags import PJN_FinalYearTag, PJN_FirstYearTag
from SpectrumCommon.Util.DP.DPUtil import Calc_Single_Ages, getSexBirthRatioPercent

Modvars = dict[str, int | float | bool | np.ndarray | dict]

# Lepafrog runs with single-ages, use this to transfer from spectrum stored HIV age group to
# single year ages. Each item represents an index for single-year from 15 to 80+
transf_cd4_ag = [
    DP_CD4_15_24,
    DP_CD4_15_24,
    DP_CD4_15_24,
    DP_CD4_15_24,
    DP_CD4_15_24,
    DP_CD4_15_24,
    DP_CD4_15_24,
    DP_CD4_15_24,
    DP_CD4_15_24,
    DP_CD4_15_24,
    DP_CD4_25_34,
    DP_CD4_25_34,
    DP_CD4_25_34,
    DP_CD4_25_34,
    DP_CD4_25_34,
    DP_CD4_25_34,
    DP_CD4_25_34,
    DP_CD4_25_34,
    DP_CD4_25_34,
    DP_CD4_25_34,
    DP_CD4_35_44,
    DP_CD4_35_44,
    DP_CD4_35_44,
    DP_CD4_35_44,
    DP_CD4_35_44,
    DP_CD4_35_44,
    DP_CD4_35_44,
    DP_CD4_35_44,
    DP_CD4_35_44,
    DP_CD4_35_44,
    DP_CD4_45_54,
    DP_CD4_45_54,
    DP_CD4_45_54,
    DP_CD4_45_54,
    DP_CD4_45_54,
    DP_CD4_45_54,
    DP_CD4_45_54,
    DP_CD4_45_54,
    DP_CD4_45_54,
    DP_CD4_45_54,
    DP_CD4_45_54,
    DP_CD4_45_54,
    DP_CD4_45_54,
    DP_CD4_45_54,
    DP_CD4_45_54,
    DP_CD4_45_54,
    DP_CD4_45_54,
    DP_CD4_45_54,
    DP_CD4_45_54,
    DP_CD4_45_54,
    DP_CD4_45_54,
    DP_CD4_45_54,
    DP_CD4_45_54,
    DP_CD4_45_54,
    DP_CD4_45_54,
    DP_CD4_45_54,
    DP_CD4_45_54,
    DP_CD4_45_54,
    DP_CD4_45_54,
    DP_CD4_45_54,
    DP_CD4_45_54,
    DP_CD4_45_54,
    DP_CD4_45_54,
    DP_CD4_45_54,
    DP_CD4_45_54,
    DP_CD4_45_54,
]
transf_cd4_ds = [
    DP_CD4_GT500,
    DP_CD4_350_500,
    DP_CD4_250_349,
    DP_CD4_200_249,
    DP_CD4_100_199,
    DP_CD4_50_99,
    DP_CD4_LT50,
]

# Internal leapfrog source indices for MTCT (from Leapfrog.pas)
_BPLUS_BEFORE = 4
_BPLUS_BEFORE_DROPOUT = 9
_BPLUS_EARLY = 5
_BPLUS_DURING_DROPOUT = 10
_BPLUS_LATE = 6
_NO_ART = 7
_MAT_SERO = 8
# VT timing dimension indices in mtct_by_source arrays
_VT_PERINATAL = 0  # perinatal
_VT_BF_FIRST = 1  # VT_BF_00_05 (first BF duration)
_VT_BF_LAST = 5  # exclusive end for BF sum (VT_BF_00_05..VT_BF_24_35 = indices 1..4)

# Delphi MTCTMappingsWomen — (modvar_source_idx, leapfrog_source_idx).
_MTCT_MAPPINGS_WOMEN = [
    (MTCT_Ind_NumWomen_ARVBeforePreg, _BPLUS_BEFORE),
    (MTCT_Ind_NumWomen_ARVBeforeDropout, _BPLUS_BEFORE_DROPOUT),
    (MTCT_Ind_NumWomen_ARVDuringPreg, _BPLUS_EARLY),
    (MTCT_Ind_NumWomen_ARVDuringDropout, _BPLUS_DURING_DROPOUT),
    (MTCT_Ind_NumWomen_ARVLate, _BPLUS_LATE),
    (MTCT_Ind_NumWomen_NoARV, _NO_ART),
    (MTCT_Ind_NumWomen_IncidentPerinatal, _MAT_SERO),
]
_MTCT_MAPPINGS_PERINATAL = [
    (MTCT_Ind_ARVBeforePerinatal, _BPLUS_BEFORE),
    (MTCT_Ind_ARVDuringPerinatal, _BPLUS_EARLY),
    (MTCT_Ind_ARVDuringDropoutChildInf, _BPLUS_DURING_DROPOUT),
    (MTCT_Ind_ARVLatePerinatal, _BPLUS_LATE),
    (MTCT_Ind_NoARVPerinatal, _NO_ART),
    (MTCT_Ind_IncidentPerinatal, _MAT_SERO),
]
_MTCT_MAPPINGS_BF = [
    (MTCT_Ind_ARVBeforeBF, _BPLUS_BEFORE),
    (MTCT_Ind_ARVDuringBF, _BPLUS_EARLY),
    (MTCT_Ind_DroppedARTDurBF, _BPLUS_DURING_DROPOUT),
    (MTCT_Ind_ARVLateBF, _BPLUS_LATE),
    (MTCT_Ind_NoARVBF, _NO_ART),
    (MTCT_Ind_IncidentBF, _MAT_SERO),
]


def update_modvars_from_state(
    modvars: Modvars, output_state: dict, n_years: int, ss: dict
):
    _map_population(modvars, output_state, n_years, ss)
    _map_hiv_population(modvars, output_state, n_years, ss)
    _map_hiv_infections(modvars, output_state, n_years, ss)
    _map_hiv_migrants(modvars, output_state, n_years, ss)
    _map_hiv_adult_deaths(modvars, output_state, n_years, ss)
    _map_hiv_child_deaths(modvars, output_state, n_years)
    _map_spectrum_excess_deaths(modvars, output_state, n_years, ss)
    _map_ctx_and_pmtct(modvars, output_state, n_years)
    _map_background_deaths(modvars, output_state, n_years, ss)
    _map_on_art_by_age(modvars, output_state, n_years, ss)
    _map_art_duration_adults(modvars, output_state, n_years)
    _map_adult_cd4_distribution(modvars, output_state, n_years, ss)
    _map_child_cd4_distribution(modvars, output_state, n_years, ss)
    _map_cd4_distribution_15_49(modvars, output_state, n_years, ss)
    _map_perinatal_and_infant(modvars, output_state, n_years)
    _map_children_aged14(modvars, output_state, n_years, ss)
    _map_child_ctx_need_1_4(modvars, output_state, n_years)
    _map_need_art(modvars, output_state, n_years, ss)
    _map_dll_internals_to_zero(modvars, n_years)


def _map_population(modvars: Modvars, output_state: dict, n_years: int, ss: dict):
    p_totpop = output_state["p_totpop"]  # (pAG=81, NS=2, T)
    modvars[DP_BigPopTag][GB_Male, : ss["pAG"], :n_years] = p_totpop[:, 0, :]
    modvars[DP_BigPopTag][GB_Female, : ss["pAG"], :n_years] = p_totpop[:, 1, :]
    modvars[DP_BigPopTag][GB_BothSexes, : ss["pAG"], :n_years] = p_totpop[:, 0, :] + p_totpop[:, 1, :]

    births = output_state["births"]  # (T,)
    for t in range(n_years):
        male_ratio = getSexBirthRatioPercent(modvars, GB_Male, t)
        female_ratio = getSexBirthRatioPercent(modvars, GB_Female, t)
        modvars[DP_BirthsTag][GB_BothSexes, GB_AllAges, t] = births[t]
        modvars[DP_BirthsTag][GB_Male, GB_AllAges, t] = births[t] * male_ratio
        modvars[DP_BirthsTag][GB_Female, GB_AllAges, t] = births[t] * female_ratio


def _map_hiv_population(modvars: Modvars, output_state: dict, n_years: int, ss: dict):
    p_hivpop = output_state["p_hivpop"]  # (pAG=81, NS=2, T)
    modvars[AM_HIVBySingleAgeTag][GB_Male, : ss["pAG"], :n_years] = p_hivpop[:, 0, :]
    modvars[AM_HIVBySingleAgeTag][GB_Female, : ss["pAG"], :n_years] = p_hivpop[:, 1, :]
    modvars[AM_HIVBySingleAgeTag][GB_BothSexes, : ss["pAG"], :n_years] = p_hivpop[:, 0, :] + p_hivpop[:, 1, :]


def _map_hiv_infections(modvars: Modvars, output_state: dict, n_years: int, ss: dict):
    infections = output_state["p_infections"]  # (pAG=81, NS=2, T)
    modvars[AM_NewInfectionsBySingleAgeTag][GB_Male, : ss["pAG"], :n_years] = infections[:, 0, :]
    modvars[AM_NewInfectionsBySingleAgeTag][GB_Female, : ss["pAG"], :n_years] = infections[:, 1, :]
    modvars[AM_NewInfectionsBySingleAgeTag][GB_BothSexes, : ss["pAG"], :n_years] = (
        infections[:, 0, :] + infections[:, 1, :]
    )


def _map_hiv_migrants(modvars: Modvars, output_state: dict, n_years: int, ss: dict):
    hiv_migr = output_state["p_net_migration_hivpop"]  # (pAG=81, NS=2, T)
    modvars[AM_HIVMigrantsBySingleAgeTag][GB_Male, : ss["pAG"], :n_years] = hiv_migr[:, 0, :]
    modvars[AM_HIVMigrantsBySingleAgeTag][GB_Female, : ss["pAG"], :n_years] = hiv_migr[:, 1, :]
    modvars[AM_HIVMigrantsBySingleAgeTag][GB_BothSexes, : ss["pAG"], :n_years] = hiv_migr[:, 0, :] + hiv_migr[:, 1, :]


def _map_hiv_adult_deaths(modvars: Modvars, output_state: dict, n_years: int, ss: dict):
    # Total AIDS deaths by single age (all ages 0-80)
    hiv_deaths = output_state["p_hiv_deaths"]  # (pAG=pAG=81, NS=2, T)
    modvars[AM_AIDSDeathsByAgeTag][GB_Male, : ss["pAG"], :n_years] = hiv_deaths[:, 0, :]
    modvars[AM_AIDSDeathsByAgeTag][GB_Female, : ss["pAG"], :n_years] = hiv_deaths[:, 1, :]
    modvars[AM_AIDSDeathsByAgeTag][GB_BothSexes, : ss["pAG"], :n_years] = hiv_deaths[:, 0, :] + hiv_deaths[:, 1, :]

    # AIDS deaths no ART — adults only (ages p_idx_hiv_first_adult..80, hAG=66 single ages)
    # h_hiv_deaths_no_art: (hDS=7, hAG=66, NS=2, T) → sum over CD4
    no_art = output_state["h_hiv_deaths_no_art"].sum(axis=0)  # (66, 2, T)
    modvars[AM_AIDSDeathsNoARTSingleAgeTag][GB_Male, ss["p_idx_hiv_first_adult"] : ss["pAG"], :n_years] = no_art[
        :, 0, :
    ]
    modvars[AM_AIDSDeathsNoARTSingleAgeTag][GB_Female, ss["p_idx_hiv_first_adult"] : ss["pAG"], :n_years] = no_art[
        :, 1, :
    ]
    modvars[AM_AIDSDeathsNoARTSingleAgeTag][GB_BothSexes, ss["p_idx_hiv_first_adult"] : ss["pAG"], :n_years] = (
        no_art[:, 0, :] + no_art[:, 1, :]
    )

    # AIDS deaths on ART — adults only
    # h_hiv_deaths_art: (hTS=3, hDS=7, hAG=66, NS=2, T) → sum over ART duration and CD4
    on_art = output_state["h_hiv_deaths_art"].sum(axis=(0, 1))  # (66, 2, T)
    modvars[AM_AIDSDeathsARTSingleAgeTag][GB_Male, ss["p_idx_hiv_first_adult"] : ss["pAG"], :n_years] = on_art[:, 0, :]
    modvars[AM_AIDSDeathsARTSingleAgeTag][GB_Female, ss["p_idx_hiv_first_adult"] : ss["pAG"], :n_years] = on_art[
        :, 1, :
    ]
    modvars[AM_AIDSDeathsARTSingleAgeTag][GB_BothSexes, ss["p_idx_hiv_first_adult"] : ss["pAG"], :n_years] = (
        on_art[:, 0, :] + on_art[:, 1, :]
    )


def _map_hiv_child_deaths(modvars: Modvars, output_state: dict, n_years: int):
    # hc1: single ages 0-4 (hc1AG=5), hc2: single ages 5-14 (hc2AG=10)

    # hc1_noart_aids_deaths: (hc1DS=7, hcTT=4, hc1AG=5, NS=2, T) → sum over CD4 and transmission type
    hc1_noart = output_state["hc1_noart_aids_deaths"].sum(axis=(0, 1))  # (5, 2, T)
    modvars[AM_AIDSDeathsNoARTSingleAgeTag][GB_Male, 0:5, :n_years] = hc1_noart[:, 0, :]
    modvars[AM_AIDSDeathsNoARTSingleAgeTag][GB_Female, 0:5, :n_years] = hc1_noart[:, 1, :]
    modvars[AM_AIDSDeathsNoARTSingleAgeTag][GB_BothSexes, 0:5, :n_years] = hc1_noart[:, 0, :] + hc1_noart[:, 1, :]

    # hc2_noart_aids_deaths: (hc2DS=6, hcTT=4, hc2AG=10, NS=2, T)
    hc2_noart = output_state["hc2_noart_aids_deaths"].sum(axis=(0, 1))  # (10, 2, T)
    modvars[AM_AIDSDeathsNoARTSingleAgeTag][GB_Male, 5:15, :n_years] = hc2_noart[:, 0, :]
    modvars[AM_AIDSDeathsNoARTSingleAgeTag][GB_Female, 5:15, :n_years] = hc2_noart[:, 1, :]
    modvars[AM_AIDSDeathsNoARTSingleAgeTag][GB_BothSexes, 5:15, :n_years] = hc2_noart[:, 0, :] + hc2_noart[:, 1, :]

    # hc1_art_aids_deaths: (hTS=3, hc1DS=7, hc1AG=5, NS=2, T) → sum over ART duration and CD4
    hc1_art = output_state["hc1_art_aids_deaths"].sum(axis=(0, 1))  # (5, 2, T)
    modvars[AM_AIDSDeathsARTSingleAgeTag][GB_Male, 0:5, :n_years] = hc1_art[:, 0, :]
    modvars[AM_AIDSDeathsARTSingleAgeTag][GB_Female, 0:5, :n_years] = hc1_art[:, 1, :]
    modvars[AM_AIDSDeathsARTSingleAgeTag][GB_BothSexes, 0:5, :n_years] = hc1_art[:, 0, :] + hc1_art[:, 1, :]

    # hc2_art_aids_deaths: (hTS=3, hc2DS=6, hc2AG=10, NS=2, T)
    hc2_art = output_state["hc2_art_aids_deaths"].sum(axis=(0, 1))  # (10, 2, T)
    modvars[AM_AIDSDeathsARTSingleAgeTag][GB_Male, 5:15, :n_years] = hc2_art[:, 0, :]
    modvars[AM_AIDSDeathsARTSingleAgeTag][GB_Female, 5:15, :n_years] = hc2_art[:, 1, :]
    modvars[AM_AIDSDeathsARTSingleAgeTag][GB_BothSexes, 5:15, :n_years] = hc2_art[:, 0, :] + hc2_art[:, 1, :]


def _map_spectrum_excess_deaths(modvars: Modvars, output_state: dict, n_years: int, ss: dict):
    # p_excess_deaths_nonaids_no_art / _on_art: (pAG=81, NS=2, T)
    # AM_NonAIDSExcessDeathsSingleAgeTag: (ART_state, sex, age, T)
    #   ART_state: 0=sum, DP_NoTreat=1, DP_OnART=2
    no_art = output_state["p_excess_deaths_nonaids_no_art"]
    on_art = output_state["p_excess_deaths_nonaids_on_art"]

    modvars[AM_NonAIDSExcessDeathsSingleAgeTag][DP_NoTreat, GB_Male, : ss["pAG"], :n_years] = no_art[:, 0, :]
    modvars[AM_NonAIDSExcessDeathsSingleAgeTag][DP_NoTreat, GB_Female, : ss["pAG"], :n_years] = no_art[:, 1, :]
    modvars[AM_NonAIDSExcessDeathsSingleAgeTag][DP_NoTreat, GB_BothSexes, : ss["pAG"], :n_years] = (
        no_art[:, 0, :] + no_art[:, 1, :]
    )

    modvars[AM_NonAIDSExcessDeathsSingleAgeTag][DP_OnART, GB_Male, : ss["pAG"], :n_years] = on_art[:, 0, :]
    modvars[AM_NonAIDSExcessDeathsSingleAgeTag][DP_OnART, GB_Female, : ss["pAG"], :n_years] = on_art[:, 1, :]
    modvars[AM_NonAIDSExcessDeathsSingleAgeTag][DP_OnART, GB_BothSexes, : ss["pAG"], :n_years] = (
        on_art[:, 0, :] + on_art[:, 1, :]
    )

    # Index 0 = sum of NoTreat + OnART
    sum_excess = no_art + on_art
    modvars[AM_NonAIDSExcessDeathsSingleAgeTag][0, GB_Male, : ss["pAG"], :n_years] = sum_excess[:, 0, :]
    modvars[AM_NonAIDSExcessDeathsSingleAgeTag][0, GB_Female, : ss["pAG"], :n_years] = sum_excess[:, 1, :]
    modvars[AM_NonAIDSExcessDeathsSingleAgeTag][0, GB_BothSexes, : ss["pAG"], :n_years] = (
        sum_excess[:, 0, :] + sum_excess[:, 1, :]
    )


def _map_ctx_and_pmtct(modvars: Modvars, output_state: dict, n_years: int):
    ctx_need = output_state["ctx_need"]  # (T,)
    hiv_births = output_state["hiv_births"]  # (T,)
    hiv_births_mat = output_state["hiv_births_by_mat_age"]  # (35, T), ages 15-49
    mtct_tr = output_state["mtct_by_source_tr"]  # (11, 5, T)
    mtct_hc_inf = output_state["mtct_by_source_hc_infections"]  # (11, 5, T)
    mtct_women = output_state["mtct_by_source_women"]  # (11, T)
    pmtct_cov = output_state["pmtct_coverage_at_delivery"]  # (7, T)

    # Cotrim (CTX) need and use — both-sexes aggregate only (matches Delphi)
    modvars[AM_ChildNeedCotrimTag][GB_BothSexes, :n_years] = ctx_need
    ctx_is_percent = modvars[AM_ChildARTByAgeGroupPerNumTag][DP_PerChildHIVPosCot, :n_years]
    ctx_value = modvars[AM_ChildTreatInputsTag][DP_PerChildHIVPosCot, :n_years]
    on_cotrim = np.where(ctx_is_percent == DP_Percent, ctx_value * ctx_need / 100, ctx_value)
    modvars[AM_ChildOnCotrimTag][GB_BothSexes, :n_years] = on_cotrim

    # PMTCT need = total HIV births
    modvars[AM_ChildNeedPMTCTTag][:n_years] = hiv_births

    # HIV pregnant women = HIV births with maternal age 15-24 (first 10 single-year age groups)
    modvars[AM_HIVPregWomenTag][:n_years] = hiv_births_mat[:10, :].sum(axis=0)

    # MTCT rate at 6 weeks = sum over all sources at perinatal timing
    modvars[AM_MTCTRate6WksTag][:n_years] = mtct_tr[:, _VT_PERINATAL, :].sum(axis=0)

    # HIV+ breastfeeding women at 3 and 12 months
    treatment_total = pmtct_cov.sum(axis=0)  # (T,) — fraction of births covered by any PMTCT strategy
    inf_feed = modvars[AM_InfantFeedingOptionsTag]  # [month_idx, pmtct_status, t], values in percent
    # Index 2 = 0–2 month BF window (~3 months), index 7 = 12 months (see Delphi comment)
    bf_3mos_not = inf_feed[2, DP_NotInPMTCT, :n_years] / 100
    bf_3mos_in = inf_feed[2, DP_InPMTCT, :n_years] / 100
    bf_12mos_not = inf_feed[7, DP_NotInPMTCT, :n_years] / 100
    bf_12mos_in = inf_feed[7, DP_InPMTCT, :n_years] / 100
    modvars[AM_HIVPosBFWomen3MonthsTag][:n_years] = hiv_births * (
        (1 - bf_3mos_not) * (1 - treatment_total) + (1 - bf_3mos_in) * treatment_total
    )
    modvars[AM_HIVPosBFWomen12MonthsTag][:n_years] = hiv_births * (
        (1 - bf_12mos_not) * (1 - treatment_total) + (1 - bf_12mos_in) * treatment_total
    )

    # On-PMTCT count and effective regimen — computed from ARV regimen inputs (matches Delphi logic)
    arv = modvars[AM_ARVRegimenTag]
    reallocated = modvars[AM_PatientsReallocatedTag]
    on_pmtct = np.zeros(n_years)
    pmtct_eff = np.zeros(n_years)
    for t in range(n_years):
        sum_num = sum(
            arv[DP_PrenatalProphylaxis, opt, DP_Number, t]
            for opt in range(DP_SingleDoseNevir, DP_TripleARTDurPreg_Late + 1)
        )
        need = hiv_births[t]
        if sum_num != 0 and need != 0:
            num_pmtct = max(0.0, sum_num + reallocated[t])
            on_pmtct[t] = num_pmtct
            sdnev_num = arv[DP_PrenatalProphylaxis, DP_SingleDoseNevir, DP_Number, t]
            pmtct_eff[t] = num_pmtct * (1.0 - sdnev_num / sum_num)
        else:
            sum_pct = sum(
                arv[DP_PrenatalProphylaxis, opt, DP_Percent, t]
                for opt in range(DP_SingleDoseNevir, DP_TripleARTDurPreg_Late + 1)
            )
            num_pmtct = max(0.0, need * sum_pct / 100 + reallocated[t])
            on_pmtct[t] = num_pmtct
            if sum_pct > 0:
                sdnev_pct = arv[DP_PrenatalProphylaxis, DP_SingleDoseNevir, DP_Percent, t]
                pmtct_eff[t] = num_pmtct * (1.0 - sdnev_pct / sum_pct)
            else:
                pmtct_eff[t] = 0.0
    modvars[AM_ChildOnPMTCTTag][:n_years] = on_pmtct
    modvars[AM_PMTCTEffRegTag][:n_years] = pmtct_eff

    for modvar_idx, lf_idx in _MTCT_MAPPINGS_WOMEN:
        modvars[AM_ResMTCTBySourceTag][PMTCT_NumberOfWomen, modvar_idx, :n_years] = mtct_women[lf_idx, :]

    for modvar_idx, lf_idx in _MTCT_MAPPINGS_PERINATAL:
        modvars[AM_ResMTCTBySourceTag][PMTCT_NewChildInfections, modvar_idx, :n_years] = mtct_hc_inf[
            lf_idx, _VT_PERINATAL, :
        ]
        modvars[AM_ResMTCTBySourceTag][PMTCT_TransmissionRate, modvar_idx, :n_years] = mtct_tr[lf_idx, _VT_PERINATAL, :]

    for modvar_idx, lf_idx in _MTCT_MAPPINGS_BF[:6]:
        modvars[AM_ResMTCTBySourceTag][PMTCT_NewChildInfections, modvar_idx, :n_years] = mtct_hc_inf[
            lf_idx, _VT_BF_FIRST:_VT_BF_LAST, :
        ].sum(axis=0)
        modvars[AM_ResMTCTBySourceTag][PMTCT_TransmissionRate, modvar_idx, :n_years] = mtct_tr[
            lf_idx, _VT_BF_FIRST:_VT_BF_LAST, :
        ].sum(axis=0)


def _map_background_deaths(modvars: Modvars, output_state: dict, n_years: int, ss: dict):
    # p_deaths_background_totpop: (pAG=81, NS=2, T) — non-HIV background deaths by single age
    bg = output_state["p_deaths_background_totpop"]
    modvars[DP_DeathsByAgeTag][GB_Male, : ss["pAG"], :n_years] = bg[:, 0, :]
    modvars[DP_DeathsByAgeTag][GB_Female, : ss["pAG"], :n_years] = bg[:, 1, :]
    modvars[DP_DeathsByAgeTag][GB_BothSexes, : ss["pAG"], :n_years] = bg[:, 0, :] + bg[:, 1, :]


def _map_on_art_by_age(modvars: Modvars, output_state: dict, n_years: int, ss: dict):
    # Adults 15-80: h_artpop (hTS=3, hDS=7, hAG=66, NS=2, T) — sum over ART duration and CD4
    art_adults = output_state["h_artpop"].sum(axis=(0, 1))  # (66, 2, T)
    modvars[AM_OnARTBySingleAgeTag][GB_Male, ss["p_idx_hiv_first_adult"] : ss["pAG"], :n_years] = art_adults[:, 0, :]
    modvars[AM_OnARTBySingleAgeTag][GB_Female, ss["p_idx_hiv_first_adult"] : ss["pAG"], :n_years] = art_adults[:, 1, :]
    modvars[AM_OnARTBySingleAgeTag][GB_BothSexes, ss["p_idx_hiv_first_adult"] : ss["pAG"], :n_years] = (
        art_adults[:, 0, :] + art_adults[:, 1, :]
    )

    # Children 0-4: hc1_artpop (hTS=3, hc1DS=7, hc1AG=5, NS=2, T)
    art_hc1 = output_state["hc1_artpop"].sum(axis=(0, 1))  # (5, 2, T)
    modvars[AM_OnARTBySingleAgeTag][GB_Male, 0:5, :n_years] = art_hc1[:, 0, :]
    modvars[AM_OnARTBySingleAgeTag][GB_Female, 0:5, :n_years] = art_hc1[:, 1, :]
    modvars[AM_OnARTBySingleAgeTag][GB_BothSexes, 0:5, :n_years] = art_hc1[:, 0, :] + art_hc1[:, 1, :]

    # Children 5-14: hc2_artpop (hTS=3, hc2DS=6, hc2AG=10, NS=2, T)
    art_hc2 = output_state["hc2_artpop"].sum(axis=(0, 1))  # (10, 2, T)
    modvars[AM_OnARTBySingleAgeTag][GB_Male, 5:15, :n_years] = art_hc2[:, 0, :]
    modvars[AM_OnARTBySingleAgeTag][GB_Female, 5:15, :n_years] = art_hc2[:, 1, :]
    modvars[AM_OnARTBySingleAgeTag][GB_BothSexes, 5:15, :n_years] = art_hc2[:, 0, :] + art_hc2[:, 1, :]


def _map_art_duration_adults(modvars: Modvars, output_state: dict, n_years: int):
    # h_artpop: (hTS=3, hDS=7, hAG=66, NS=2, T)
    #   hTS 0 = ART <6mo, hTS 1 = ART 6-12mo, hTS 2 = ART >12mo
    # AM_ResOnARTlt1Yr15PlusTag[sex, T]: adults 15-80 on ART < 1 year (hTS 0+1)
    # AM_ResOnARTgt1Yr15PlusTag[sex, T]: adults 15-80 on ART > 1 year (hTS 2)
    h_art = output_state["h_artpop"]  # (3, 7, 66, 2, T)
    lt1yr = h_art[0:2, :, :, :, :].sum(axis=(0, 1, 2))  # (2, T)
    gt1yr = h_art[2, :, :, :, :].sum(axis=(0, 1))  # (2, T)

    modvars[AM_ResOnARTlt1Yr15PlusTag][GB_Male, :n_years] = lt1yr[0, :]
    modvars[AM_ResOnARTlt1Yr15PlusTag][GB_Female, :n_years] = lt1yr[1, :]
    modvars[AM_ResOnARTlt1Yr15PlusTag][GB_BothSexes, :n_years] = lt1yr[0, :] + lt1yr[1, :]

    modvars[AM_ResOnARTgt1Yr15PlusTag][GB_Male, :n_years] = gt1yr[0, :]
    modvars[AM_ResOnARTgt1Yr15PlusTag][GB_Female, :n_years] = gt1yr[1, :]
    modvars[AM_ResOnARTgt1Yr15PlusTag][GB_BothSexes, :n_years] = gt1yr[0, :] + gt1yr[1, :]


def _map_adult_cd4_distribution(modvars: Modvars, output_state: dict, n_years: int, ss: dict):
    # h_hivpop: (hDS=7, hAG=66, NS=2, T) — HIV+ not on ART by CD4 stage, age, sex, year
    # h_artpop: (hTS=3, hDS=7, hAG=66, NS=2, T) — on ART by duration, CD4, age, sex, year
    # AM_CD4DistributionTag[sex, CD4, ART_state, T]: adults 15-80, CD4 stages DP_CD4_GT500..DP_CD4_LT50
    hiv_by_cd4 = output_state["h_hivpop"].sum(axis=1)  # (7, 2, T) — sum over age
    art_by_cd4 = output_state["h_artpop"].sum(axis=(0, 2))  # (7, 2, T) — sum over ART-dur and age

    for c_idx in range(ss["hDS"]):  # 7 CD4 stages, 0-indexed in leapfrog
        c = c_idx + DP_CD4_GT500  # 1-indexed modvar CD4 constant
        modvars[AM_CD4DistributionTag][GB_Male, c, DP_NoTreat, :n_years] = hiv_by_cd4[c_idx, 0, :]
        modvars[AM_CD4DistributionTag][GB_Female, c, DP_NoTreat, :n_years] = hiv_by_cd4[c_idx, 1, :]
        modvars[AM_CD4DistributionTag][GB_BothSexes, c, DP_NoTreat, :n_years] = (
            hiv_by_cd4[c_idx, 0, :] + hiv_by_cd4[c_idx, 1, :]
        )

        modvars[AM_CD4DistributionTag][GB_Male, c, DP_OnART, :n_years] = art_by_cd4[c_idx, 0, :]
        modvars[AM_CD4DistributionTag][GB_Female, c, DP_OnART, :n_years] = art_by_cd4[c_idx, 1, :]
        modvars[AM_CD4DistributionTag][GB_BothSexes, c, DP_OnART, :n_years] = (
            art_by_cd4[c_idx, 0, :] + art_by_cd4[c_idx, 1, :]
        )


def _map_child_cd4_distribution(modvars: Modvars, output_state: dict, n_years: int, ss: dict):
    # hc1_hivpop: (hc1DS=7, hcTT=4, hc1AG=5, NS=2, T) — children 0-4, not on ART
    # hc2_hivpop: (hc2DS=6, hcTT=4, hc2AG=10, NS=2, T) — children 5-14, not on ART
    # hc1_artpop: (hTS=3, hc1DS=7, hc1AG=5, NS=2, T) — children 0-4, on ART
    # hc2_artpop: (hTS=3, hc2DS=6, hc2AG=10, NS=2, T) — children 5-14, on ART
    # AM_CD4DistributionChildTag[sex, age_grp, CD4, TT/ART-dur, ART_state, T]
    #   No-ART: TT dimension d = DP_P_Perinatal..DP_P_BF12 (4 values, maps to hcTT_idx 0-3)
    #   On-ART: d = DP_D_ARTlt6m..DP_D_ARTgt12m (3 values, maps to hTS_idx 0-2)

    hc1_hiv = output_state["hc1_hivpop"].sum(axis=2)  # (7, 4, 2, T) — sum over age
    hc2_hiv = output_state["hc2_hivpop"].sum(axis=2)  # (6, 4, 2, T)
    hc1_art = output_state["hc1_artpop"].sum(axis=2)  # (3, 7, 2, T) — sum over age
    hc2_art = output_state["hc2_artpop"].sum(axis=2)  # (3, 6, 2, T)

    # Children 0-4, not on ART: CD4 stages DP_CD4_Per_GT30..DP_CD4_Per_LT5 (7 stages)
    for c_idx in range(ss["hc1DS"]):
        c = c_idx + DP_CD4_Per_GT30
        for tt_idx in range(ss["hcTT"]):
            d = tt_idx + DP_P_Perinatal
            mv = modvars[AM_CD4DistributionChildTag]
            mv[GB_Male, DP_CD4_0t4, c, d, DP_NoTreat, :n_years] = hc1_hiv[c_idx, tt_idx, 0, :]
            mv[GB_Female, DP_CD4_0t4, c, d, DP_NoTreat, :n_years] = hc1_hiv[c_idx, tt_idx, 1, :]
            mv[GB_BothSexes, DP_CD4_0t4, c, d, DP_NoTreat, :n_years] = (
                hc1_hiv[c_idx, tt_idx, 0, :] + hc1_hiv[c_idx, tt_idx, 1, :]
            )

    # Children 5-14, not on ART: CD4 stages DP_CD4_Ped_GT1000..DP_CD4_Ped_LT200 (6 stages)
    for c_idx in range(ss["hc2DS"]):
        c = c_idx + DP_CD4_Ped_GT1000
        for tt_idx in range(ss["hcTT"]):
            d = tt_idx + DP_P_Perinatal
            mv = modvars[AM_CD4DistributionChildTag]
            mv[GB_Male, DP_CD4_5t14, c, d, DP_NoTreat, :n_years] = hc2_hiv[c_idx, tt_idx, 0, :]
            mv[GB_Female, DP_CD4_5t14, c, d, DP_NoTreat, :n_years] = hc2_hiv[c_idx, tt_idx, 1, :]
            mv[GB_BothSexes, DP_CD4_5t14, c, d, DP_NoTreat, :n_years] = (
                hc2_hiv[c_idx, tt_idx, 0, :] + hc2_hiv[c_idx, tt_idx, 1, :]
            )

    # Children 0-4, on ART: ART duration DP_D_ARTlt6m..DP_D_ARTgt12m (3 durations = hTS)
    for ts_idx in range(ss["hTS"]):
        d = ts_idx + DP_D_ARTlt6m
        for c_idx in range(ss["hc1DS"]):
            c = c_idx + DP_CD4_Per_GT30
            # sum over hcTT (dim 2 in hc1_art which is (hTS, hc1DS, NS, T))
            vals = hc1_art[ts_idx, c_idx, :, :]  # (2, T)
            mv = modvars[AM_CD4DistributionChildTag]
            mv[GB_Male, DP_CD4_0t4, c, d, DP_OnART, :n_years] = vals[0]
            mv[GB_Female, DP_CD4_0t4, c, d, DP_OnART, :n_years] = vals[1, :]
            mv[GB_BothSexes, DP_CD4_0t4, c, d, DP_OnART, :n_years] = vals[0, :] + vals[1, :]

    # Children 5-14, on ART
    for ts_idx in range(ss["hTS"]):
        d = ts_idx + DP_D_ARTlt6m
        for c_idx in range(ss["hc2DS"]):
            c = c_idx + DP_CD4_Ped_GT1000
            vals = hc2_art[ts_idx, c_idx, :, :]  # (2, T)
            mv = modvars[AM_CD4DistributionChildTag]
            mv[GB_Male, DP_CD4_5t14, c, d, DP_OnART, :n_years] = vals[0, :]
            mv[GB_Female, DP_CD4_5t14, c, d, DP_OnART, :n_years] = vals[1, :]
            mv[GB_BothSexes, DP_CD4_5t14, c, d, DP_OnART, :n_years] = vals[0, :] + vals[1, :]


def _map_cd4_distribution_15_49(modvars: Modvars, output_state: dict, n_years: int, ss: dict):
    # Ages 15-49 = leapfrog hAG indices 0-34 (hAG covers 66 single ages from 15)
    hiv_by_cd4 = output_state["h_hivpop"][:, 0:35, :, :].sum(axis=1)  # (7, 2, T)
    art_by_cd4 = output_state["h_artpop"][:, :, 0:35, :, :].sum(axis=(0, 2))  # (7, 2, T)

    for c_idx in range(ss["hDS"]):
        c = c_idx + DP_CD4_GT500
        modvars[AM_CD4Distribution15_49Tag][GB_Male, c, DP_NoTreat, :n_years] = hiv_by_cd4[c_idx, 0, :]
        modvars[AM_CD4Distribution15_49Tag][GB_Female, c, DP_NoTreat, :n_years] = hiv_by_cd4[c_idx, 1, :]
        modvars[AM_CD4Distribution15_49Tag][GB_BothSexes, c, DP_NoTreat, :n_years] = (
            hiv_by_cd4[c_idx, 0, :] + hiv_by_cd4[c_idx, 1, :]
        )

        modvars[AM_CD4Distribution15_49Tag][GB_Male, c, DP_OnART, :n_years] = art_by_cd4[c_idx, 0, :]
        modvars[AM_CD4Distribution15_49Tag][GB_Female, c, DP_OnART, :n_years] = art_by_cd4[c_idx, 1, :]
        modvars[AM_CD4Distribution15_49Tag][GB_BothSexes, c, DP_OnART, :n_years] = (
            art_by_cd4[c_idx, 0, :] + art_by_cd4[c_idx, 1, :]
        )


def _map_perinatal_and_infant(modvars: Modvars, output_state: dict, n_years: int):
    # Perinatal MTCT rate = sum of transmission rates across all sources at perinatal timing
    mtct_tr = output_state["mtct_by_source_tr"]  # (11, 5, T)
    modvars[AM_PerinatalTransmissionTag][:n_years] = mtct_tr[:, _VT_PERINATAL, :].sum(axis=0)

    # New infant infections = total HIV births
    modvars[AM_NewInfantInfectionsTag][:n_years] = output_state["hiv_births"]


def _map_children_aged14(modvars: Modvars, output_state: dict, n_years: int, ss: dict):
    # hc2 covers ages 5-14 (hc2AG=10), so age 14 = index 9
    hc2_hiv_age14 = output_state["hc2_hivpop"][:, :, 9, :, :]  # (hc2DS=6, hcTT=4, NS=2, T)
    hc2_art_age14 = output_state["hc2_artpop"][:, :, 9, :, :]  # (hTS=3, hc2DS=6, NS=2, T)

    # No-ART: d = DP_P_Perinatal..DP_P_BF12 (4 transmission types, hcTT_idx 0-3)
    for c_idx in range(ss["hc2DS"]):
        c = c_idx + DP_CD4_Ped_GT1000
        for tt_idx in range(ss["hcTT"]):
            d = tt_idx + DP_P_Perinatal
            mv = modvars[AM_ChAged14ByCD4CatTag]
            mv[GB_Male, c, d, :n_years] = hc2_hiv_age14[c_idx, tt_idx, 0, :]
            mv[GB_Female, c, d, :n_years] = hc2_hiv_age14[c_idx, tt_idx, 1, :]
            mv[GB_BothSexes, c, d, :n_years] = hc2_hiv_age14[c_idx, tt_idx, 0, :] + hc2_hiv_age14[c_idx, tt_idx, 1, :]

    # On-ART: d = DP_D_ARTlt6m..DP_D_ARTgt12m (3 durations, hTS_idx 0-2); sum over hcTT
    for ts_idx in range(ss["hTS"]):
        d = ts_idx + DP_D_ARTlt6m
        for c_idx in range(ss["hc2DS"]):
            c = c_idx + DP_CD4_Ped_GT1000
            vals = hc2_art_age14[ts_idx, c_idx, :, :]  # (NS=2, T)
            mv = modvars[AM_ChAged14ByCD4CatTag]
            mv[GB_Male, c, d, :n_years] = vals[0, :]
            mv[GB_Female, c, d, :n_years] = vals[1, :]
            mv[GB_BothSexes, c, d, :n_years] = vals[0, :] + vals[1, :]


def _map_child_ctx_need_1_4(modvars: Modvars, output_state: dict, n_years: int):
    # CTX need for ages 1-4 = all HIV+ children (not on ART + on ART) aged 1-4
    # hc1 covers ages 0-4 (hc1AG=5), so ages 1-4 = indices 1:5
    hc1_hiv_1_4 = output_state["hc1_hivpop"][:, :, 1:5, :, :].sum(axis=(0, 1, 2))  # (NS=2, T)
    hc1_art_1_4 = output_state["hc1_artpop"][:, :, 1:5, :, :].sum(axis=(0, 1, 2))  # (NS=2, T)
    ctx_1_4 = hc1_hiv_1_4 + hc1_art_1_4

    modvars[AM_ChildCTXNeed1To4Tag][GB_Male, :n_years] = ctx_1_4[0, :]
    modvars[AM_ChildCTXNeed1To4Tag][GB_Female, :n_years] = ctx_1_4[1, :]
    modvars[AM_ChildCTXNeed1To4Tag][GB_BothSexes, :n_years] = ctx_1_4[0, :] + ctx_1_4[1, :]


# CD4 lower limits corresponding to leapfrog h_hivpop stage indices 0-6
_CD4_LOWER_LIMITS = [500, 350, 250, 200, 100, 50, 0]


def _map_need_art(modvars: Modvars, output_state: dict, n_years: int, ss: dict):
    # Replicates CalcNeedForARTEndYear from Delphi PostLeapfrogBookkeeping
    h_hivpop = output_state["h_hivpop"]  # (hDS=7, hAG=66, NS=2, T)
    h_artpop = output_state["h_artpop"]  # (hTS=3, hDS=7, hAG=66, NS=2, T)
    p_hivpop = output_state["p_hivpop"]  # (pAG=81, NS=2, T)

    # All adults on ART need ART (regardless of CD4)
    art_adults = h_artpop.sum(axis=(0, 1))  # (hAG=66, NS=2, T)

    cd4_thresholds = modvars[AM_CD4ThreshHoldAdultsTag]

    for t in range(n_years):
        threshold = int(cd4_thresholds[t])
        # Special case: WHO stage 3/4 adjustment (matches get_cd4_threshold_adult_idx logic)
        if threshold == 200:
            threshold = 250

        # HIV+ adults below CD4 threshold
        eligible = [c for c in range(ss["hDS"]) if _CD4_LOWER_LIMITS[c] < threshold]
        if eligible:
            hiv_below = h_hivpop[eligible, :, :, t].sum(axis=0)  # (hAG=66, NS=2)
        else:
            hiv_below = np.zeros((ss["hAG"], ss["NS"]))

        need = art_adults[:, :, t] + hiv_below  # (66, 2)
        modvars[AM_NeedARTTag][GB_Male, ss["p_idx_hiv_first_adult"] : ss["pAG"], t] = need[:, 0]
        modvars[AM_NeedARTTag][GB_Female, ss["p_idx_hiv_first_adult"] : ss["pAG"], t] = need[:, 1]
        modvars[AM_NeedARTTag][GB_BothSexes, ss["p_idx_hiv_first_adult"] : ss["pAG"], t] = need[:, 0] + need[:, 1]

        # Children 0-14: universal eligibility — all HIV+ children need ART
        child_hiv = p_hivpop[0:15, :, t]  # (15, NS=2)
        modvars[AM_NeedARTTag][GB_Male, 0:15, t] = child_hiv[:, 0]
        modvars[AM_NeedARTTag][GB_Female, 0:15, t] = child_hiv[:, 1]
        modvars[AM_NeedARTTag][GB_BothSexes, 0:15, t] = child_hiv[:, 0] + child_hiv[:, 1]


def _map_dll_internals_to_zero(modvars: Modvars, n_years: int):
    # These are computed internally by the DLL and have no leapfrog equivalent
    # modvars[AM_IncidenceAdjustmentFactorTag][:n_years] = 1
    modvars[AM_PopAdjTag][:, :n_years] = 0
    modvars[AM_PopAdjAmountTag][:] = 0
    modvars[AM_NewlyStartingARTTag][:] = 0


def modvars_to_leapfrog(modvars: Modvars, ss: dict):

    first_year = modvars[PJN_FirstYearTag]
    final_year = modvars[PJN_FinalYearTag]
    final_year_idx = final_year - first_year

    opts = _get_leapfrog_opts(modvars, final_year_idx)

    dp_modvars = _dp_modvars_leapfrog(modvars, final_year_idx)

    adult_modvars = _hiv_adult_modvars_leapfrog(modvars, final_year_idx, ss)

    child_modvars = _hiv_child_modvars_leapfrog(modvars, final_year_idx, ss)

    return {**opts, **dp_modvars, **adult_modvars, **child_modvars}


def _get_t_art_start(modvars, final_year_idx):
    for t in range(final_year_idx + 1):
        if any(modvars[AM_HAARTBySexTag][GB_Male : GB_Female + 1, t] != 0):
            return t
    # There is no ART start date, so ensure we use a time later than the final
    # index so ART not run in leapfrog
    return final_year_idx + 1


def _get_leapfrog_opts(modvars, final_year_idx):
    t_art_start = _get_t_art_start(modvars, final_year_idx)

    return {
        "t_ART_start": t_art_start,
        "hts_per_year": 10,
        "projection_start_year": modvars[PJN_FirstYearTag],
        "projection_end_year": modvars[PJN_FinalYearTag],
        "projection_period": "calendar",
    }


def _dp_modvars_leapfrog(modvars: Modvars, final_year_idx: int):
    ## TODO: This get first year bigpop, is that right? What if we're running
    ## from 1980, not 1970. What index do we have in the data here vs
    ## We have first year above, but what idx will this correspond to?
    ## Does bigpop get truncated or does it always have 61 years? Look into this
    base_pop = modvars[DP_BigPopTag][GB_Male : (GB_Female + 1), : (GB_MaxSingleAges + 1), 0].T.copy(order="F")

    ## MaxSingleAges + 3 because this is the probability of survival moving from
    ## age birth to end of year, 0 to 1, 1 to 2, ..., 79 to 80, 80-80+, 80+ to 80+
    ## So MaxSingleAges is 80, +1 for 80-80+ and + 1 for 80+ to 80+ and +1 for numpy indexing
    ## Starts counting at index 1 for this modvar
    survival_prob = modvars[DP_SurvRateTag][
        1 : (GB_MaxSingleAges + 3), GB_Male : (GB_Female + 1), : (final_year_idx + 1)
    ].copy(order="F")

    net_migration = np.zeros((GB_MaxSingleAges + 1, GB_NumSexes, final_year_idx + 1), order="F")

    # TODO: this is really messy, but we probably have to refactor
    # calc_single_ages to make it nicer
    for t in range(final_year_idx + 1):
        for s_idx, s in enumerate([GB_Male, GB_Female]):
            # Calc_Single_Ages is expecting to index a length 18 array, so we need to use
            # all ages here, even though Calc_Single_Ages doesn't use it
            migr_age_dist = modvars[DP_MigrAgeDistTag][s, GB_AllAges : (GB_MAX_AGE + 1), t]
            migr_rate = modvars[DP_MigrRateTag][s, GB_AllAges, t]
            net_migr_5 = (migr_age_dist / 100) * migr_rate

            # TODO: Calc_Single_Ages reads really weird, why don't we have it return the
            # created list?
            net_migr = np.full((GB_MaxSingleAges + 1), 0).tolist()
            Calc_Single_Ages(modvars, net_migr_5.tolist(), net_migr, s)

            net_migration[:, s_idx, t] = net_migr

    asfr = _get_leapfrog_asfr(modvars, final_year_idx)

    births_sex_prop = np.zeros((GB_NumSexes, final_year_idx + 1), order="F")
    for t in range(final_year_idx + 1):
        births_sex_prop[GB_Male - GB_Male, t] = getSexBirthRatioPercent(modvars, GB_Male, t)
        births_sex_prop[GB_Female - GB_Male, t] = getSexBirthRatioPercent(modvars, GB_Female, t)

    tfr = modvars[DP_TFRTag]

    return {
        "basepop": base_pop,
        "Sx": survival_prob,
        "netmigr_adj": net_migration,
        "asfr": asfr,
        "births_sex_prop": births_sex_prop,
        "tfr": tfr,
    }


def _hiv_adult_modvars_leapfrog(modvars: Modvars, final_year_idx: int, ss: dict):
    incidence_option = modvars[AM_IncidenceOptionsTag]
    input_adult_incidence_rate = (modvars[AM_IncidenceByFitTag][incidence_option, : (final_year_idx + 1)] / 100).copy(
        order="F"
    )

    incrr_age_5year = (
        modvars[AM_DistOfHIVTag][GB_Male : (GB_Female + 1), GB_AllAges : (GB_MAX_AGE + 1), : (final_year_idx + 1)]
        .transpose(2, 0, 1)
        .copy(order="F")
    )

    incrr_age_single = np.zeros((final_year_idx + 1, GB_NumSexes, GB_MaxSingleAges + 1), order="F")

    for t in range(final_year_idx + 1):
        for s_idx, s in enumerate([GB_Male, GB_Female]):
            incrr_age_slice = incrr_age_5year[t, s_idx, :].tolist()
            incrr_age_single_year = np.full((GB_MaxSingleAges + 1), 0.0).tolist()
            Calc_Single_Ages(modvars, incrr_age_slice, incrr_age_single_year, s)
            incrr_age_single[t, s_idx, :] = incrr_age_single_year

    incidence_rate_ratio_age = np.clip(
        incrr_age_single[:, :, ss["p_idx_hiv_first_adult"] :].transpose(2, 1, 0), 0, None
    ).copy(order="F")

    incidence_rate_ratio_sex = modvars[AM_HIVSexRatioTag][: (final_year_idx + 1)].copy(order="F")

    # TODO: This has weird values for the first disease stage
    #  It has low negative values instead of 0s. Other than that the values
    # look quite good.
    cd4_mortality = np.zeros((ss["hDS"], ss["hAG"], ss["NS"]), order="F")
    for ds in range(ss["hDS"]):
        for a in range(ss["hAG"]):
            cd4_mortality[ds, a, :] = modvars[AM_AdultMortByCD4NoARTTag][
                DP_Data, GB_Male : (GB_Female + 1), transf_cd4_ag[a], transf_cd4_ds[ds]
            ]

    cd4_progression = np.zeros((ss["hDS"] - 1, ss["hAG"], ss["NS"]), order="F")
    for ds in range(ss["hDS"] - 1):
        for a in range(ss["hAG"]):
            rate = modvars[AM_AdultAnnRateProgressLowerCD4Tag][
                DP_Data, GB_Male : (GB_Female + 1), transf_cd4_ag[a], transf_cd4_ds[ds]
            ]
            cd4_progression[ds, a, :] = (1 - np.exp(-rate / ss["HIV_STEPS_PER_YEAR"])) * ss["HIV_STEPS_PER_YEAR"]

    cd4_init_dist = np.zeros((ss["hDS"], ss["hAG"], ss["NS"]), order="F")
    for ds in range(ss["hDS"]):
        for a in range(ss["hAG"]):
            cd4_init_dist[ds, a, :] = (
                modvars[AM_AdultDistNewInfectionsCD4Tag][
                    DP_Data, GB_Male : (GB_Female + 1), transf_cd4_ag[a], transf_cd4_ds[ds]
                ]
                / 100
            )

    cd4_thresholds = modvars[AM_CD4ThreshHoldAdultsTag][: (final_year_idx + 1)]
    idx_hm_elig = get_cd4_threshold_adult_idx(cd4_thresholds) - DP_CD4_GT500

    art_mortality = np.zeros((ss["hTS"], ss["hDS"], ss["hAG"], ss["NS"]), order="F")

    for ds in range(ss["hDS"]):
        cd4_cat = transf_cd4_ds[ds]
        for a in range(ss["hAG"]):
            age_group = transf_cd4_ag[a]
            art_mortality[0, ds, a, :] = modvars[AM_AdultMortByCD4WithART0to6Tag][
                DP_Data, GB_Male : (GB_Female + 1), age_group, cd4_cat
            ]
            art_mortality[1, ds, a, :] = modvars[AM_AdultMortByCD4WithART7to12Tag][
                DP_Data, GB_Male : (GB_Female + 1), age_group, cd4_cat
            ]
            art_mortality[2, ds, a, :] = modvars[AM_AdultMortByCD4WithARTGT12Tag][
                DP_Data, GB_Male : (GB_Female + 1), age_group, cd4_cat
            ]

    multiplier = modvars[AM_MortalityRatesMultiplierTag]
    mort_lt12 = modvars[AM_MortalityRatesTag][DP_Data, DP_MortRates_LT12Mo, : (final_year_idx + 1)]
    mort_gt12 = modvars[AM_MortalityRatesTag][DP_Data, DP_MortRates_GT12Mo, : (final_year_idx + 1)]

    art_mortality_time_rate_ratio = np.stack(
        [mort_lt12 * multiplier, mort_lt12 * multiplier, mort_gt12 * multiplier], axis=0
    ).copy(order="F")

    cd4_nonaids_excess_mort = np.zeros((ss["hDS"], ss["hAG"], ss["NS"]), order="F")
    art_nonaids_excess_mort = np.zeros((ss["hTS"], ss["hDS"], ss["hAG"], ss["NS"]), order="F")
    for ds in range(ss["hDS"]):
        for a in range(ss["hAG"]):
            cd4_nonaids_excess_mort[ds, a, :] = modvars[AM_AdultNonAIDSExcessMortTag][
                DP_Data, GB_Male : (GB_Female + 1), transf_cd4_ag[a], transf_cd4_ds[ds], DP_NoTreat
            ]
            for ts in range(ss["hTS"]):
                art_nonaids_excess_mort[ts, ds, a, :] = modvars[AM_AdultNonAIDSExcessMortTag][
                    DP_Data, GB_Male : (GB_Female + 1), transf_cd4_ag[a], transf_cd4_ds[ds], DP_OnART
                ]

    dropout_rate = -np.log(1.0 - modvars[AM_PercInterruptedTag][: (final_year_idx + 1)] / 100).copy(order="F")

    adults_on_art = np.zeros((ss["NS"], final_year_idx + 1), order="F")
    adults_on_art_is_percent = np.zeros((ss["NS"], final_year_idx + 1), dtype=np.int32, order="F")

    for s_idx, s in enumerate([GB_Male, GB_Female]):
        is_percent = modvars[AM_HAARTBySexPerNumTag][s, : (final_year_idx + 1)]
        haart_values = modvars[AM_HAARTBySexTag][s, : (final_year_idx + 1)]

        adults_on_art_is_percent[s_idx, :] = is_percent
        adults_on_art[s_idx, :] = np.where(is_percent == DP_Percent, haart_values / 100, haart_values)

    h_art_stage_dur = np.full(ss["hTS"] - 1, 0.5, dtype=np.float64, order="F")

    initiation_mortality_weight = modvars[AM_NewARTPatAllocTag][DP_AdvOpt_ART_ExpMort]

    pag_incidpop = ss["p_fertility_age_groups"] if modvars[AM_EPPPopulationAgesTag] == DP_EPP_15t49 else ss["hAG"]

    fert_mult_by_age = np.zeros((DP_NumFertileAges, final_year_idx + 1), order="F")
    fert_mult_on_art = np.zeros(DP_NumFertileAges, order="F")

    for a in range(DP_NumFertileAges):
        five_year_age_group = (a // 5) + GB_A15_19
        fert_mult_on_art[a] = modvars[AM_RatioWomenOnARTTag][DP_Data, five_year_age_group]
        fert_mult_by_age[a, :] = modvars[AM_HIVTFRTag][DP_Data, five_year_age_group, : (final_year_idx + 1)]

    fert_mult_off_art = modvars[AM_FertCD4DiscountTag][DP_Data, DP_CD4_GT500 : (DP_CD4_LT50 + 1)].copy(order="F")

    local_adj_factor = modvars[AM_FRRbyLocationTag][DP_Data]

    return {
        "incidence_model_choice": 0,  # Turn off the incidence model
        "incidinput": input_adult_incidence_rate,
        "transmission_rate_hts": np.full(
            (final_year_idx + 1) * ss["HIV_STEPS_PER_YEAR"], 0.0
        ),  # Only used by incidence model
        "initial_incidence": 0.0,  # Only used by incidence model
        "epidemic_start_hts": (final_year_idx + 1) * ss["HIV_STEPS_PER_YEAR"],  # Only used by incidence model
        "relative_infectiousness_art": 0.1,  # Only used by incidence model
        "incrr_age": incidence_rate_ratio_age,
        "incrr_sex": incidence_rate_ratio_sex,
        "cd4_mort": cd4_mortality,
        "cd4_prog": cd4_progression,
        "cd4_initdist": cd4_init_dist,
        "scale_cd4_mort": 1,  # Always 1
        "artcd4elig_idx": idx_hm_elig,
        "art_mort": art_mortality,
        "artmx_timerr": art_mortality_time_rate_ratio,
        "cd4_nonaids_excess_mort": cd4_nonaids_excess_mort,
        "art_nonaids_excess_mort": art_nonaids_excess_mort,
        "art_dropout_recover_cd4": 1,  # Always 1
        "art_dropout_rate": dropout_rate,
        "art15plus_num": adults_on_art,
        "art15plus_isperc": adults_on_art_is_percent,
        "art_alloc_mxweight": initiation_mortality_weight,
        "h_art_stage_dur": h_art_stage_dur,
        "pAG_INCIDPOP": pag_incidpop,
        "pIDX_INCIDPOP": 15,  # Always 15
        "fert_rat": fert_mult_by_age,
        "cd4fert_rat": fert_mult_off_art,
        "frr_art6mos": fert_mult_on_art,
        "frr_scalar": local_adj_factor,
    }


def _hiv_child_modvars_leapfrog(modvars: Modvars, final_year_idx: int, ss: dict):
    hc_nosocomial = modvars[AM_NosocomialInfectionsByAgeTag][GB_A0_4, : (final_year_idx + 1)].copy(order="F")

    hc1_cd4_dist = (
        modvars[AM_ChildDistNewInfectionsCD4Tag][DP_Data, DP_CD4_Per_GT30 : (DP_CD4_Per_LT5 + 1)] / 100
    ).copy(order="F")

    hc1_cd4_mort = np.zeros((ss["hc1DS"], ss["hcTT"], ss["hc1AG"]), order="F")
    age_mapping_hc1 = [DP_A0t2, DP_A0t2, DP_A0t2, DP_A3t4, DP_A3t4]
    for c in range(ss["hc1DS"]):
        cd4_cat = c + DP_CD4_Per_GT30
        for d in range(ss["hcTT"]):
            trans_type = d + DP_P_Perinatal
            for a in range(ss["hc1AG"]):
                age_group = age_mapping_hc1[a]
                hc1_cd4_mort[c, d, a] = modvars[AM_ChildMortByCD4NoARTTag][DP_Data, age_group, trans_type, cd4_cat]

    hc2_cd4_mort = np.zeros((ss["hc2DS"], ss["hcTT"], ss["hc2AG"]), order="F")
    for c in range(ss["hc2DS"]):
        cd4_cat = c + DP_CD4_Ped_GT1000
        for d in range(ss["hcTT"]):
            trans_type = d + DP_P_Perinatal
            for a in range(ss["hc2AG"]):
                hc2_cd4_mort[c, d, a] = modvars[AM_ChildMortByCD4NoARTTag][DP_Data, DP_A5t14, trans_type, cd4_cat]

    hc1_cd4_prog = np.zeros((ss["hc1DS"], ss["hc1AG_c"], ss["NS"]), order="F")
    for a_idx in range(ss["hc1AG_c"]):
        age_group = a_idx + DP_A0t2
        for s_idx, s in enumerate([GB_Male, GB_Female]):
            for c in range(ss["hc1DS"] - 1):
                cd4_cat = c + DP_CD4_Per_GT30
                hc1_cd4_prog[c, a_idx, s_idx] = modvars[AM_ChildAnnRateProgressLowerCD4Tag][
                    DP_Data, s, age_group, cd4_cat
                ]

    hc2_cd4_prog = np.zeros((ss["hc2DS"], ss["hc2AG_c"], ss["NS"]), order="F")
    for s_idx, s in enumerate([GB_Male, GB_Female]):
        for c in range(ss["hc2DS"] - 1):
            cd4_cat = c + DP_CD4_Ped_GT1000
            hc2_cd4_prog[c, 0, s_idx] = modvars[AM_ChildAnnRateProgressLowerCD4Tag][DP_Data, s, DP_A5t14, cd4_cat]

    ctx_val = np.zeros(final_year_idx + 1, order="F")
    ctx_val_is_percent = np.zeros(final_year_idx + 1, dtype=np.int32, order="F")
    hc_art_val = np.zeros((ss["hcAG_coarse"], final_year_idx + 1), order="F")
    hc_art_is_percent = np.zeros(final_year_idx + 1, dtype=np.int32, order="F")
    hc_art_is_age_spec = np.zeros(final_year_idx + 1, dtype=np.int32, order="F")

    hc_art_start = 0

    for t in range(final_year_idx + 1):
        ctx_val_is_percent[t] = int(modvars[AM_ChildARTByAgeGroupPerNumTag][DP_PerChildHIVPosCot, t])
        ctx_value = modvars[AM_ChildTreatInputsTag][DP_PerChildHIVPosCot, t]
        if ctx_val_is_percent[t] == DP_Percent:
            ctx_val[t] = ctx_value / 100
        else:
            ctx_val[t] = ctx_value

        hc_art_is_percent[t] = int(modvars[AM_ChildARTByAgeGroupPerNumTag][DP_PerChildHIVRecART, t])
        hc_art_has_value = False
        for a in range(DP_PerChildHIVRecART, DP_PerChildHIVRecART10_14 + 1):
            value = modvars[AM_ChildTreatInputsTag][a, t]

            if value != -9999:  # -9999 is used as NA value
                if hc_art_is_percent[t] == DP_Percent:
                    hc_art_val[a - DP_PerChildHIVRecART, t] = value / 100
                else:
                    hc_art_val[a - DP_PerChildHIVRecART, t] = value
                hc_art_has_value = hc_art_has_value or (value > 0)
            else:
                hc_art_val[a - DP_PerChildHIVRecART, t] = 0

        if modvars[AM_ChildTreatInputsTag][DP_PerChildHIVRecART0_4, t] != -9999:
            hc_art_is_age_spec[t] = 1
        else:
            hc_art_is_age_spec[t] = 0

        if hc_art_start == 0 and hc_art_has_value:
            hc_art_start = t

    ctx_effect = np.zeros(3, order="F")
    ctx_effect[0] = np.mean(modvars[AM_EffectTreatChildTag][DP_Data, DP_ChildEffNoART, 1:6])
    ctx_effect[1] = modvars[AM_EffectTreatChildTag][DP_Data, DP_ChildEffWithART, 1]
    ctx_effect[2] = np.mean(modvars[AM_EffectTreatChildTag][DP_Data, DP_ChildEffWithART, 2:6])

    hc_art_elig_age = (
        (modvars[AM_AgeHIVChildOnTreatmentTag][: (final_year_idx + 1)] // 12).astype(np.int32).copy(order="F")
    )

    hc_art_elig_cd4 = np.zeros((ss["p_idx_hiv_first_adult"], final_year_idx + 1), dtype=np.int32, order="F")

    for a in range(ss["p_idx_hiv_first_adult"]):
        # Determine age group and percent/number
        if a == 0:
            a1 = DP_AgeLT11Mths
            p = DP_Percent
        elif a in [1, 2]:
            a1 = DP_Age12to35Mths
            p = DP_Percent
        elif a in [3, 4]:
            a1 = DP_Age35to59Mths
            p = DP_Percent
        else:  # 5-14
            a1 = DP_AgeGT5Years
            p = DP_Number

        for t in range(final_year_idx + 1):
            threshold = modvars[AM_CD4ThreshHoldTag][p, a1, t]
            cd4_idx = get_cd4_threshold_child_idx(threshold, p)

            if p == DP_Number:
                hc_art_elig_cd4[a, t] = cd4_idx - DP_CD4_Ped_GT1000
            else:
                hc_art_elig_cd4[a, t] = cd4_idx - DP_CD4_Per_GT30

    hc_art_mort_rr = np.zeros((ss["hTS"], ss["p_idx_hiv_first_adult"], final_year_idx + 1), order="F")
    for a in range(ss["p_idx_hiv_first_adult"]):
        if a <= 4:
            a2 = DP_CD4_0t4
        else:
            a2 = DP_CD4_5t14

        for t in range(final_year_idx + 1):
            mort_lt12 = modvars[AM_ChildMortalityRatesTag][DP_Data, a2, DP_MortRates_LT12Mo, t]
            mort_gt12 = modvars[AM_ChildMortalityRatesTag][DP_Data, a2, DP_MortRates_GT12Mo, t]

            hc_art_mort_rr[0, a, t] = mort_lt12
            hc_art_mort_rr[1, a, t] = mort_lt12
            hc_art_mort_rr[2, a, t] = mort_gt12

    hc1_art_mort = np.zeros((ss["hc1DS"], ss["hTS"], ss["hc1AG"]), order="F")
    age_mapping_hc1_art = [DP_A0, DP_A1t2, DP_A1t2, DP_A3t4, DP_A3t4]
    for c in range(ss["hc1DS"]):
        cd4_cat = c + DP_CD4_Per_GT30
        for a in range(ss["hc1AG"]):
            age_group = age_mapping_hc1_art[a]
            hc1_art_mort[c, 0, a] = modvars[AM_ChildMortByCD4WithART0to6PercTag][DP_Data, GB_Male, age_group, cd4_cat]
            hc1_art_mort[c, 1, a] = modvars[AM_ChildMortByCD4WithART7to12PercTag][DP_Data, GB_Male, age_group, cd4_cat]
            hc1_art_mort[c, 2, a] = modvars[AM_ChildMortByCD4WithARTGT12PercTag][DP_Data, GB_Male, age_group, cd4_cat]

    hc2_art_mort = np.zeros((ss["hc2DS"], ss["hTS"], ss["hc2AG"]), order="F")
    for c in range(ss["hc2DS"]):
        cd4_cat = c + DP_CD4_Ped_GT1000
        for a in range(5, 15):  # Ages 5-14
            # Map to age group
            if a <= 9:
                age_group = DP_A5t9
            else:
                age_group = DP_A10t14

            a_idx = a - 5
            hc2_art_mort[c, 0, a_idx] = modvars[AM_ChildMortByCD4WithART0to6Tag][DP_Data, GB_Male, age_group, cd4_cat]
            hc2_art_mort[c, 1, a_idx] = modvars[AM_ChildMortByCD4WithART7to12Tag][DP_Data, GB_Male, age_group, cd4_cat]
            hc2_art_mort[c, 2, a_idx] = modvars[AM_ChildMortByCD4WithARTGT12Tag][DP_Data, GB_Male, age_group, cd4_cat]

    hc_art_init_dist = modvars[AM_ChildARTDistTag][DP_Data, DP_A0 : (DP_A14 + 1), : (final_year_idx + 1)].copy(
        order="F"
    )

    # Shape: (hDS+1, hVT) where hDS=7 adult CD4 categories + 1 for incident
    vertical_transmission_rate = np.zeros((ss["hDS"] + 1, ss["hVT"]), order="F")

    vt_mapping = [
        # CD4 categories for existing infections (indices 0-6)
        (DP_NoProphExistInfCD4GT350, DP_Perinatal, DP_BreastfeedingGE350),
        (DP_NoProphExistInfCD4GT350, DP_Perinatal, DP_BreastfeedingGE350),
        (DP_NoProphExistInfCD4200_350, DP_Perinatal, DP_BreastfeedingLT350),
        (DP_NoProphExistInfCD4200_350, DP_Perinatal, DP_BreastfeedingLT350),
        (DP_NoProphExistInfCD4LT200, DP_Perinatal, DP_BreastfeedingLT350),
        (DP_NoProphExistInfCD4LT200, DP_Perinatal, DP_BreastfeedingLT350),
        (DP_NoProphExistInfCD4LT200, DP_Perinatal, DP_BreastfeedingLT350),
    ]

    for idx, (cd4_status, peri_type, bf_type) in enumerate(vt_mapping):
        vertical_transmission_rate[idx, 0] = modvars[AM_TransEffAssumpTag][DP_Data, cd4_status, peri_type] / 100
        vertical_transmission_rate[idx, 1] = modvars[AM_TransEffAssumpTag][DP_Data, cd4_status, bf_type] / 100

    # Incident infections (index 7)
    vertical_transmission_rate[7, 0] = modvars[AM_TransEffAssumpTag][DP_Data, DP_NoProphIncidentInf, DP_Perinatal] / 100
    vertical_transmission_rate[7, 1] = (
        modvars[AM_TransEffAssumpTag][DP_Data, DP_NoProphIncidentInf, DP_BreastfeedingLT350] / 100
    )

    pmtct_dropout = np.zeros((ss["hPS"], ss["hVT_dropout"], final_year_idx + 1), order="F")
    pmtct_dropout[:, 0, :] = 1

    for t in range(final_year_idx + 1):
        pmtct_dropout[4, 0, t] = modvars[AM_PercentARTDeliveryTag][DP_OnARTAtDelivery, t] / 100
        pmtct_dropout[5, 0, t] = modvars[AM_PercentARTDeliveryTag][DP_StartingARTAtDelivery, t] / 100
        dropout_0_12 = modvars[AM_ARVRegimenTag][DP_AnnDropPostnatalProph, DP_ART0_12MthsBF, DP_Percent, t] / 100
        dropout_gt12 = modvars[AM_ARVRegimenTag][DP_AnnDropPostnatalProph, DP_ARTGT12MthsBF, DP_Percent, t] / 100

        for strat in [0, 1, 4, 5, 6]:
            pmtct_dropout[strat, 1, t] = dropout_0_12
            pmtct_dropout[strat, 2, t] = dropout_gt12

    pmtct = np.zeros((ss["hPS"], final_year_idx + 1), order="F")
    pmtct_input_is_percent = np.zeros(final_year_idx + 1, dtype=np.int32, order="F")

    pmtct_options = [
        DP_OptA,
        DP_OptB,
        DP_SingleDoseNevir,
        DP_DualARV,
        DP_TripleARTBefPreg,
        DP_TripleARTDurPreg,
        DP_TripleARTDurPreg_Late,
    ]

    for t in range(final_year_idx + 1):
        total_number = modvars[AM_ARVRegimenTag][DP_PrenatalProphylaxis, DP_TotalTreat, DP_Number, t]

        if total_number > 0:
            pmtct_input_is_percent[t] = 0
            p_type = DP_Number
        else:
            pmtct_input_is_percent[t] = 1
            p_type = DP_Percent

        for idx, option in enumerate(pmtct_options):
            value = modvars[AM_ARVRegimenTag][DP_PrenatalProphylaxis, option, p_type, t]
            pmtct[idx, t] = value if p_type == DP_Percent else value

    pmtct_transmission_rate = np.zeros((ss["hDS"], ss["hPS"], ss["hVT"]), order="F")

    pmtct_trans_options = [
        DP_OptionA,
        DP_OptionB,
        DP_SingleDoseNev,
        DP_WHO2006DualARV,
        DP_ARTStartPrePreg,
        DP_ARTStartDurPreg,
        DP_ARTStartDurPreg_Late,
    ]

    for cd4_cat in range(DP_CD4_GT500, DP_CD4_LT50 + 1):  # CD4 categories
        c_idx = cd4_cat - DP_CD4_GT500

        # Perinatal transmission (all strategies)
        for strat_idx, strat in enumerate(pmtct_trans_options):
            pmtct_transmission_rate[c_idx, strat_idx, 0] = (
                modvars[AM_TransEffAssumpTag][DP_Data, strat, DP_Perinatal] / 100
            )

        # Breastfeeding transmission
        # DualARV same for all CD4
        pmtct_transmission_rate[c_idx, 3, 1] = (
            modvars[AM_TransEffAssumpTag][DP_Data, DP_WHO2006DualARV, DP_BreastfeedingLT350] / 100
        )

        if cd4_cat <= DP_CD4_350_500:
            # High CD4 (>350)
            pmtct_transmission_rate[c_idx, 0, 1] = 0
            pmtct_transmission_rate[c_idx, 1, 1] = 0
            pmtct_transmission_rate[c_idx, 2, 1] = (
                modvars[AM_TransEffAssumpTag][DP_Data, DP_SingleDoseNev, DP_BreastfeedingLT350] / 100
            )
            pmtct_transmission_rate[c_idx, 4, 1] = 0
            pmtct_transmission_rate[c_idx, 5, 1] = 0
            pmtct_transmission_rate[c_idx, 6, 1] = 0
        else:
            # Low CD4 (<350)
            pmtct_transmission_rate[c_idx, 0, 1] = (
                modvars[AM_TransEffAssumpTag][DP_Data, DP_OptionA, DP_BreastfeedingGE350] / 100
            )
            pmtct_transmission_rate[c_idx, 1, 1] = (
                modvars[AM_TransEffAssumpTag][DP_Data, DP_OptionB, DP_BreastfeedingGE350] / 100
            )
            pmtct_transmission_rate[c_idx, 2, 1] = (
                modvars[AM_TransEffAssumpTag][DP_Data, DP_SingleDoseNev, DP_BreastfeedingGE350] / 100
            )
            # Note: Using LT350 for ART strategies (matches comment in Delphi)
            pmtct_transmission_rate[c_idx, 4, 1] = (
                modvars[AM_TransEffAssumpTag][DP_Data, DP_ARTStartPrePreg, DP_BreastfeedingLT350] / 100
            )
            pmtct_transmission_rate[c_idx, 5, 1] = (
                modvars[AM_TransEffAssumpTag][DP_Data, DP_ARTStartDurPreg, DP_BreastfeedingLT350] / 100
            )
            pmtct_transmission_rate[c_idx, 6, 1] = (
                modvars[AM_TransEffAssumpTag][DP_Data, DP_ARTStartDurPreg_Late, DP_BreastfeedingLT350] / 100
            )

    breastfeeding_duration_art = (
        modvars[AM_InfantFeedingOptionsTag][1:19, DP_InPMTCT, : (final_year_idx + 1)] / 100
    ).copy(order="F")

    breastfeeding_duration_no_art = (
        modvars[AM_InfantFeedingOptionsTag][1:19, DP_NotInPMTCT, : (final_year_idx + 1)] / 100
    ).copy(order="F")

    abortion = np.stack(
        [
            modvars[AM_PregTermAbortionTag][: (final_year_idx + 1)],
            modvars[AM_PregTermAbortionPerNumTag][: (final_year_idx + 1)],
        ],
        axis=0,
    ).copy(order="F")

    patients_reallocated = modvars[AM_PatientsReallocatedTag][: (final_year_idx + 1)].copy(order="F")

    hc_art_ltfu = (modvars[AM_PercInterruptedChildTag][: (final_year_idx + 1)] / 100).copy(order="F")

    # Only used when running the paed model standalone
    adult_female_hivnpop = np.zeros((ss["p_fertility_age_groups"], final_year_idx + 1), order="F")

    hc_age_specific_fertility_rate = _get_leapfrog_asfr(modvars, final_year_idx)

    # Direct input parameters (set to 0/empty - not used in normal operation)
    mat_prev_input = np.zeros(final_year_idx + 1, dtype=np.int32, order="F")
    mat_hiv_births = np.zeros(final_year_idx + 1, order="F")
    prop_lt200 = np.zeros(final_year_idx + 1, order="F")
    prop_gte350 = np.zeros(final_year_idx + 1, order="F")
    adult_female_infections = np.zeros((ss["p_fertility_age_groups"], final_year_idx + 1), order="F")
    total_births = np.zeros(final_year_idx + 1, order="F")
    infant_pop = np.zeros((ss["hc_infant"], ss["NS"], final_year_idx + 1), order="F")

    return {
        "hc_nosocomial": hc_nosocomial,
        "hc1_cd4_dist": hc1_cd4_dist,
        "hc1_cd4_mort": hc1_cd4_mort,
        "hc2_cd4_mort": hc2_cd4_mort,
        "hc1_cd4_prog": hc1_cd4_prog,
        "hc2_cd4_prog": hc2_cd4_prog,
        "ctx_val": ctx_val,
        "hc_art_elig_age": hc_art_elig_age,
        "hc_art_elig_cd4": hc_art_elig_cd4,
        "hc_art_mort_rr": hc_art_mort_rr,
        "hc1_art_mort": hc1_art_mort,
        "hc2_art_mort": hc2_art_mort,
        "hc_art_isperc": hc_art_is_percent,
        "hc_art_val": hc_art_val,
        "hc_art_init_dist": hc_art_init_dist,
        "PMTCT": pmtct,
        "vertical_transmission_rate": vertical_transmission_rate,
        "PMTCT_transmission_rate": pmtct_transmission_rate,
        "PMTCT_dropout": pmtct_dropout,
        "PMTCT_input_is_percent": pmtct_input_is_percent,
        "breastfeeding_duration_art": breastfeeding_duration_art,
        "breastfeeding_duration_no_art": breastfeeding_duration_no_art,
        "infant_pop": infant_pop,
        "mat_hiv_births": mat_hiv_births,
        "mat_prev_input": mat_prev_input,
        "prop_lt200": prop_lt200,
        "prop_gte350": prop_gte350,
        "ctx_val_is_percent": ctx_val_is_percent,
        "hc_art_is_age_spec": hc_art_is_age_spec,
        "abortion": abortion,
        "patients_reallocated": patients_reallocated,
        "hc_art_ltfu": hc_art_ltfu,
        "adult_female_infections": adult_female_infections,
        "adult_female_hivnpop": adult_female_hivnpop,
        "total_births": total_births,
        "ctx_effect": ctx_effect,
        "hc_art_start": hc_art_start,
        "hc_age_specific_fertility_rate": hc_age_specific_fertility_rate,
    }


def _get_leapfrog_asfr(modvars: Modvars, final_index: int) -> np.ndarray:
    """
    Get age-specific fertility rates in Leapfrog format.

    Args:
        modvars: Dictionary containing modvar data
        final_index: Number of time periods

    Returns:
        Array of shape (DP_NumFertileAges, final_index)
    """
    result = np.zeros((DP_NumFertileAges, final_index + 1), order="F")

    # Get ASFR data for 5-year age groups (15-19 to 45-49)
    asfr_5year = modvars[DP_ASFRTag][GB_A15_19 : GB_A45_49 + 1, : (final_index + 1)]
    asfr_sum = asfr_5year.sum(axis=0)

    # Distribute each 5-year rate across 5 single-year ages
    for a in range(DP_NumFertileAges):
        five_year_age_group = a // 5
        result[a, :] = (modvars[DP_TFRTag] * asfr_5year[five_year_age_group, :]) / (5.0 * asfr_sum)

    return result


def get_cd4_threshold_adult_idx(threshold: np.ndarray) -> np.ndarray:
    """
    Map CD4 threshold value(s) to CD4 category index/indices for adults.

    Args:
        threshold: Single threshold value or numpy array of thresholds

    Returns:
        Array of indices corresponding to CD4 categories
    """
    out = np.full_like(threshold, DP_CD4_GT500, dtype=np.int32, order="F")
    out[threshold <= 500] = DP_CD4_350_500
    out[threshold <= 350] = DP_CD4_250_349
    out[threshold <= 250] = DP_CD4_200_249
    # Update eligibility threshold from CD4<200 to CD4<250 to account for
    # additional proportion eligible with WHO Stage 3/4
    out[threshold <= 200] = DP_CD4_200_249
    out[threshold <= 100] = DP_CD4_50_99
    out[threshold <= 50] = DP_CD4_LT50

    return out


def get_cd4_threshold_child_idx(threshold: np.ndarray, p_type: int) -> np.ndarray:
    """
    Map CD4 threshold value(s) to CD4 category index/indices for children.

    Args:
        threshold: Single threshold value or numpy array of thresholds
        p_type: DP_Percent or DP_Number

    Returns:
        Array of indices corresponding to CD4 categories
    """
    if p_type == DP_Percent:
        out = np.full_like(threshold, DP_CD4_Per_GT30, dtype=np.int32, order="F")
        out[threshold <= 30] = DP_CD4_Per_26_30
        out[threshold <= 26] = DP_CD4_Per_21_25
        out[threshold <= 21] = DP_CD4_Per_16_20
        out[threshold <= 16] = DP_CD4_Per_11_15
        out[threshold <= 11] = DP_CD4_Per_5_10
        out[threshold <= 5] = DP_CD4_Per_LT5
    else:
        out = np.full_like(threshold, DP_CD4_Ped_GT1000, dtype=np.int32, order="F")
        out[threshold <= 1000] = DP_CD4_Ped_750_999
        out[threshold <= 750] = DP_CD4_Ped_500_749
        out[threshold <= 500] = DP_CD4_Ped_350_499
        out[threshold <= 350] = DP_CD4_Ped_200_349
        out[threshold <= 200] = DP_CD4_Ped_LT200

    return out
