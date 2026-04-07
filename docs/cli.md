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
goals-scenario simulations scenario_definition.json scenario_simulations.json
```

| Argument / Option | Description |
|---|---|
| `DEFINITION_PATH` | Path to the input scenario definition file (positional) |
| `SIMULATIONS_PATH` | Path to write the scenario simulations file to (positional) |
| `-n`, `--n-simulations` | Number of simulations per scenario (default: 100) |

---

#### File formats

Scenario definition

```json
{
  "scenario_definitions": [
    {
      "id": 1,
      "interventions": [
        {
          "product": "One month pill for PrEP",
          "target_population": ["People who inject drugs (PWID)", "Men who have sex with men"],
          "sex": "both",
          "parameters": {
            "efficacy":        { "mean": 0.95, "sd": 0.03 },
            "adherence":       { "mean": 0.95, "sd": 0.03 },
            "target_coverage": { "mean": 0.20, "sd": 0.05 },
            "target_year":     { "mean": 2028, "sd": 2    }
          }
        }
      ]
    },
    {
      "id": 2,
      "interventions": [
        {
          "product": "Daily PrEP",
          "target_population": ["People who inject drugs (PWID)", "Men who have sex with men"],
          "sex": "both",
          "parameters": {
            "efficacy":        { "mean": 0.95, "sd": 0.03 },
            "adherence":       { "mean": 0.80, "sd": 0.20 },
            "target_coverage": { "mean": 0.10, "sd": 0.05 },
            "target_year":     { "mean": 2027, "sd": 2    }
          }
        }
      ]
    },
    ...
    {
      "id": 25,
      "combines": [1, 2]
    },
    ...
  ]
}
```

Scenario simulations

```json
{
  "scenarios": [
    {
      "scenario_id": 1,
      "interventions": [
        { "id": "prep_pill", "product": "One month pill for PrEP", "target_population": ["People who inject drugs (PWID)", "Men who have sex with men"], "sex": "both" }
      ],
      "simulations": [
        {
          "prep_pill": { "efficacy": 0.976158, "adherence": 0.9425262, "target_coverage": 0.202123, "target_year": 2028 }
        },
        {
          "prep_pill": { "efficacy": 0.96213, "adherence": 0.951231, "target_coverage": 0.19862, "target_year": 2028 }
        }
      ]
    },
    ...
    {
      "scenario_id": 25,
      "interventions": [
        { "id": "prep_pill", "product": "One month pill for PrEP", "target_population": ["People who inject drugs (PWID)", "Men who have sex with men"], "sex": "both" },
        { "id": "daily_prep", "product": "Daily PrEP", "target_population": ["People who inject drugs (PWID)", "Men who have sex with men"], "sex": "both" }
      ],
      "simulations": [
        {
          "prep_pill":  { "efficacy": 0.976158, "adherence": 0.9425262, "target_coverage": 0.202123, "target_year": 2028 },
          "daily_prep": { "efficacy": 0.96213,  "adherence": 0.951231,  "target_coverage": 0.19862,  "target_year": 2028 }
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
