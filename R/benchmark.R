#!/usr/bin/env Rscript
# benchmark.R ---------------------------------------------------------------
# Compares Goals scenario analysis output formats: HDF5 vs Parquet (arrow,
# DuckDB via dbplyr, duckplyr) across three query patterns:
#
#   A. Single scenario, single country — filter sex=female + year range
#   B. All scenarios,  single country  — total p_hivpop by scenario + year
#   C. Single scenario, all countries  — total p_hivpop by country  + year
#
# No library() calls — all packages are qualified.
#
# Parquet layout:
#   {output_dir}/p_hivpop/pjnz_name=X/part-N.parquet
#   pjnz_name is a hive partition; each part file holds many scenarios, one row
#   group per scenario. Data columns: scenario_id (string), simulation (int32),
#   age (int16), sex (dict "male"/"female"),
#                 year (int16, actual calendar year), value (float64)
#
# HDF5 layout:
#   {output_dir}/{pjnz_name}/scenario_{id}.h5
#   Dataset p_hivpop has shape (n_sim, age=81, sex=2, year=n_years) in Python;
#   hdf5r reverses dims to (n_years, sex=2, age=81, n_sim) in R.
#
# Dependencies:
#   install.packages(c("bench", "dplyr", "hdf5r", "arrow", "duckdb", "duckplyr"))
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Configuration — edit to match your run
# ---------------------------------------------------------------------------
HDF5_DIR        <- "~/Downloads/scenario_analysis_output"
PARQUET_DIR     <- "~/Downloads/scenario_analysis_output_pq"
BASE_YEAR       <- 2010L

TARGET_PJNZ     <- "Zimbabwe"
TARGET_SCENARIO <- 2L
YEAR_FROM       <- 2015L
YEAR_TO         <- 2025L

# ---------------------------------------------------------------------------
# HDF5 helpers
#
# hdf5r reverses dims vs Python (HDF5 C-order → R Fortran-order), so a Python
# array of shape (n_sim, age, sex, year) arrives in R as (year, sex, age, n_sim).
# expand.grid() lists dims in that reversed order so as.vector() row-order
# matches the flat HDF5 data.
# ---------------------------------------------------------------------------
DIMS_HDF5 <- list(
  p_hivpop      = list(sex = c("male", "female"), age = 0:80),
  p_infections  = list(sex = c("male", "female"), age = 0:80),
  p_hiv_deaths  = list(sex = c("male", "female"), age = 0:80),
  h_artpop      = list(sex = c("male", "female"), age = 0:65,
                       disease_stage = 0:6, treatment_stage = 0:2)
)

flat_to_long_hdf5 <- function(flat, indicator, n_sim, n_years, base_year,
                               pjnz, scenario_id) {
  inner <- DIMS_HDF5[[indicator]]
  years <- seq(base_year, by = 1L, length.out = n_years)
  grid  <- expand.grid(
    c(list(year = years), inner, list(simulation = seq_len(n_sim))),
    KEEP.OUT.ATTRS = FALSE, stringsAsFactors = FALSE
  )
  grid$value       <- flat
  grid$pjnz        <- pjnz
  grid$scenario_id <- scenario_id
  grid
}

scenario_id_from_path <- function(path) {
  as.integer(sub("^scenario_", "", tools::file_path_sans_ext(basename(path))))
}

read_hdf5_p_hivpop <- function(h5_path, pjnz, base_year) {
  f <- hdf5r::H5File$new(h5_path, mode = "r")
  on.exit(f$close_all(), add = TRUE)
  arr     <- f[["p_hivpop"]]$read()
  dims    <- dim(arr)
  n_years <- dims[[1L]]
  n_sim   <- dims[[length(dims)]]
  flat_to_long_hdf5(as.vector(arr), "p_hivpop", n_sim, n_years,
                    base_year, pjnz, scenario_id_from_path(h5_path))
}

