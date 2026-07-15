# =============================================================================
# generate_scenarios.R
#
# Builds scenario_definitions.json for the Goals scenario analysis tool.
#
# For each scenario (= one branch of the success/failure tree over R&D products):
#   - SOC products are always included.
#   - R&D products are included on "success" and omitted on "failure".
#   - The full 2^(n R&D products) combinations are generated.
#   - Each combination has a "branch_probability" computed from per-product PTRS.
#   - Each combination's "id" is "{branch_id}_A{i}" (e.g. "B000000011_A1").
#   - "branch_probability", "market_outcome", and "country" are written as extra
#     fields on each scenario object. The Goals analysis tool ignores them
#     (extra="ignore" in the Python model), but they are useful for downstream
#     probability weighting in R.
#
# Product identity vs. canonical name:
#   - Each entry in products_input.json may have an optional "id" field. This is
#     the internal R&D product name used in RND_PRODUCTS, PTRS, and market dynamics.
#     If omitted, the "product" field is used as the id.
#   - The "product" field is the canonical Goals product name (must match the
#     Python Literal exactly, e.g. "Vaccine").
#   - Each product in RND_PRODUCTS must map to a unique canonical product name.
#
# Country archetypes:
#   - Countries are grouped by archetype profile (the set of coverage multipliers
#     across all target populations). Each branch produces one scenario per profile
#     group, with pjnz_names listing that group's countries and each target's value
#     (target_coverage, or target_initiation_rate for Adult ART) scaled by the
#     archetype multiplier for that target population.
#   - Products with mixed per-target multipliers are split into one intervention
#     entry per target, each with its own scaled value.
#   - Scenario ids are suffixed _A{i} for archetype group i.
#   - Long-acting treatment's target_coverage lives in "parameters" (like AHD
#     treatment / POC tests below), so archetype and market-dynamic scaling
#     apply to it via the same "*" archetype lookup.
#
# Market dynamics:
#   - trigger_products and affected_product use CANONICAL product names (e.g.
#     "Vaccine"), so a rule fires regardless of which internal variant succeeded.
#   - When all trigger products are present, the affected product's
#     target_coverage.mean is multiplied by coverage_multiplier (multiplicative).
#
# Inputs:
#   - products_input.json        product definitions with per-type parameters
#   - countries_input.csv        Country, Archetype
#   - archetypes_input.csv       Archetype, Target Population, coverage_multiplier
#   - ptrs_input.csv             Product, ptrs  (uses internal product id)
#   - market_dynamics_input.csv  trigger_products (";"-sep canonical names),
#                                affected_product (canonical name),
#                                coverage_multiplier, type
#
# Output:
#   - scenario_definitions.json  Goals scenario definition JSON
# =============================================================================

# ---- Config ------------------------------------------------------------------

SOC_PRODUCTS <- c(
  "Oral PrEP (daily)",
  "Injectable PrEP (2 month)",
  "Adult ART"
)

# R&D products.
# NOT YET INCLUDED:
#   "Therapeutic vaccine"            — not added yet (TODO).
#   2nd "Long-acting treatment" variant — only one variant included for now.
#   "Vaginal microbiome modification" / "Cure (neonates)" — new model products
#                                       available to adopt, omitted for now.
RND_PRODUCTS <- c(
  "Injectable PrEP (6 month)",
  "Oral PrEP (monthly)",
  "Implantable PrEP",
  "PEP",
  "Vaccine",
  "Long-acting treatment",
  "AHD treatment",
  "Cure (adults and children)",
  "POC CD4 test",
  "POC VL test"
)

PRODUCTS_INPUT_PATH        <- "products_input.json"
COUNTRIES_INPUT_PATH       <- "countries_input.csv"
ARCHETYPES_INPUT_PATH      <- "archetypes_input.csv"
PTRS_INPUT_PATH            <- "ptrs_input.csv"
MARKET_DYNAMICS_INPUT_PATH <- "market_dynamics_input.csv"
OUTPUT_PATH                <- "scenario_definitions.json"

