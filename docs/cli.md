# CLI

The `goals-scenario` CLI provides two commands.

## Installation

```bash
pip install avenir_goals_scenario
```

After installation, `goals-scenario` is available on your PATH.

## Commands

### `simulations`

Generates a scenario simulations file from a scenario definition.

```bash
goals-scenario simulations scenario_definition.csv scenario_simulations.json
```

| Argument / Option | Description |
|---|---|
| `DEFINITION_PATH` | Path to the input scenario definition CSV file (positional) |
| `SIMULATIONS_PATH` | Path to write the scenario simulations file to (positional) |
| `-n`, `--n-simulations` | Number of simulations per scenario (default: 100) |

---

#### File formats

Scenario definition CSV

Each scenario ID maps to one or a group of interventions. Multiple rows sharing the same `Number` represent multiple target populations for that intervention — all parameter columns must be identical across those rows, only `Target Population` and `Sex` may differ. A combined scenario row has the IDs to combine joined by `+` in the `Product` column, with all other columns empty. Column headers are case-insensitive.

| Column | Description |
|---|---|
| `Number` | Integer scenario ID (repeated for multi-population interventions) |
| `Product` | Intervention name, or `X+Y+Z` to combine scenarios X, Y and Z |
| `Efficacy mean` | Mean efficacy |
| `Efficacy STD` | Efficacy standard deviation |
| `Adherence mean` | Mean adherence |
| `Adherence STD` | Adherence standard deviation |
| `Target Coverage mean` | Mean target coverage |
| `Target Coverage STD` | Target coverage standard deviation |
| `Target Year mean` | Mean target year |
| `Target Year STD` | Target year standard deviation |
| `Target Population` | Population group (e.g. `High risk heterosexual`, `PLHIV`) |
| `Sex` | `Female`, `Male`, or `Both` |

```
Number,Product,Efficacy mean,Efficacy STD,Adherence mean,Adherence STD,Target Coverage mean,Target Coverage STD,Target Year mean,Target Year STD,Target Population,Sex
1,One month pill for PrEP,0.95,0.03,0.95,0.03,0.20,0.05,2028,2,High risk heterosexual,Female
1,One month pill for PrEP,0.95,0.03,0.95,0.03,0.20,0.05,2028,2,Men who have sex with men,Male
2,Daily PrEP,0.95,0.03,0.80,0.20,0.10,0.05,2027,2,High risk heterosexual,Female
...
25,1+2,,,,,,,,,,
...
```

Scenario simulations

```json
{
  "scenarios": [
    {
      "scenario_id": 1,
      "interventions": [
        {
          "id": "one_month_pill_for_prep",
          "product": "One month pill for PrEP",
          "targets": [
            { "population": "High risk heterosexual", "sex": "Female" },
            { "population": "Men who have sex with men", "sex": "Male" }
          ]
        }
      ],
      "simulations": [
        {
          "one_month_pill_for_prep": { "efficacy": 0.976158, "adherence": 0.9425262, "target_coverage": 0.202123, "target_year": 2028 }
        }
      ]
    },
    ...
    {
      "scenario_id": 25,
      "interventions": [
        {
          "id": "one_month_pill_for_prep",
          "product": "One month pill for PrEP",
          "targets": [
            { "population": "High risk heterosexual", "sex": "Female" },
            { "population": "Men who have sex with men", "sex": "Male" }
          ]
        },
        {
          "id": "daily_prep",
          "product": "Daily PrEP",
          "targets": [
            { "population": "High risk heterosexual", "sex": "Female" }
          ]
        }
      ],
      "simulations": [
        {
          "one_month_pill_for_prep": { "efficacy": 0.976158, "adherence": 0.9425262, "target_coverage": 0.202123, "target_year": 2028 },
          "daily_prep":              { "efficacy": 0.96213,  "adherence": 0.951231,  "target_coverage": 0.19862,  "target_year": 2028 }
        }
      ]
    },
    ...
  ]
}
```

### `run`

Runs scenario analysis across a directory of PJNZ files, driven by a JSON config file.

```bash
goals-scenario run config.json
```

| Argument | Description |
|---|---|
| `CONFIG_PATH` | Path to a JSON config file (positional) |

#### Config file format

Field names are case-insensitive (`Goals_path`, `goals_path`, and `GOALS_PATH` are all accepted).

```json
{
  "Goals_path": "path/to/pjnz.files",
  "Scenario_path": "path/to/scenario_simulations.json",
  "Output_path": "path/to/scenario_output.?",
  "Base_year": "2025",
  "Output_indicators": [
    "PLHIV",
    "New Infections",
    "AIDS deaths",
    "Number on ART",
    "DALYs",
    "Total Cost"
  ]
}
```

| Field | Description |
|---|---|
| `Goals_path` | Directory containing `.PJNZ` files |
| `Scenario_path` | Path to scenario simulations JSON file |
| `Output_path` | Path to write output to |
| `Base_year` | Base year for the analysis |
| `Output_indicators` | List of indicators to include in output |

## Global options

| Option | Description |
|---|---|
| `--version` | Show version and exit |
| `--help`, `-h` | Show help and exit |

## Tab completion

```bash
goals-scenario --install-completion
```
