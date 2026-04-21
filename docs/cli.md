# CLI

The `goals-scenario` CLI provides two commands: `draw` and `run`.

## Installation

```bash
pip install avenir_goals_scenario
```

After installation, `goals-scenario` is available on your PATH.

## Config file

Both commands are driven by a single JSON config file. Field names are case-insensitive
(`pjnz_dir`, `PJNZ_DIR`, and `Pjnz_Dir` are all accepted).

```json
{
  "pjnz_dir": "path/to/pjnz/files",
  "definition_path": "path/to/scenario_definitions.csv",
  "scenario_path": "path/to/draws.json",
  "output_dir": "path/to/output",
  "base_year": 2025,
  "output_indicators": [
    "p_hivpop",
    "p_infections",
    "p_hiv_deaths",
    "h_artpop"
  ],
  "n_simulations": 100,
  "n_workers": 4,
  "seed": null
}
```

| Field | Required | Description |
|---|---|---|
| `pjnz_dir` | Yes | Directory containing `.PJNZ` files |
| `output_dir` | Yes | Directory to write results to (created if absent; parent must exist) |
| `base_year` | Yes | First year of the output projection range |
| `output_indicators` | Yes | Goals output indicator names to extract |
| `definition_path` | No* | Path to the scenario definitions CSV file |
| `scenario_path` | No* | Path to a scenario draws JSON file |
| `n_simulations` | No | Number of draws per scenario (default: `100`) |
| `seed` | No | Integer RNG seed for reproducible draws (default: `null` - random) |
| `n_workers` | No | Parallel workers: `-1` for all CPUs, positive integer for explicit count (default: `4` or CPU count if fewer) |

\* At least one of `definition_path` or `scenario_path` must be supplied for `run`.
Both are required for `draw`.

---

## Commands

### `draw`

Generates scenario draws from a definition file and saves them to disk.

Both `definition_path` and `scenario_path` must be set in the config.

```bash
goals-scenario draw config.json
```

| Argument | Description |
|---|---|
| `CONFIG_PATH` | Path to a JSON config file |

---

### `run`

Runs scenario analysis across a directory of PJNZ files. Behaviour depends on
which of `definition_path` and `scenario_path` are set in the config:

| `definition_path` | `scenario_path` | Behaviour |
|---|---|---|
| Set | Not set | Draws in memory, saves to `<output_dir>/draws.json`, runs |
| Not set | Set (file exists) | Loads draws from file, runs |
| Set | Set (file exists) | Uses existing draws (logs a message), runs |
| Set | Set (file missing) | Redraws, saves to `scenario_path`, runs |

```bash
goals-scenario run config.json
```

| Argument | Description |
|---|---|
| `CONFIG_PATH` | Path to a JSON config file (positional) |

#### Typical workflows

**One-shot** - draw and run in a single command, no intermediate file:

```json
{
  "pjnz_dir": "path/to/pjnz",
  "definition_path": "scenario_definitions.csv",
  "output_dir": "path/to/output",
  "base_year": 2025,
  "output_indicators": ["p_hivpop", "p_infections"]
}
```

```bash
goals-scenario run config.json
```

**Two-step** - generate and inspect draws first, then run:

```bash
goals-scenario draw config.json   # writes draws to scenario_path
goals-scenario run config.json    # reuses the same draws
```

---

## File formats

### Scenario definition CSV

Each scenario ID maps to one or a group of interventions. Multiple rows sharing
the same `Number` represent multiple target populations for that intervention -
all parameter columns must be identical across those rows, only `Target
Population` and `Sex` may differ. A combined scenario row has the IDs to
combine joined by `+` in the `Product` column, with all other columns empty.
Column headers are case-insensitive.

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

### Scenario draws JSON

The draws file produced by `draw` (or saved automatically by `run`) has this
structure:

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

## Global options

| Option | Description |
|---|---|
| `--version` | Show version and exit |
| `--help`, `-h` | Show help and exit |
| `-v`, `--verbose` | Enable debug logging |

## Tab completion

```bash
goals-scenario --install-completion
```