# ---- Dummy input data --------------------------------------------------------
# Replace with real data when available.

create_dummy_products <- function(path) {
  # Each entry:
  #   id (optional) : internal name matching RND_PRODUCTS / ptrs_input.csv.
  #                   If absent, "product" is used as the id.
  #   product       : canonical Goals product name (Python Literal, e.g. "Vaccine")
  #   targets       : product-type-specific list of target objects (see below);
  #                   omit entirely for AHD treatment and POC tests.
  #   parameters    : product-type-specific
  #
  # IMPORTANT — coverage location (Goals model "coverage fix"):
  #   For products WITH targets (PrEP/PEP, Vaccine, Cure, Adult ART), the
  #   per-target value {mean, sd} now lives INSIDE EACH TARGET, not in
  #   "parameters". This is "target_coverage" for every product except Adult ART,
  #   which uses "target_initiation_rate" (an annual ART initiation rate). The
  #   target-less products (AHD treatment, POC tests, Long-acting treatment) keep
  #   "target_coverage" (and "target_year") in "parameters" instead, and must NOT
  #   have a "targets" field at all (the Goals schema forbids it for these).
  #
  # Valid canonical product names:
  #   PrEP:    "Oral PrEP (daily)", "Oral PrEP (monthly)",
  #            "Injectable PrEP (1 month)", "Injectable PrEP (2 month)",
  #            "Injectable PrEP (6 month)", "Oral PrEP plus contraceptive",
  #            "PrEP ring", "Implantable PrEP", "bNABs", "PEP"
  #   Other:   "Vaccine", "Cure (adults and children)", "Cure (neonates)",
  #            "Vaginal microbiome modification", "AHD treatment",
  #            "POC CD4 test", "POC VL test", "Long-acting treatment", "Adult ART"
  #
  # Target shapes by product family:
  #   PrEP / PEP        : {risk_group, sex, target_coverage}
  #   Vaccine / Cure    : {risk_group, sex (optional), target_coverage}
  #                       risk_group may be "PLHIV" (then sex must be "Both" or omitted)
  #   Adult ART         : {sex, target_initiation_rate}     (no risk_group)
  #   Long-acting tx    : NO targets list; target_year/target_coverage live in
  #                       "parameters" (same shape as AHD treatment / POC tests).
  #
  # Risk groups (PrEP / Vaccine / Cure):
  #   "Low risk heterosexual", "Medium risk heterosexual", "High risk heterosexual",
  #   "People who inject drugs", "Men who have sex with men", and (Vaccine/Cure) "PLHIV"
  #   sex: "Male", "Female", "Both"
  #
  # Vaccine parameter Literals:
  #   vaccine_action_type: "Take" | "Degree"
  #   targeting: "Vaccinate without HIV testing"
  #            | "Vaccinate only HIV-negative individuals"
  #   TODO: confirm the correct targeting value for the vaccine product.

  products <- list(
    # --- SOC ---
    list(
      product = "Oral PrEP (daily)",
      targets = list(
        list(risk_group = "High risk heterosexual", sex = "Female",
             target_coverage = list(mean = 0.30, sd = 0.05)),
        list(risk_group = "Men who have sex with men", sex = "Male",
             target_coverage = list(mean = 0.30, sd = 0.05))
      ),
      parameters = list(
        efficacy    = list(mean = 0.95, sd = 0.03),
        adherence   = list(mean = 0.85, sd = 0.05),
        target_year = list(mean = 2028, sd = 2)
      )
    ),
    list(
      product = "Injectable PrEP (2 month)",
      targets = list(
        list(risk_group = "High risk heterosexual", sex = "Female",
             target_coverage = list(mean = 0.20, sd = 0.05)),
        list(risk_group = "Men who have sex with men", sex = "Male",
             target_coverage = list(mean = 0.20, sd = 0.05))
      ),
      parameters = list(
        efficacy    = list(mean = 0.99, sd = 0.01),
        adherence   = list(mean = 0.95, sd = 0.03),
        target_year = list(mean = 2028, sd = 2)
      )
    ),
    # Adult ART: standard-of-care treatment backbone. Targets are by sex only
    # (no risk_group); parameters carry only target_year. ART entry is an annual
    # initiation rate (the PJNZ must be in "initiation rate" mode), not coverage.
    list(
      product = "Adult ART",
      targets = list(
        list(sex = "Female", target_initiation_rate = list(mean = 0.85, sd = 0.05)),
        list(sex = "Male",   target_initiation_rate = list(mean = 0.85, sd = 0.05))
      ),
      parameters = list(
        target_year = list(mean = 2030, sd = 2)
      )
    ),
    # --- R&D ---
    list(
      product = "Injectable PrEP (6 month)",
      targets = list(
        list(risk_group = "High risk heterosexual", sex = "Female",
             target_coverage = list(mean = 0.20, sd = 0.05)),
        list(risk_group = "Men who have sex with men", sex = "Male",
             target_coverage = list(mean = 0.20, sd = 0.05)),
        list(risk_group = "Medium risk heterosexual", sex = "Female",
             target_coverage = list(mean = 0.20, sd = 0.05))
      ),
      parameters = list(
        efficacy    = list(mean = 0.99, sd = 0.01),
        adherence   = list(mean = 0.99, sd = 0.01),
        target_year = list(mean = 2030, sd = 2)
      )
    ),
    list(
      product = "Oral PrEP (monthly)",
      targets = list(
        list(risk_group = "High risk heterosexual", sex = "Female",
             target_coverage = list(mean = 0.20, sd = 0.05)),
        list(risk_group = "Medium risk heterosexual", sex = "Female",
             target_coverage = list(mean = 0.20, sd = 0.05))
      ),
      parameters = list(
        efficacy    = list(mean = 0.95, sd = 0.03),
        adherence   = list(mean = 0.95, sd = 0.03),
        target_year = list(mean = 2028, sd = 2)
      )
    ),
    list(
      product = "Implantable PrEP",
      targets = list(
        list(risk_group = "High risk heterosexual", sex = "Female",
             target_coverage = list(mean = 0.15, sd = 0.05))
      ),
      parameters = list(
        efficacy    = list(mean = 0.98, sd = 0.02),
        adherence   = list(mean = 0.99, sd = 0.01),
        target_year = list(mean = 2032, sd = 2)
      )
    ),
    # PEP (post-exposure prophylaxis): a PrEP-family product. From the original
    # script's "One month pill for PEP".
    list(
      product = "PEP",
      targets = list(
        list(risk_group = "High risk heterosexual", sex = "Female",
             target_coverage = list(mean = 0.10, sd = 0.03))
      ),
      parameters = list(
        efficacy    = list(mean = 0.90, sd = 0.05),
        adherence   = list(mean = 0.85, sd = 0.05),
        target_year = list(mean = 2030, sd = 2)
      )
    ),
    # TODO: confirm whether targeting should be "Vaccinate without HIV testing"
    # or "Vaccinate only HIV-negative individuals" for this product.
    list(
      product = "Vaccine",
      targets = list(
        list(risk_group = "Medium risk heterosexual", sex = "Female",
             target_coverage = list(mean = 0.50, sd = 0.10)),
        list(risk_group = "Medium risk heterosexual", sex = "Male",
             target_coverage = list(mean = 0.50, sd = 0.10))
      ),
      parameters = list(
        target_year                          = list(mean = 2035, sd = 3),
        reduction_in_susceptibility          = list(mean = 0.70, sd = 0.10),
        reduction_in_infectiousness          = list(mean = 0.50, sd = 0.10),
        increase_in_progression_time_to_aids = list(mean = 0.30, sd = 0.05),
        vaccine_duration_years               = list(mean = 10.0, sd = 2.0),
        vaccine_action_type                  = "Take",
        targeting                            = "Vaccinate without HIV testing"
      )
    ),
    # Cure: targets PLHIV (sex omitted; PLHIV must be sex "Both" or unset).
    list(
      product = "Cure (adults and children)",
      targets = list(
        list(risk_group = "PLHIV", target_coverage = list(mean = 0.20, sd = 0.05))
      ),
      parameters = list(
        target_year      = list(mean = 2035, sd = 3),
        efficacy         = list(mean = 0.85, sd = 0.05),
        duration_of_cure = list(mean = 5.0,  sd = 1.0)
      )
    ),
    # Long-acting treatment: NO targets field (Goals schema forbids it);
    # target_year/target_coverage live in parameters, like AHD treatment / POC
    # tests below. Included as a single variant.
    list(
      product = "Long-acting treatment",
      parameters = list(
        target_year                  = list(mean = 2030, sd = 2),
        target_coverage              = list(mean = 0.70, sd = 0.08),
        interruption_rate_reduction  = list(mean = 0.25, sd = 0.05),
        viral_load_suppression_ratio = list(mean = 0.80, sd = 0.05)
      )
    ),
    # AHD treatment and POC tests: NO targets field (Goals schema forbids it);
    # target_coverage stays in parameters.
    list(
      product = "AHD treatment",
      parameters = list(
        target_year            = list(mean = 2029, sd = 2),
        target_coverage        = list(mean = 0.80, sd = 0.08),
        reduction_in_mortality = list(mean = 0.60, sd = 0.10)
      )
    ),
    list(
      product = "POC CD4 test",
      parameters = list(
        target_year     = list(mean = 2029, sd = 2),
        target_coverage = list(mean = 0.70, sd = 0.08),
        effect          = list(mean = 0.25, sd = 0.0)
      )
    ),
    list(
      product = "POC VL test",
      parameters = list(
        target_year     = list(mean = 2029, sd = 2),
        target_coverage = list(mean = 0.70, sd = 0.08),
        effect          = list(mean = 0.12, sd = 0.0)
      )
    )
  )

  jsonlite::write_json(products, path, auto_unbox = TRUE, pretty = TRUE)
  message("Wrote dummy ", path)
}

