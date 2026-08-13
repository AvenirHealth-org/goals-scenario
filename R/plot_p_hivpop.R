output_dir <- path.expand("~/Downloads/scenario_analysis_output_pq2")
country <- "SouthAfrica"

indicator_dir <- file.path(output_dir, "p_infections")
ds <- arrow::open_dataset(indicator_dir)

by_year_sim <- ds |>
  dplyr::filter(pjnz_name == country) |>
  dplyr::group_by(scenario_id, simulation, year) |>
  dplyr::summarise(total = sum(value), .groups = "drop") |>
  dplyr::collect()

by_year <- by_year_sim |>
  dplyr::group_by(scenario_id, year) |>
  dplyr::summarise(mean_total = mean(total), .groups = "drop")

baseline_id <- "no_intervention"
other_ids <- setdiff(sort(unique(by_year$scenario_id)), baseline_id)
palette <- stats::setNames(scales::hue_pal()(length(other_ids)), other_ids)
palette[baseline_id] <- "black"

p <- ggplot2::ggplot(
  by_year,
  ggplot2::aes(
    x = year,
    y = mean_total,
    color = scenario_id,
    linewidth = scenario_id == baseline_id,
    group = scenario_id
  )
) +
  ggplot2::geom_line() +
  ggplot2::scale_color_manual(values = palette) +
  ggplot2::scale_linewidth_manual(
    values = c(`TRUE` = 1.4, `FALSE` = 0.6),
    guide = "none"
  ) +
  ggplot2::labs(
    title = paste("Mean HIV infections by scenario -", country),
    x = "Year",
    y = "Mean p_infections (across simulations)",
    color = "Scenario"
  )

plotly::ggplotly(p)