# ---------------------------------------------------------------------------
# A. Single scenario, single country — filter sex=female, year range, agg sims
# ---------------------------------------------------------------------------
A_hdf5 <- function(output_dir, pjnz, scenario_id, year_from, year_to, base_year) {
  h5_path <- file.path(output_dir, pjnz, sprintf("scenario_%d.h5", scenario_id))
  read_hdf5_p_hivpop(h5_path, pjnz, base_year) |>
    dplyr::filter(sex == "female", year >= year_from, year <= year_to) |>
    dplyr::group_by(dplyr::across(-c(simulation, value))) |>
    dplyr::summarise(mean = mean(value), sd = sd(value), .groups = "drop")
}

A_arrow <- function(output_dir, target_pjnz, target_scenario, year_from, year_to) {
  arrow::open_dataset(file.path(output_dir, "p_hivpop")) |>
    dplyr::filter(pjnz_name == target_pjnz, scenario_id == target_scenario) |>
    dplyr::collect() |>
    dplyr::filter(sex == "female", year >= year_from, year <= year_to) |>
    dplyr::group_by(pjnz_name, scenario_id, age, year) |>
    dplyr::summarise(mean = mean(value), sd = sd(value), .groups = "drop")
}

A_duckdb <- function(output_dir, target_pjnz, target_scenario, year_from, year_to) {
  con  <- duckdb::dbConnect(duckdb::duckdb())
  on.exit(duckdb::dbDisconnect(con, shutdown = TRUE), add = TRUE)
  glob <- file.path(output_dir, "p_hivpop", "**", "*.parquet")
  dplyr::tbl(con, sprintf("read_parquet('%s', hive_partitioning = true)", glob)) |>
    dplyr::filter(pjnz_name   == target_pjnz,
                  scenario_id == target_scenario,
                  sex         == "female",
                  year        >= year_from,
                  year        <= year_to) |>
    dplyr::group_by(pjnz_name, scenario_id, age, year) |>
    dplyr::summarise(mean = mean(value, na.rm = TRUE),
                     sd   = sd(value,   na.rm = TRUE),
                     .groups = "drop") |>
    dplyr::collect()
}

A_duckplyr <- function(output_dir, target_pjnz, target_scenario, year_from, year_to) {
  glob <- file.path(output_dir, "p_hivpop", "**", "*.parquet")
  duckplyr::read_parquet_duckdb(glob,
                                options  = list(hive_partitioning = "true"),
                                prudence = "lavish") |>
    dplyr::filter(pjnz_name   == target_pjnz,
                  scenario_id == target_scenario,
                  sex         == "female",
                  year        >= year_from,
                  year        <= year_to) |>
    dplyr::group_by(pjnz_name, scenario_id, age, year) |>
    dplyr::summarise(mean = mean(value), sd = sd(value), .groups = "drop")
}

# ---------------------------------------------------------------------------
# B. All scenarios, single country — total p_hivpop by scenario + year
# ---------------------------------------------------------------------------
B_hdf5 <- function(output_dir, pjnz, base_year) {
  pjnz_dir <- file.path(output_dir, pjnz)
  h5_paths <- list.files(pjnz_dir, pattern = "\\.h5$", full.names = TRUE)
  if (!length(h5_paths))
    stop("No .h5 files found in: ", pjnz_dir)
  dplyr::bind_rows(lapply(h5_paths, read_hdf5_p_hivpop, pjnz = pjnz, base_year = base_year)) |>
    dplyr::group_by(pjnz, scenario_id, year, simulation) |>
    dplyr::summarise(total = sum(value), .groups = "drop") |>
    dplyr::group_by(pjnz, scenario_id, year) |>
    dplyr::summarise(mean = mean(total), sd = sd(total), .groups = "drop")
}