create_dummy_countries <- function(path) {
  readr::write_csv(data.frame(
    Country   = c("Kenya", "South Africa", "Nigeria", "Ukraine"),
    Archetype = c("Generalized - high", "Generalized - high",
                  "Generalized - low",  "Concentrated - high")
  ), path)
  message("Wrote dummy ", path)
}

create_dummy_archetypes <- function(path) {
  # Canonical population names must match Python RiskGroup Literal values.
  readr::write_csv(tibble::tribble(
    ~Archetype,             ~`Target Population`,        ~coverage_multiplier,
    "Generalized - high",   "Medium risk heterosexual",  1.00,
    "Generalized - high",   "*",                         1.00,
    "Generalized - low",    "*",                         1.00,
    "Concentrated - high",  "Medium risk heterosexual",  0.25,
    "Concentrated - high",  "*",                         1.00,
    "Concentrated - low",   "Medium risk heterosexual",  0.00,
    "Concentrated - low",   "*",                         1.00
  ), path)
  message("Wrote dummy ", path)
}

create_dummy_ptrs <- function(path) {
  # Uses internal product ids (the "id" field, defaulting to "product").
  # One row per R&D product, in RND_PRODUCTS order:
  #   Injectable PrEP (6 month), Oral PrEP (monthly), Implantable PrEP, PEP,
  #   Vaccine, Cure (adults and children), Long-acting treatment, AHD treatment,
  #   POC CD4 test, POC VL test
  readr::write_csv(tibble::tibble(
    Product = RND_PRODUCTS,
    ptrs    = c(0.90, 0.70, 0.40, 0.50, 0.17, 0.10, 0.50, 0.30, 0.60, 0.60)
  ), path)
  message("Wrote dummy ", path)
}

