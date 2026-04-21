"""Dimension specifications for Goals leapfrog output indicators.

Each indicator produced by leapfrog is an F-contiguous numpy array whose axes
are documented below. ``build_indicator_dims`` maps every indicator name to an
ordered tuple of `DimSpec`. A trailing ``year`` dimension is always
appended implicitly.

Use `list_indicators` to access both descriptions and dimension specs for
all indicators (e.g. for CLI display or documentation generation).
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


@dataclass
class IndicatorSpec:
    """Specification for one Goals output indicator.

    Args:
        description: Human-readable description of what the indicator measures.
        dims: Ordered dimension specs (outermost axis first), **excluding** the
            trailing ``year`` dimension which is always appended automatically.
    """

    description: str
    dims: Sequence[str | DimSpec]


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
# Common dimension combinations (year is always appended automatically)
# ---------------------------------------------------------------------------

_pag_ns = (_age, _sex)
_hds_hag_ns = (_adult_disease_stage, _hiv_age, _sex)
_hts_hds_hag_ns = (_treatment_stage, _adult_disease_stage, _hiv_age, _sex)


# ---------------------------------------------------------------------------
# Indicator registry
# ---------------------------------------------------------------------------

_INDICATOR_SPECS: dict[str, IndicatorSpec] = {
    # --- population totals ---
    "p_totpop": IndicatorSpec(
        "Total population by single year of age and sex.",
        dims=_pag_ns,
    ),
    "p_deaths_background_totpop": IndicatorSpec(
        "Background (non-HIV) deaths in the total population by age and sex.",
        dims=_pag_ns,
    ),
    "births": IndicatorSpec(
        "Total births.",
        dims=(),
    ),
    # --- HIV population ---
    "p_hivpop": IndicatorSpec(
        "HIV-positive population by age and sex.",
        dims=_pag_ns,
    ),
    "p_deaths_background_hivpop": IndicatorSpec(
        "Background (non-HIV) deaths in the HIV-positive population by age and sex.",
        dims=_pag_ns,
    ),
    "p_infections": IndicatorSpec(
        "New HIV infections by age and sex.",
        dims=_pag_ns,
    ),
    "p_hiv_deaths": IndicatorSpec(
        "HIV-related deaths by age and sex.",
        dims=_pag_ns,
    ),
    "p_deaths_excess_nonaids": IndicatorSpec(
        "Excess non-AIDS deaths (elevated mortality attributable to HIV) by age and sex.",
        dims=_pag_ns,
    ),
    "p_net_migration_hivpop": IndicatorSpec(
        "Number of HIV+ migrants by age and sex.",
        dims=_pag_ns,
    ),
    "p_deaths_nonaids_artpop": IndicatorSpec(
        "Non-AIDS deaths in the ART population by age and sex.",
        dims=_pag_ns,
    ),
    "p_deaths_nonaids_hivpop": IndicatorSpec(
        "Non-AIDS deaths in the HIV-positive population by age and sex.",
        dims=_pag_ns,
    ),
    "p_excess_deaths_nonaids_on_art": IndicatorSpec(
        "Excess non-AIDS deaths in HIV-positive individuals on ART by age and sex.",
        dims=_pag_ns,
    ),
    "p_excess_deaths_nonaids_no_art": IndicatorSpec(
        "Excess non-AIDS deaths in HIV-positive individuals not on ART by age and sex.",
        dims=_pag_ns,
    ),
    # --- adult HIV (h_ prefix) ---
    "h_hivpop": IndicatorSpec(
        "Adult PLHIV not on ART by CD4 disease stage, age (15+), and sex.",
        dims=_hds_hag_ns,
    ),
    "h_artpop": IndicatorSpec(
        "Adult PLHIV on ART by treatment duration stage, CD4 disease stage, age (15+), and sex.",
        dims=_hts_hds_hag_ns,
    ),
    "h_hiv_deaths_no_art": IndicatorSpec(
        "HIV-related deaths in adults not on ART by CD4 disease stage, age (15+), and sex.",
        dims=_hds_hag_ns,
    ),
    "h_deaths_excess_nonaids_no_art": IndicatorSpec(
        "Excess non-AIDS deaths in adults not on ART by CD4 disease stage, age (15+), and sex.",
        dims=_hds_hag_ns,
    ),
    "h_hiv_deaths_art": IndicatorSpec(
        "HIV-related deaths in adults on ART by treatment stage, CD4 disease stage, age (15+), and sex.",
        dims=_hts_hds_hag_ns,
    ),
    "h_deaths_excess_nonaids_on_art": IndicatorSpec(
        "Excess non-AIDS deaths in adults on ART by treatment stage, CD4 disease stage, age (15+), and sex.",
        dims=_hts_hds_hag_ns,
    ),
    "h_art_initiation": IndicatorSpec(
        "ART initiations in adults by CD4 disease stage, age (15+), and sex.",
        dims=_hds_hag_ns,
    ),
    # --- sub-annual HTS outputs ---
    "prevalence_15to49_hts": IndicatorSpec(
        "HIV prevalence among adults aged 15-49 at each sub-annual transmission step.",
        dims=(_hiv_step,),
    ),
    "incidence_15to49_hts": IndicatorSpec(
        "HIV incidence among adults aged 15-49 at each sub-annual transmission step.",
        dims=(_hiv_step,),
    ),
    "artcoverage_15to49_hts": IndicatorSpec(
        "ART coverage among HIV-positive adults aged 15-49 at each sub-annual transmission step.",
        dims=(_hiv_step,),
    ),
    # --- births and fertility ---
    "hiv_births_by_mat_age": IndicatorSpec(
        "HIV-exposed births by maternal age group.",
        dims=(_fertility_age,),
    ),
    "hiv_births": IndicatorSpec(
        "Number of births to WLHIV.",
        dims=(),
    ),
    # --- child HIV (hc_ prefix) ---
    "hc1_hivpop": IndicatorSpec(
        "PLHIV aged 0-4 not on ART by disease stage, transmission type, age, and sex.",
        dims=(_hc1_disease_stage, _transmission_type, _hc1_age, _sex),
    ),
    "hc2_hivpop": IndicatorSpec(
        "PLHIV aged 5-14 not on ART by disease stage, transmission type, age, and sex.",
        dims=(_hc2_disease_stage, _transmission_type, _hc2_age, _sex),
    ),
    "hc1_artpop": IndicatorSpec(
        "PLHIV aged 0-4 on ART by treatment stage, disease stage, age, and sex.",
        dims=(_treatment_stage, _hc1_disease_stage, _hc1_age, _sex),
    ),
    "hc2_artpop": IndicatorSpec(
        "PLHIV aged 5-14 on ART by treatment stage, disease stage, age, and sex.",
        dims=(_treatment_stage, _hc2_disease_stage, _hc2_age, _sex),
    ),
    "hc1_noart_aids_deaths": IndicatorSpec(
        "AIDS deaths among PLHIV aged 0-4 not on ART by disease stage, transmission type, age, and sex.",
        dims=(_hc1_disease_stage, _transmission_type, _hc1_age, _sex),
    ),
    "hc2_noart_aids_deaths": IndicatorSpec(
        "AIDS deaths among PLHIV aged 5-14 not on ART by disease stage, transmission type, age, and sex.",
        dims=(_hc2_disease_stage, _transmission_type, _hc2_age, _sex),
    ),
    "hc1_art_aids_deaths": IndicatorSpec(
        "AIDS deaths among PLHIV aged 0-4 on ART by treatment stage, disease stage, age, and sex.",
        dims=(_treatment_stage, _hc1_disease_stage, _hc1_age, _sex),
    ),
    "hc2_art_aids_deaths": IndicatorSpec(
        "AIDS deaths among PLHIV aged 5-14 on ART by treatment stage, disease stage, age, and sex.",
        dims=(_treatment_stage, _hc2_disease_stage, _hc2_age, _sex),
    ),
    "hc_art_init": IndicatorSpec(
        "Number of new ART initiates by 5-year age group.",
        dims=(_hc_ag_coarse,),
    ),
    "hc_art_need_init": IndicatorSpec(
        "Number of children who are eligible for ART by disease stage, transmission type, age, and sex.",
        dims=(_hc1_disease_stage, _transmission_type, _hc_ag_end, _sex),
    ),
    "ctx_need": IndicatorSpec(
        "Number of children needing co-trimoxazole (CTX) prophylaxis.",
        dims=(),
    ),
    "infection_by_type": IndicatorSpec(
        "New child HIV infections by transmission type, age, and sex.",
        dims=(_transmission_type, _hc1_age, _sex),
    ),
    # --- MTCT ---
    "mtct_by_source_tr": IndicatorSpec(
        "Mother-to-child HIV transmissions by source (maternal ART/PMTCT regimen) and transmission type.",
        dims=(_mtct_source, _transmission_type_expanded),
    ),
    "mtct_by_source_women": IndicatorSpec(
        "Mother-to-child HIV transmissions by source (maternal ART/PMTCT regimen).",
        dims=(_mtct_source,),
    ),
    "mtct_by_source_hc_infections": IndicatorSpec(
        "New child HIV infections by MTCT source and transmission type.",
        dims=(_mtct_source, _transmission_type_expanded),
    ),
    "pmtct_coverage_at_delivery": IndicatorSpec(
        "PMTCT coverage at delivery by regimen.",
        dims=(_pmtct_regimen,),
    ),
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def list_indicators() -> dict[str, IndicatorSpec]:
    """Return all supported indicator names and their specifications.

    The returned dict preserves insertion order (population totals first,
    then adult HIV, HTS, births, child HIV, and MTCT).  Each value is an
    ``IndicatorSpec`` with a human-readable ``description`` and an
    ordered tuple of ``DimSpec`` objects in ``dims`` (outermost axis
    first, excluding the trailing ``year`` dimension).
    """
    return _INDICATOR_SPECS


def build_indicator_dims(base_year: int) -> IndicatorDims:
    """Return per-indicator dimension specs for all known Goals output indicators.

    A trailing ``year`` dimension is always included.

    Args:
        base_year: First projection year.  Year indices are stored as actual
            calendar years (index + base_year).
    """
    year = DimSpec("year", offset=base_year)
    return {name: (*spec.dims, year) for name, spec in _INDICATOR_SPECS.items()}