B_arrow <- function(output_dir, target_pjnz) {
  arrow::open_dataset(file.path(output_dir, "p_hivpop")) |>
    dplyr::filter(pjnz_name == target_pjnz) |>
    dplyr::collect() |>
    dplyr::group_by(pjnz_name, scenario_id, year, simulation) |>
    dplyr::summarise(total = sum(value), .groups = "drop") |>
    dplyr::group_by(pjnz_name, scenario_id, year) |>
    dplyr::summarise(mean = mean(total), sd = sd(total), .groups = "drop")
}

B_duckdb <- function(output_dir, target_pjnz) {
  con  <- duckdb::dbConnect(duckdb::duckdb())
  on.exit(duckdb::dbDisconnect(con, shutdown = TRUE), add = TRUE)
  glob <- file.path(output_dir, "p_hivpop", "**", "*.parquet")
  dplyr::tbl(con, sprintf("read_parquet('%s', hive_partitioning = true)", glob)) |>
    dplyr::filter(pjnz_name == target_pjnz) |>
    dplyr::group_by(pjnz_name, scenario_id, year, simulation) |>
    dplyr::summarise(total = sum(value, na.rm = TRUE), .groups = "drop") |>
    dplyr::group_by(pjnz_name, scenario_id, year) |>
    dplyr::summarise(mean = mean(total, na.rm = TRUE),
                     sd   = sd(total,   na.rm = TRUE),
                     .groups = "drop") |>
    dplyr::collect()
}

B_duckplyr <- function(output_dir, target_pjnz) {
  glob <- file.path(output_dir, "p_hivpop", "**", "*.parquet")
  duckplyr::read_parquet_duckdb(glob,
                                options  = list(hive_partitioning = "true"),
                                prudence = "lavish") |>
    dplyr::filter(pjnz_name == target_pjnz) |>
    dplyr::group_by(pjnz_name, scenario_id, year, simulation) |>
    dplyr::summarise(total = sum(value), .groups = "drop") |>
    dplyr::group_by(pjnz_name, scenario_id, year) |>
    dplyr::summarise(mean = mean(total), sd = sd(total), .groups = "drop")
}

# ---------------------------------------------------------------------------
# C. Single scenario, all countries — total p_hivpop by country + year
# ---------------------------------------------------------------------------
C_hdf5 <- function(output_dir, target_scenario, base_year) {
  pjnz_dirs <- list.dirs(output_dir, recursive = FALSE)
  dplyr::bind_rows(lapply(pjnz_dirs, function(d) {
    h5_path <- file.path(d, sprintf("scenario_%d.h5", target_scenario))
    if (!file.exists(h5_path)) return(NULL)
    read_hdf5_p_hivpop(h5_path, basename(d), base_year)
  })) |>
    dplyr::group_by(pjnz, scenario_id, year, simulation) |>
    dplyr::summarise(total = sum(value), .groups = "drop") |>
    dplyr::group_by(pjnz, scenario_id, year) |>
    dplyr::summarise(mean = mean(total), sd = sd(total), .groups = "drop")
}

C_arrow <- function(output_dir, target_scenario) {
  arrow::open_dataset(file.path(output_dir, "p_hivpop")) |>
    dplyr::filter(scenario_id == target_scenario) |>
    dplyr::collect() |>
    dplyr::group_by(pjnz_name, scenario_id, year, simulation) |>
    dplyr::summarise(total = sum(value), .groups = "drop") |>
    dplyr::group_by(pjnz_name, scenario_id, year) |>
    dplyr::summarise(mean = mean(total), sd = sd(total), .groups = "drop")
}