create_dummy_market_dynamics <- function(path) {
  # trigger_products and affected_product use CANONICAL product names (e.g.
  # "Vaccine"), so a rule fires when any matching variant is present.
  # "Long-acting treatment" now carries a target_coverage (in parameters), so
  # it can be used as either a trigger or an affected_product.
  readr::write_csv(tibble::tribble(
    ~trigger_products,                                       ~affected_product,            ~coverage_multiplier, ~type,
    "Vaccine",                                               "Oral PrEP (daily)",          0.50,                 "cannibalization",
    "Vaccine",                                               "Injectable PrEP (2 month)",  0.50,                 "cannibalization",
    "Vaccine",                                               "Injectable PrEP (6 month)",  0.50,                 "cannibalization",
    "Implantable PrEP",                                      "Oral PrEP (daily)",          0.10,                 "cannibalization",
    "Cure (adults and children)",                            "Adult ART",                  0.10,                 "cannibalization",
    "Injectable PrEP (6 month);Oral PrEP (monthly)",         "Injectable PrEP (6 month)",  1.10,                 "synergy",
    "Injectable PrEP (6 month);Oral PrEP (monthly)",         "Oral PrEP (monthly)",        1.10,                 "synergy"
  ), path)
  message("Wrote dummy ", path)
}

