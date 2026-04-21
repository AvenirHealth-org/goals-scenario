"""Dimension specifications for Goals leapfrog output indicators.

Each indicator produced by leapfrog is an F-contiguous numpy array whose axes
are documented below.  ``build_indicator_dims`` maps every indicator name to an
ordered tuple of :class:`DimSpec`. A trailing ``year`` dimension is always
appended implicitly.
"""

import difflib
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field

from leapfrog_goals import get_goals_ss
from loguru import logger


@dataclass
class DimSpec:
    """Specification for one dimension in the long-format output.

    Args:
        name: Column name in the output table.
        labels: If given, the dimension is stored as a dictionary-encoded
            column (parquet dict / R factor) using these string labels.
            ``labels[i]`` is the label for index ``i``.
        offset: Integer added to the raw index before storage.  Use
            ``offset=base_year`` so that year indices are stored as actual
            calendar years rather than zero-based offsets.
    """

    name: str
    labels: list[str] | None = field(default=None)
    offset: int = 0


# Mapping of indicator name to per-dimension specs.
# String entries are shorthand for DimSpec(name=entry).
IndicatorDims = Mapping[str, Sequence[str | DimSpec]]


class DimNamesMismatchError(ValueError):
    def __init__(self, provided: int, expected: int) -> None:
        super().__init__(
            f"Expected {expected} dimension spec(s) to match the array shape, "
            f"but got {provided}. Check that specs are in C axis order and "
            "exclude the simulation axis."
        )


class UnknownIndicatorError(ValueError):
    def __init__(self, indicator: str, supported: list[str] | None = None) -> None:
        logger.debug("Dimension spec missing for indicator '{}'. Add it to the indicator_dims mapping.", indicator)
        if supported:
            close = difflib.get_close_matches(indicator, supported, n=3, cutoff=0.6)
            if close:
                detail = f" Did you mean: {', '.join(close)}?"
            else:
                detail = f" Supported indicators are: {', '.join(sorted(supported))}."
        else:
            detail = ""
        super().__init__(f"Unknown indicator '{indicator}'.{detail}")


# ---------------------------------------------------------------------------
# Shared dimension specs (SS:: constants from the leapfrog-goals model)
# TODO: Can we get this from leapfrog-goals? We'll have to keep this in
# sync at the moment, it could be nice to export this from the metadata
# somehow.
# ---------------------------------------------------------------------------

ss = get_goals_ss()


# SS::NS - sex
_sex = DimSpec("sex", labels=["male", "female"])

# SS::pAG - 81 population age groups (0 - 80+)
_age = DimSpec("age")

# SS::hAG - 66 HIV adult age groups (15 - 80+)
_hiv_age = DimSpec("age", offset=int(ss["pAG"] - ss["hAG"]))

# SS::hDS - HIV disease stages (CD4 categories)
_adult_disease_stage = DimSpec(
    "disease_stage", labels=[">500", "350-500", "250-349", "200-249", "100-199", "50-99", "<50"]
)

# SS::hTS - HIV treatment stages
_treatment_stage = DimSpec("treatment_stage", labels=["0 to 6 months", "7 to 12 months", "12+ months"])

# 10 sub-annual HIV transmission steps
_hiv_step = DimSpec("hiv_step")

# SS::hAG_fertility - 35 maternal fertility age groups
_fertility_age = DimSpec("age", offset=int(ss["p_fertility_age_groups"]))

# SS::hc1DS - disease stages for child 0 - 4 population
_hc1_disease_stage = DimSpec(
    "disease_stage_child_0to4", labels=[">30", "26-30", "21-25", "16-20", "11-15", "5-10", "<5"]
)

# SS::hc2DS - disease stages for child 5 - 14 population
_hc2_disease_stage = DimSpec(
    "disease_stage_child5to14", labels=[">1000", "750-999", "500-749", "350-499", "200-349", "<200"]
)

# SS::hc1AG - age groups for child 0 - 4 population
_hc1_age = DimSpec("age")

# SS::hc2AG - age groups for child 5 - 14 population
_hc2_age = DimSpec("age", offset=int(ss["hc2_agestart"]))

# SS::hcTT - child HIV transmission types
_transmission_type = DimSpec(
    "transmission_type",
    labels=[
        "Perinatal",
        "Breastfeeding 6 weeks - 2 months",
        "Breastfeeding 6 - 11 months",
        "Breastfeeding 12 - 23 months",
    ],
)

# SS::hcTT_expanded - expanded child transmission type
_transmission_type_expanded = DimSpec(
    "transmission_type",
    labels=[
        "Perinatal",
        "Breastfeeding 6 weeks - 2 months",
        "Breastfeeding 6 - 11 months",
        "Breastfeeding 12 - 23 months",
        "Breastfeeding 24-36 months",
    ],
)

