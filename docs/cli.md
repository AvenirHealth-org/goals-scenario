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

| Argument / Option | Description |
|---|---|
| `CONFIG_PATH` | Path to a JSON config file (positional) |
| `--retry PATH` | Re-run only the units listed in a `failures.json` from a previous run (see [Fault tolerance & re-runs](#fault-tolerance-and-re-runs)) |

#### Fault tolerance and re-runs

A run is made up of one work unit per `(PJNZ, scenario)` combination. If an individual
unit fails (for example a single scenario errors for one country), it is **logged and
skipped** — the run continues and every other unit still completes and is written.

PJNZ **import** failures are the exception: a `.PJNZ` file that cannot be read is treated
as a fatal data error and aborts the whole run (exit code `1`).

When any unit fails, a summary is printed and a `failures.json` manifest is written to
`output_dir` (see [Failures manifest JSON](#failures-manifest-json)). The command exits
with code `2` to signal a partial run. Re-run just the failed units by pointing `--retry`
at that manifest:

```bash
goals-scenario run config.json --retry path/to/output/failures.json
```

Retries reuse the same draws, so the failed units reproduce exactly. Output partitions are
overwritten in place, and on a fully successful (re-)run the stale `failures.json` is removed.

| Exit code | Meaning |
|---|---|
| `0` | Success — every unit completed |
| `1` | Fatal error — invalid config, PJNZ import failure, or no PJNZ files found |
| `2` | Partial — some scenario units failed; output produced and `failures.json` written |

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

Valid `product` values: `"Oral PrEP (daily)"`, `"Oral PrEP (monthly)"`,
`"Injectable PrEP (1 month)"`, `"Injectable PrEP (2 month)"`,
`"Injectable PrEP (6 month)"`, `"Oral PrEP plus contraceptive"`,
`"PrEP ring"`, `"Implantable PrEP"`, `"bNABs"`, `"PEP"`

`targets`: one or more risk group/sex combinations.

| Field | Values |
|---|---|
| `risk_group` | `"Low risk heterosexual"`, `"Medium risk heterosexual"`, `"High risk heterosexual"`, `"People who inject drugs"`, `"Men who have sex with men"` |
| `sex` | `"Male"`, `"Female"`, `"Both"` |

`"Men who have sex with men"` cannot have `sex: "Female"`.

`parameters`:

| Parameter | Description |
|---|---|
| `efficacy` | Distribution for intervention efficacy (proportion, 0–1) |
| `adherence` | Distribution for adherence (proportion, 0–1) |
| `target_coverage` | Distribution for target population coverage (proportion, 0–1) |
| `target_year` | Distribution for target implementation year (integer ≥ 1970) |
| `substitution` | Distribution for substitution (proportion, 0–1). **Only valid for `"Oral PrEP plus contraceptive"`.** |
| `duration` | Distribution for implant duration in months (≥ 0). **Only valid for `"Implantable PrEP"`.** |

Each distribution is `{"mean": <float>, "sd": <float>}` with optional `min_value` and `max_value` overrides.

`substitution` and `duration` are optional and product-specific: setting `substitution` on any
product other than `"Oral PrEP plus contraceptive"`, or `duration` on anything other than
`"Implantable PrEP"`, is a validation error. When omitted, the model's PJNZ default is used.

```json
{
  "product": "Oral PrEP (daily)",
  "targets": [
    {"risk_group": "High risk heterosexual", "sex": "Female"},
    {"risk_group": "Men who have sex with men", "sex": "Male"}
  ],
  "parameters": {
    "efficacy":        {"mean": 0.95, "sd": 0.03},
    "adherence":       {"mean": 0.85, "sd": 0.05},
    "target_coverage": {"mean": 0.30, "sd": 0.05},
    "target_year":     {"mean": 2028, "sd": 2}
  }
}
```

Implantable PrEP with a `duration` (months), and Oral PrEP plus contraceptive with a `substitution`:

```json
{
  "product": "Implantable PrEP",
  "targets": [{"risk_group": "High risk heterosexual", "sex": "Female"}],
  "parameters": {
    "efficacy":    {"mean": 0.90, "sd": 0.03},
    "adherence":   {"mean": 0.85, "sd": 0.05},
    "target_year": {"mean": 2028, "sd": 2},
    "duration":    {"mean": 12, "sd": 1}
  }
}
```

---

##### Vaccine

`product`: `"Vaccine"`

`targets`: one or more entries (one or more required). Two targeting modes:

- **PLHIV** — applies coverage across all PLHIV regardless of risk group. Use `risk_group: "PLHIV"` with `sex: "Both"` or omit `sex`.
- **Risk group** — targets a specific risk group. Use the same `risk_group` and `sex` values as PrEP. `"Both"` applies coverage to both male and female indices for that group.

`"Men who have sex with men"` cannot have `sex: "Female"`. `"PLHIV"` cannot have `sex: "Male"` or `"Female"`.

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

```json
{
  "product": "Vaccine",
  "targets": [
    {"risk_group": "PLHIV"}
  ],
  "parameters": {
    "target_year":                           {"mean": 2035, "sd": 3},
    "target_coverage":                       {"mean": 0.50, "sd": 0.10},
    "reduction_in_susceptibility":           {"mean": 0.60, "sd": 0.05},
    "reduction_in_infectiousness":           {"mean": 0.40, "sd": 0.05},
    "increase_in_progression_time_to_aids":  {"mean": 0.20, "sd": 0.02},
    "vaccine_duration_years":                {"mean": 5,    "sd": 1},
    "vaccine_action_type":                   "Take",
    "targeting":                             "Vaccinate only HIV-negative individuals"
  }
}
```

---

##### Cure

`product`: `"Cure (adults and children)"`

`targets`: one or more entries (one or more required). Same two targeting modes as Vaccine:

- **PLHIV** — `risk_group: "PLHIV"` with `sex: "Both"` or omit `sex`.
- **Risk group** — same `risk_group` and `sex` values as PrEP. `"Both"` applies coverage to both male and female indices.

`"Men who have sex with men"` cannot have `sex: "Female"`. `"PLHIV"` cannot have `sex: "Male"` or `"Female"`.

`parameters`:

| Parameter | Description |
|---|---|
| `target_year` | Target implementation year |
| `target_coverage` | Target coverage (0–1) |
| `efficacy` | Efficacy of the cure (0–1) |
| `duration_of_cure` | Duration of cure effect |

```json
{
  "product": "Cure (adults and children)",
  "targets": [
    {"risk_group": "PLHIV"}
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

##### POC VL test

`product`: `"POC VL test"`

No `targets` field.

`parameters`:

| Parameter | Description |
|---|---|
| `target_year` | Target implementation year |
| `target_coverage` | Target coverage (0–1) |
| `effect` | Effect size (0–1) |

```json
{
  "product": "POC VL test",
  "parameters": {
    "target_year":     {"mean": 2027, "sd": 1},
    "target_coverage": {"mean": 0.70, "sd": 0.08},
    "effect":          {"mean": 0.50, "sd": 0.05}
  }
}
```

---

##### POC CD4 test

`product`: `"POC CD4 test"`

Same structure as POC VL test.

```json
{
  "product": "POC CD4 test",
  "parameters": {
    "target_year":     {"mean": 2027, "sd": 1},
    "target_coverage": {"mean": 0.70, "sd": 0.08},
    "effect":          {"mean": 0.50, "sd": 0.05}
  }
}
```

---

##### Adult ART

`product`: `"Adult ART"`

`targets`: one or more entries, each specifying a sex.

| Field | Values |
|---|---|
| `sex` | `"Male"`, `"Female"`, `"Both"` |

`parameters`:

| Parameter | Description |
|---|---|
| `target_coverage` | Target ART coverage as a proportion (0–1) |
| `target_year` | Target implementation year (integer ≥ 1970) |

Coverage values are interpreted as proportions (ratio between 0 and 1). `adults_on_art_is_percent` is automatically set to 1 for the targeted sex and year.

```json
{
  "product": "Adult ART",
  "targets": [
    {"sex": "Female"},
    {"sex": "Male"}
  ],
  "parameters": {
    "target_coverage": {"mean": 0.85, "sd": 0.05},
    "target_year":     {"mean": 2028, "sd": 2}
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
          "id": "oral_prep_daily",
          "product": "Oral PrEP (daily)",
          "targets": [
            { "risk_group": "High risk heterosexual", "sex": "Female" },
            { "risk_group": "Men who have sex with men", "sex": "Male" }
          ]
        }
      ],
      "simulations": [
        {
          "oral_prep_daily": {
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

### Failures manifest JSON

Written to `<output_dir>/failures.json` whenever one or more `(PJNZ, scenario)` units fail.
Pass it back to `run --retry` to re-run only those units.

```json
{
  "failures": [
    { "pjnz": "Zimbabwe", "scenario_id": "3", "error": "..." }
  ]
}
```

| Field | Description |
|---|---|
| `pjnz` | Stem of the PJNZ file whose scenario failed (no `.PJNZ`) |
| `scenario_id` | Identifier of the scenario that failed for that PJNZ |
| `error` | Short error message describing the failure |

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