# ---- Loaders -----------------------------------------------------------------

load_products <- function(path) {
  if (!file.exists(path)) create_dummy_products(path)
  products <- jsonlite::read_json(path, simplifyVector = FALSE)
  # Resolve id: explicit "id" field if present, otherwise fall back to "product".
  resolve_id <- function(entry) if (!is.null(entry$id)) entry$id else entry$product
  ids         <- vapply(products, resolve_id, character(1))
  expected    <- c(SOC_PRODUCTS, RND_PRODUCTS)
  missing_ids <- setdiff(expected, ids)
  if (length(missing_ids) > 0) {
    warning("products_input.json has no entry for id(s): ",
            paste(missing_ids, collapse = ", "))
  }
  stats::setNames(products, ids)
}

load_countries <- function(path) {
  if (!file.exists(path)) create_dummy_countries(path)
  df <- readr::read_csv(path, show_col_types = FALSE)
  if (!"Country" %in% names(df)) stop("countries_input.csv must have a 'Country' column.")
  if (!"Archetype" %in% names(df)) {
    message("countries_input.csv has no 'Archetype' column; assigning '_default' archetype.")
    df$Archetype <- "_default"
  }
  df
}

load_archetypes <- function(path) {
  if (!file.exists(path)) create_dummy_archetypes(path)
  df <- readr::read_csv(path, show_col_types = FALSE)
  for (col in c("Archetype", "Target Population", "coverage_multiplier")) {
    if (!col %in% names(df)) stop("archetypes_input.csv must have a '", col, "' column.")
  }
  df
}

load_ptrs <- function(path) {
  if (!file.exists(path)) create_dummy_ptrs(path)
  df <- readr::read_csv(path, show_col_types = FALSE)
  for (col in c("Product", "ptrs")) {
    if (!col %in% names(df)) stop("ptrs_input.csv must have a '", col, "' column.")
  }
  missing <- setdiff(RND_PRODUCTS, df$Product)
  if (length(missing) > 0) stop("ptrs_input.csv missing PTRS for: ", paste(missing, collapse = ", "))
  df
}

load_market_dynamics <- function(path) {
  if (!file.exists(path)) create_dummy_market_dynamics(path)
  df <- readr::read_csv(path, show_col_types = FALSE)
  for (col in c("trigger_products", "affected_product", "coverage_multiplier")) {
    if (!col %in% names(df)) stop("market_dynamics_input.csv must have a '", col, "' column.")
  }
  if (!"type" %in% names(df)) df$type <- NA_character_
  # Pre-split trigger_products once (it's constant per rule but consulted for
  # every scenario) to avoid repeated stringr calls in the hot loop.
  df$triggers <- lapply(df$trigger_products, function(s) {
    stringr::str_trim(stringr::str_split(s, ";")[[1]])
  })
  df
}