# SS::hcAG_coarse
_hc_ag_coarse = DimSpec("hc_ag_coarse", labels=["0-14", "0-4", "5-9", "10-14"])

# SS::hcAG_end age when child age groups end and adult age groups start
_hc_ag_end = DimSpec("age")

# SS::hPS - PMTCT regimens at delivery
_pmtct_regimen = DimSpec(
    "pmtct_regimen",
    labels=["Option A", "Option B", "SDNVP", "Dual ARV", "Option B+ before", "Option B+ early", "Option B+ Late"],
)

# SS::mtct_source - source of mother-to-child transmission
_mtct_source = DimSpec(
    "mtct_source",
    labels=[
        "Option A",
        "Option B",
        "SDNVP",
        "Dual ARV",
        "Option B+ before",
        "Option B+ early",
        "Option B+ Late",
        "No ART",
        "Mother seroconverted",
        "B+ Before dropout",
        "B+ During dropout",
    ],
)


# ---------------------------------------------------------------------------
# Indicator dimension map
# ---------------------------------------------------------------------------


def build_indicator_dims(base_year: int) -> IndicatorDims:
    """Return per-indicator dimension specs for all known Goals output indicators.

    A trailing ``year`` dimension is always included.

    Args:
        base_year: First projection year.  Year indices are stored as actual
            calendar years (index + base_year).
    """
    year = DimSpec("year", offset=base_year)

    # Common axis combinations
    _pag_ns = (_age, _sex, year)
    _hds_hag_ns = (_adult_disease_stage, _hiv_age, _sex, year)
    _hts_hds_hag_ns = (_treatment_stage, _adult_disease_stage, _hiv_age, _sex, year)

    return {
        # --- population totals ---
        "p_totpop": _pag_ns,
        "p_deaths_background_totpop": _pag_ns,
        "births": (year,),
        # --- HIV population ---
        "p_hivpop": _pag_ns,
        "p_deaths_background_hivpop": _pag_ns,
        "p_infections": _pag_ns,
        "p_hiv_deaths": _pag_ns,
        "p_deaths_excess_nonaids": _pag_ns,
        "p_net_migration_hivpop": _pag_ns,
        "p_deaths_nonaids_artpop": _pag_ns,
        "p_deaths_nonaids_hivpop": _pag_ns,
        "p_excess_deaths_nonaids_on_art": _pag_ns,
        "p_excess_deaths_nonaids_no_art": _pag_ns,
        # --- adult HIV (h_ prefix) ---
        "h_hivpop": _hds_hag_ns,
        "h_artpop": _hts_hds_hag_ns,
        "h_hiv_deaths_no_art": _hds_hag_ns,
        "h_deaths_excess_nonaids_no_art": _hds_hag_ns,
        "h_hiv_deaths_art": _hts_hds_hag_ns,
        "h_deaths_excess_nonaids_on_art": _hts_hds_hag_ns,
        "h_art_initiation": _hds_hag_ns,
        # --- sub-annual HTS outputs ---
        "prevalence_15to49_hts": (_hiv_step, year),
        "incidence_15to49_hts": (_hiv_step, year),
        "artcoverage_15to49_hts": (_hiv_step, year),
        # --- births and fertility ---
        "hiv_births_by_mat_age": (_fertility_age, year),
        "hiv_births": (year,),
        # --- child HIV (hc_ prefix) ---
        "hc1_hivpop": (_hc1_disease_stage, _transmission_type, _hc1_age, _sex, year),
        "hc2_hivpop": (_hc2_disease_stage, _transmission_type, _hc2_age, _sex, year),
        "hc1_artpop": (_treatment_stage, _hc1_disease_stage, _hc1_age, _sex, year),
        "hc2_artpop": (_treatment_stage, _hc2_disease_stage, _hc2_age, _sex, year),
        "hc1_noart_aids_deaths": (_hc1_disease_stage, _transmission_type, _hc1_age, _sex, year),
        "hc2_noart_aids_deaths": (_hc2_disease_stage, _transmission_type, _hc2_age, _sex, year),
        "hc1_art_aids_deaths": (_treatment_stage, _hc1_disease_stage, _hc1_age, _sex, year),
        "hc2_art_aids_deaths": (_treatment_stage, _hc2_disease_stage, _hc2_age, _sex, year),
        "hc_art_init": (_hc_ag_coarse, year),
        "hc_art_need_init": (_hc1_disease_stage, _transmission_type, _hc_ag_end, _sex, year),
        "ctx_need": (year,),
        "infection_by_type": (_transmission_type, _hc1_age, _sex, year),
        # --- MTCT ---
        "mtct_by_source_tr": (_mtct_source, _transmission_type_expanded, year),
        "mtct_by_source_women": (_mtct_source, year),
        "mtct_by_source_hc_infections": (_mtct_source, _transmission_type_expanded, year),
        "pmtct_coverage_at_delivery": (_pmtct_regimen, year),
    }
