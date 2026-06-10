# CLI

The `goals-scenario` CLI provides two commands: `draw` and `run`.

## Installation

**Via pip (Python required)**

```bash
pip install avenir_goals_scenario
```

After installation, `goals-scenario` is available on your PATH.

**Windows standalone executable (no Python required)**

Download `goals-scenario-windows.zip` from the [releases page](https://github.com/avenirhealth-org/goals-scenario/releases), unzip it, and run `goals-scenario.exe` from the extracted folder. Optionally add the folder to your `PATH` so the command is available globally.

## Config file

Both commands are driven by a single JSON config file. Field names are case-insensitive
(`pjnz_dir`, `PJNZ_DIR`, and `Pjnz_Dir` are all accepted).

```json
{
  "pjnz_dir": "C:\\path\\to\\pjnz\\files",
  "definition_path": "C:\\path\\to\\scenario_definitions.json",
  "scenario_path": "C:\\path\\to\\draws.json",
  "output_dir": "C:\\path\\to\\output",
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

Note you need to escape the `\` in windows-style file paths, so use `\\`. Alternatively you can use unix-style `/` and the tool will translate them for you.

| Field | Required | Description |
|---|---|---|
| `pjnz_dir` | Yes | Directory containing `.PJNZ` files |
| `output_dir` | Yes | Directory to write results to (created if absent; parent must exist) |
| `base_year` | Yes | First year of the output projection range |
| `output_indicators` | Yes | Goals output indicator names to extract |
| `definition_path` | No* | Path to the scenario definitions JSON file |
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
  "definition_path": "scenario_definitions.json",
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

### Scenario definition JSON

The scenario definition file specifies the set of scenarios to analyse. Each scenario
is either a single set of interventions, or a combination of other single scenarios.
The file is consumed by the `draw` command, which samples parameter distributions and
writes the resulting draws to the scenario draws JSON.

```json
{
  "scenarios": [
    {
      "id": "1",
      "pjnz_names": ["Zimbabwe"],
      "interventions": [ ... ]
    },
    {
      "id": "2",
      "interventions": [ ... ]
    },
    {
      "id": "3",
      "combines": ["1", "2"]
    }
  ]
}
```

| Field | Description |
|---|---|
| `id` | Unique string identifier for this scenario |
| `pjnz_names` | Optional list of PJNZ file names (without `.PJNZ`) to restrict this scenario to |
| `interventions` | List of typed intervention objects (single scenarios only) |
| `combines` | List of two or more single scenario IDs to merge (combined scenarios only) |

#### Intervention types

Each intervention is discriminated by its `product` field. The valid products and their
required fields are listed below.

---

##### PrEP interventions

Valid `product` values: `"Daily PrEP"`, `"One month pill for PrEP"`,
`"One month injectable PrEP"`, `"Two month injectable PrEP"`,
`"Six month injectable PrEP"`, `"Oral PrEP plus contraceptive"`,
`"Ring PrEP"`, `"Implantable PrEP"`, `"bNABs"`

`targets`: one or more population/sex combinations. Valid populations:
`"Low risk heterosexual"`, `"Medium risk heterosexual"`, `"High risk heterosexual"`,
`"People who inject drugs"`, `"Men who have sex with men"`.
Valid sex values: `"Male"`, `"Female"`, `"All"`.

`parameters`:

| Parameter | Description |
|---|---|
| `efficacy` | Distribution for intervention efficacy (proportion, 0–1) |
| `adherence` | Distribution for adherence (proportion, 0–1) |
| `target_coverage` | Distribution for target population coverage (proportion, 0–1) |
| `target_year` | Distribution for target implementation year (integer ≥ 1970) |

Each distribution is `{"mean": <float>, "sd": <float>}` with optional `min_value` and `max_value` overrides.

```json
{
  "product": "Daily PrEP",
  "targets": [
    {"population": "High risk heterosexual", "sex": "Female"},
    {"population": "Men who have sex with men", "sex": "Male"}
  ],
  "parameters": {
    "efficacy":        {"mean": 0.95, "sd": 0.03},
    "adherence":       {"mean": 0.85, "sd": 0.05},
    "target_coverage": {"mean": 0.30, "sd": 0.05},
    "target_year":     {"mean": 2028, "sd": 2}
  }
}
```

---

##### Vaccine

`product`: `"Vaccine"`

`targets`: same populations and sex values as PrEP (one or more required).

`parameters`:

| Parameter | Type | Description |
|---|---|---|
| `target_year` | Distribution | Target implementation year |
| `target_coverage` | Distribution | Target population coverage (0–1) |
| `reduction_in_susceptibility` | Distribution | Reduction in susceptibility to HIV due to vaccination (0–1) |
| `reduction_in_infectiousness` | Distribution | Reduction in infectiousness due to vaccination (0–1) |
| `increase_in_progression_time_to_aids` | Distribution | Increase in progression time to AIDS (0–1) |
| `vaccine_duration_years` | Distribution | Vaccine duration in years |
| `vaccine_action_type` | `"Take"` or `"Degree"` | Type of vaccine action on susceptibility |
| `targeting` | `"Vaccinate without HIV testing"` or `"Vaccinate only HIV-negative individuals"` | Vaccination targeting strategy |
| `behavior_change_reversal_vaccinated` | Distribution | Behaviour change reversal among vaccinated individuals (0–1) |
| `behavior_change_reversal_all_adults` | Distribution | Behaviour change reversal among all adults (0–1) |

```json
{
  "product": "Vaccine",
  "targets": [
    {"population": "Medium risk heterosexual", "sex": "Female"}
  ],
  "parameters": {
    "target_year":                           {"mean": 2035, "sd": 3},
    "target_coverage":                       {"mean": 0.50, "sd": 0.10},
    "reduction_in_susceptibility":           {"mean": 0.60, "sd": 0.05},
    "reduction_in_infectiousness":           {"mean": 0.40, "sd": 0.05},
    "increase_in_progression_time_to_aids":  {"mean": 0.20, "sd": 0.02},
    "vaccine_duration_years":                {"mean": 5,    "sd": 1},
    "vaccine_action_type":                   "Take",
    "targeting":                             "Vaccinate only HIV-negative individuals",
    "behavior_change_reversal_vaccinated":   {"mean": 0.10, "sd": 0.01},
    "behavior_change_reversal_all_adults":   {"mean": 0.05, "sd": 0.005}
  }
}
```

---

##### Cure

`product`: `"Cure"`

`targets`: same populations and sex values as PrEP (one or more required).

`parameters`:

| Parameter | Description |
|---|---|
| `target_year` | Target implementation year |
| `target_coverage` | Target coverage (0–1) |
| `efficacy` | Efficacy of the cure (0–1) |
| `duration_of_cure` | Duration of cure effect |

```json
{
  "product": "Cure",
  "targets": [
    {"population": "High risk heterosexual", "sex": "Female"}
  ],
  "parameters": {
    "target_year":     {"mean": 2035, "sd": 3},
    "target_coverage": {"mean": 0.20, "sd": 0.05},
    "efficacy":        {"mean": 0.85, "sd": 0.05},
    "duration_of_cure":{"mean": 0.50, "sd": 0.10}
  }
}
```

---

##### AHD treatment

`product`: `"AHD treatment"`

No `targets` field — coverage applies globally.

`parameters`:

| Parameter | Description |
|---|---|
| `target_year` | Target implementation year |
| `target_coverage` | Target coverage (0–1) |
| `reduction_in_mortality` | Reduction in AHD mortality (0–1) |

```json
{
  "product": "AHD treatment",
  "parameters": {
    "target_year":          {"mean": 2026, "sd": 1},
    "target_coverage":      {"mean": 0.70, "sd": 0.08},
    "reduction_in_mortality":{"mean": 0.40, "sd": 0.05}
  }
}
```

---

##### Point of care viral load test

`product`: `"Point of care viral load test"`

No `targets` field.

`parameters`:

| Parameter | Description |
|---|---|
| `target_year` | Target implementation year |
| `target_coverage` | Target coverage (0–1) |
| `effect` | Effect size (0–1) |

```json
{
  "product": "Point of care viral load test",
  "parameters": {
    "target_year":     {"mean": 2027, "sd": 1},
    "target_coverage": {"mean": 0.70, "sd": 0.08},
    "effect":          {"mean": 0.50, "sd": 0.05}
  }
}
```

---

##### Point of care CD4 test

`product`: `"Point of care CD4 test"`

Same structure as Point of care viral load test.

```json
{
  "product": "Point of care CD4 test",
  "parameters": {
    "target_year":     {"mean": 2027, "sd": 1},
    "target_coverage": {"mean": 0.70, "sd": 0.08},
    "effect":          {"mean": 0.50, "sd": 0.05}
  }
}
```

---

##### Long-acting treatment

`product`: `"Long-acting treatment"`

`targets`: one or more entries. Valid populations: `"Key populations"`,
`"General population"`, `"Medium risk populations"`, `"Not sexually active"`.
Valid sex values: `"Male"`, `"Female"`, `"Both"` (omit `sex` for Key populations).

`parameters`:

| Parameter | Description |
|---|---|
| `target_year` | Target implementation year |
| `target_coverage` | Target coverage (0–1) |

```json
{
  "product": "Long-acting treatment",
  "targets": [
    {"population": "Key populations"},
    {"population": "General population", "sex": "Female"},
    {"population": "General population", "sex": "Male"}
  ],
  "parameters": {
    "target_year":     {"mean": 2030, "sd": 2},
    "target_coverage": {"mean": 0.30, "sd": 0.05}
  }
}
```

> **Note:** Long-acting treatment is defined in the schema but its application to the
> Goals model is not yet implemented. Scenarios containing this intervention will raise
> an error at run time.

---

### Scenario draws JSON

The draws file produced by `draw` (or saved automatically by `run`) has this structure:

```json
{
  "scenarios": [
    {
      "id": "1",
      "interventions": [
        {
          "id": "daily_prep",
          "product": "Daily PrEP",
          "targets": [
            { "population": "High risk heterosexual", "sex": "Female" },
            { "population": "Men who have sex with men", "sex": "Male" }
          ]
        }
      ],
      "simulations": [
        {
          "daily_prep": {
            "efficacy": 0.976158,
            "adherence": 0.942526,
            "target_coverage": 0.202123,
            "target_year": 2028
          }
        }
      ]
    }
  ]
}
```

Each entry in `simulations` maps intervention slug → sampled parameter values for one
draw. Categorical parameters (e.g. `vaccine_action_type`) are passed through unchanged.

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