# ---- Scenario construction ---------------------------------------------------

# Precompute archetype × target-population -> multiplier as a named numeric
# vector for O(1) lookups. Done once per run; passed to archetype_multiplier in
# place of the data frame (per-call dplyr::filter otherwise dominates runtime).
# Keys are "{archetype}\u001f{target population}" (\u001f = unit separator, which
# cannot appear in a name).
archetype_lookup <- function(archetypes_df) {
  keys <- paste(archetypes_df$Archetype, archetypes_df$`Target Population`, sep = "\u001f")
  stats::setNames(archetypes_df$coverage_multiplier, keys)
}

# Lookup: archetype + target population -> coverage multiplier.
# If no row matches the specific target population, fall back to the
# archetype's "*" row; if that's also missing, return 1.
archetype_multiplier <- function(lookup, archetype, target_pop) {
  v <- lookup[paste(archetype, target_pop, sep = "\u001f")]
  if (!is.na(v)) return(unname(v))
  w <- lookup[paste(archetype, "*", sep = "\u001f")]
  if (!is.na(w)) return(unname(w))
  1
}

# For one scenario (a set of products present), compute the product-level
# market-dynamic multiplier from ALL applicable rules (combined multiplicatively).
# Market dynamics operates on CANONICAL product names so that a "Vaccine" rule
# fires regardless of which vaccine variant (prophylactic / therapeutic) succeeded.
market_dynamic_multipliers <- function(canonical_products_in_scenario, market_df) {
  out <- stats::setNames(rep(1, length(canonical_products_in_scenario)),
                         canonical_products_in_scenario)
  if (nrow(market_df) == 0) return(out)
  for (i in seq_len(nrow(market_df))) {
    triggers <- market_df$triggers[[i]]  # pre-split in load_market_dynamics
    affected <- market_df$affected_product[i]
    if (all(triggers %in% canonical_products_in_scenario) &&
        affected %in% canonical_products_in_scenario) {
      out[affected] <- out[affected] * market_df$coverage_multiplier[i]
    }
  }
  out
}

# Build all 2^k success/failure patterns over RND_PRODUCTS as a logical matrix.
# Column order matches RND_PRODUCTS; rows are ordered by ascending number of
# successes for readability.
rnd_success_matrix <- function(rnd_products) {
  k    <- length(rnd_products)
  grid <- expand.grid(rep(list(c(FALSE, TRUE)), k), KEEP.OUT.ATTRS = FALSE)
  names(grid) <- rnd_products
  grid <- grid[order(rowSums(grid)), , drop = FALSE]
  rownames(grid) <- NULL
  as.matrix(grid)
}

# Branch ID: "B" + one bit per R&D product (in REVERSE RND_PRODUCTS order:
# last product is the first bit, first product is the last bit) + trailing "1".
branch_id <- function(success_row) {
  paste0("B", paste0(as.integer(rev(success_row)), collapse = ""), "1")
}

# market_outcome string: comma-separated names of successful R&D products,
# or "SOC only" if none succeeded.
market_outcome_string <- function(success_row, rnd_products) {
  picked <- rnd_products[as.logical(success_row)]
  if (length(picked) == 0) "SOC only" else paste(picked, collapse = ", ")
}

# Probability of a branch: product over R&D products of (ptrs if success
# else 1-ptrs).
branch_probability <- function(success_row, ptrs_named) {
  s <- as.logical(success_row)
  p <- ptrs_named[names(success_row)]
  prod(ifelse(s, p, 1 - p))
}

build_intervention <- function(prod_entry) {
  if (!is.null(prod_entry$targets) && length(prod_entry$targets) > 0) {
    list(product    = prod_entry$product,
         targets    = prod_entry$targets,
         parameters = prod_entry$parameters)
  } else {
    list(product    = prod_entry$product,
         parameters = prod_entry$parameters)
  }
}