C_duckdb <- function(output_dir, target_scenario) {
  con  <- duckdb::dbConnect(duckdb::duckdb())
  on.exit(duckdb::dbDisconnect(con, shutdown = TRUE), add = TRUE)
  glob <- file.path(output_dir, "p_hivpop", "**", "*.parquet")
  dplyr::tbl(con, sprintf("read_parquet('%s', hive_partitioning = true)", glob)) |>
    dplyr::filter(scenario_id == target_scenario) |>
    dplyr::group_by(pjnz_name, scenario_id, year, simulation) |>
    dplyr::summarise(total = sum(value, na.rm = TRUE), .groups = "drop") |>
    dplyr::collect() |>
    dplyr::group_by(pjnz_name, scenario_id, year) |>
    dplyr::summarise(mean = mean(total), sd = sd(total), .groups = "drop")
}

C_duckplyr <- function(output_dir, target_scenario) {
  glob <- file.path(output_dir, "p_hivpop", "**", "*.parquet")
  duckplyr::read_parquet_duckdb(glob,
                                options  = list(hive_partitioning = "true"),
                                prudence = "lavish") |>
    dplyr::filter(scenario_id == target_scenario) |>
    dplyr::group_by(pjnz_name, scenario_id, year, simulation) |>
    dplyr::summarise(total = sum(value), .groups = "drop") |>
    dplyr::collect() |>
    dplyr::group_by(pjnz_name, scenario_id, year) |>
    dplyr::summarise(mean = mean(total), sd = sd(total), .groups = "drop")
}

# ---------------------------------------------------------------------------
# Run benchmarks
# ---------------------------------------------------------------------------
cat("=== Goals scenario output benchmark ===\n")

bm <- list()

cat(sprintf("\n--- A: scenario=%d  pjnz=%s  sex=female  year=%d-%d ---\n",
            TARGET_SCENARIO, TARGET_PJNZ, YEAR_FROM, YEAR_TO))
bm[["A"]] <- bench::mark(
  hdf5    = A_hdf5(path.expand(HDF5_DIR), TARGET_PJNZ, TARGET_SCENARIO, YEAR_FROM, YEAR_TO, BASE_YEAR),
  arrow   = A_arrow(path.expand(PARQUET_DIR), TARGET_PJNZ, TARGET_SCENARIO, YEAR_FROM, YEAR_TO),
  duckdb  = A_duckdb(path.expand(PARQUET_DIR), TARGET_PJNZ, TARGET_SCENARIO, YEAR_FROM, YEAR_TO),
  duckplyr = A_duckplyr(path.expand(PARQUET_DIR), TARGET_PJNZ, TARGET_SCENARIO, YEAR_FROM, YEAR_TO),
  iterations = 5L, check = FALSE
)
print(bm[["A"]])

cat(sprintf("\n--- B: all scenarios  pjnz=%s  total p_hivpop by scenario+year ---\n",
            TARGET_PJNZ))
bm[["B"]] <- bench::mark(
  hdf5    = B_hdf5(path.expand(HDF5_DIR), TARGET_PJNZ, BASE_YEAR),
  arrow   = B_arrow(path.expand(PARQUET_DIR), TARGET_PJNZ),
  duckdb  = B_duckdb(path.expand(PARQUET_DIR), TARGET_PJNZ),
  duckplyr = B_duckplyr(path.expand(PARQUET_DIR), TARGET_PJNZ),
  iterations = 5L, check = FALSE
)
print(bm[["B"]])

cat(sprintf("\n--- C: scenario=%d  all countries  total p_hivpop by country+year ---\n",
            TARGET_SCENARIO))
bm[["C"]] <- bench::mark(
  hdf5    = C_hdf5(path.expand(HDF5_DIR), TARGET_SCENARIO, BASE_YEAR),
  arrow   = C_arrow(path.expand(PARQUET_DIR), TARGET_SCENARIO),
  duckdb  = C_duckdb(path.expand(PARQUET_DIR), TARGET_SCENARIO),
  duckplyr = C_duckplyr(path.expand(PARQUET_DIR), TARGET_SCENARIO),
  iterations = 5L, check = FALSE
)
print(bm[["C"]])

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
cat("\n=== Summary ===\n")
print(dplyr::bind_rows(bm, .id = "test"))