# Per-target value fields scaled by archetype/market multipliers. Adult ART uses
# "target_initiation_rate" (an annual ART initiation rate); every other product
# with targets uses "target_coverage". Both are scaled identically.
TARGET_VALUE_FIELDS <- c("target_coverage", "target_initiation_rate")

# Build a single intervention for one product entry, scaling its target value by
# both the per-target archetype multiplier and the product-level market-dynamic
# multiplier.
#
# The scaled value lives in one of two places (see create_dummy_products):
#   - per-target field (PrEP/PEP, Vaccine, Cure -> "target_coverage";
#     Adult ART -> "target_initiation_rate"): each target is scaled by
#     archetype_multiplier(archetype, its risk_group) * md_mult. Targets with no
#     risk_group (Adult ART) use the "*" archetype row.
#   - parameters$target_coverage (AHD treatment, POC tests, Long-acting
#     treatment): scaled by archetype_multiplier(archetype, "*") * md_mult.
build_intervention_scaled <- function(entry, arch_lookup, archetype, md_mult) {
  if (!is.null(entry$targets) && length(entry$targets) > 0) {
    entry$targets <- lapply(entry$targets, function(t) {
      pop <- if (!is.null(t$risk_group)) t$risk_group else "*"
      am  <- archetype_multiplier(arch_lookup, archetype, pop)
      for (field in TARGET_VALUE_FIELDS) {
        if (!is.null(t[[field]])) {
          t[[field]]$mean <- t[[field]]$mean * am * md_mult
        }
      }
      t
    })
  } else if (!is.null(entry$parameters$target_coverage)) {
    am <- archetype_multiplier(arch_lookup, archetype, "*")
    entry$parameters$target_coverage$mean <-
      entry$parameters$target_coverage$mean * am * md_mult
  }
  build_intervention(entry)
}

# Build a scenario object for one branch × archetype-group combination.
# Returns a list of length 1 (one scenario).
build_scenarios_for_branch <- function(success_row, products_named, pjnz_names,
                                       arch_lookup, archetype, arch_idx,
                                       market_df, ptrs_named) {
  rnd_in      <- names(success_row)[as.logical(success_row)]
  ids_in_scen <- c(SOC_PRODUCTS, rnd_in)
  bid         <- branch_id(success_row)
  bp          <- branch_probability(success_row, ptrs_named)
  outcome     <- market_outcome_string(success_row, names(success_row))

  canonical_in_scen <- unique(vapply(ids_in_scen, function(pid) {
    e <- products_named[[pid]]
    if (!is.null(e)) e$product else pid
  }, character(1)))
  md_mult <- market_dynamic_multipliers(canonical_in_scen, market_df)

  interventions <- lapply(ids_in_scen, function(pid) {
    entry <- products_named[[pid]]
    if (is.null(entry)) { warning("No entry for '", pid, "' — skipping."); return(NULL) }
    build_intervention_scaled(entry, arch_lookup, archetype, md_mult[[entry$product]])
  })
  interventions <- Filter(Negate(is.null), interventions)

  list(list(
    id                 = paste0(bid, "_A", arch_idx),
    pjnz_names         = as.list(pjnz_names),
    branch_probability = bp,
    market_outcome     = outcome,
    interventions      = interventions
  ))
}

build_all_scenarios <- function(products_named, countries_df, archetypes_df, market_df, ptrs_df) {
  success_mat <- rnd_success_matrix(RND_PRODUCTS)
  ptrs_named  <- stats::setNames(ptrs_df$ptrs, ptrs_df$Product)
  arch_lookup <- archetype_lookup(archetypes_df)

  # Collect all target risk groups across all products for profile comparison.
  # Targets without a risk_group (e.g. Adult ART, which targets by sex) are skipped.
  all_target_pops <- unique(unlist(lapply(products_named, function(e) {
    if (!is.null(e$targets)) {
      Filter(Negate(is.null), lapply(e$targets, function(t) t$risk_group))
    } else {
      character(0)
    }
  })))

  # Profile key: concatenated multipliers over all target populations. Archetypes
  # with identical effective multipliers are grouped together so they share a scenario.
  profile_key <- function(arch) {
    mults <- vapply(all_target_pops, function(pop) {
      archetype_multiplier(arch_lookup, arch, pop)
    }, numeric(1))
    paste(mults, collapse = "_")
  }

  countries_df$profile <- vapply(countries_df$Archetype, profile_key, character(1))
  groups <- split(countries_df, countries_df$profile)
  archetype_groups <- lapply(groups, function(g) list(archetype = g$Archetype[1], countries = g$Country))

  n_branches <- nrow(success_mat)
  n_groups   <- length(archetype_groups)
  message("Building ", n_branches, " branches × ", n_groups, " archetype group(s) = ",
          n_branches * n_groups, " scenarios...")

  # Preallocate (one scenario per branch × group) to avoid quadratic list growth.
  scenarios <- vector("list", n_branches * n_groups)
  k <- 0L
  for (i in seq_len(n_branches)) {
    for (j in seq_along(archetype_groups)) {
      grp       <- archetype_groups[[j]]
      new_scens <- build_scenarios_for_branch(
        success_mat[i, ], products_named,
        pjnz_names  = grp$countries,
        arch_lookup = arch_lookup,
        archetype   = grp$archetype,
        arch_idx    = j,
        market_df   = market_df,
        ptrs_named  = ptrs_named
      )
      k <- k + 1L
      scenarios[[k]] <- new_scens[[1]]
    }
    if (i %% 64 == 0) message("  ...", i, " / ", n_branches)
  }
  scenarios
}

# ---- Main --------------------------------------------------------------------

main <- function() {
  products_named <- load_products(PRODUCTS_INPUT_PATH)
  countries_df   <- load_countries(COUNTRIES_INPUT_PATH)
  archetypes_df  <- load_archetypes(ARCHETYPES_INPUT_PATH)
  ptrs_df        <- load_ptrs(PTRS_INPUT_PATH)
  market_df      <- load_market_dynamics(MARKET_DYNAMICS_INPUT_PATH)

  if ("_default" %in% countries_df$Archetype &&
      !"_default" %in% archetypes_df$Archetype) {
    archetypes_df <- dplyr::bind_rows(
      archetypes_df,
      tibble::tibble(Archetype = "_default", `Target Population` = "*",
                     coverage_multiplier = 1)
    )
  }

  scenarios <- build_all_scenarios(products_named, countries_df, archetypes_df, market_df, ptrs_df)

  # Baseline: no interventions, runs against all countries, id = "0".
  baseline <- list(list(id = "0", pjnz = as.list(countries_df$Country), interventions = list()))
  scenarios <- c(baseline, scenarios)

  jsonlite::write_json(list(scenarios = scenarios), OUTPUT_PATH,
                       auto_unbox = TRUE, pretty = TRUE)

  message("Wrote ", OUTPUT_PATH, " with ", format(length(scenarios), big.mark = ","),
          " scenarios.")

  # Sanity: sum branch probabilities (exclude baseline which has no branch_probability).
  # Deduplicate archetype-group variants — all _A{i} variants of the same branch
  # share the same branch_probability.
  branch_scens <- Filter(function(s) !is.null(s$branch_probability), scenarios)
  all_ids   <- vapply(branch_scens, `[[`, character(1), "id")
  all_probs <- vapply(branch_scens, `[[`, numeric(1), "branch_probability")
  base_ids  <- stringr::str_remove(all_ids, "_A\\d+$")
  total_prob <- sum(all_probs[!duplicated(base_ids)])
  message("Sum of branch_probability (should be ~1.0): ", round(total_prob, 6))
}

if (sys.nframe() == 0) {
  main()
}
