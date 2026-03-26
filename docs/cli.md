# CLI

The `goals-sa` CLI provides two commands.

## Installation

```bash
pip install goals-sa
```

After installation, `goals-sa` is available on your PATH.

## Commands

### `scenarios`

Generates a scenarios file at the given path.

```bash
goals-sa scenarios --dest-path ./scenarios.csv
```

| Option | Description |
|---|---|
| `--dest-path` | Path to write the generated scenarios file to |

---

### `run`

Runs scenario analysis across a directory of PJNZ files, driven by a JSON config file.

```bash
goals-sa run --config-path config.json
```

| Option | Description |
|---|---|
| `--config-path` | Path to a JSON config file |

#### Config file format

Field names are case-insensitive (`Goals_path`, `goals_path`, and `GOALS_PATH` are all accepted).

```json
{
  "Goals_path": "path/to/pjnz/files",
  "Scenario_path": "path/to/scenarios",
  "Scenario_file_name": "scenarios.csv",
  "Output_path": "path/to/output",
  "Output_file_name": "results.parquet",
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
| `Scenario_path` | Directory containing the scenario file |
| `Scenario_file_name` | Filename of the scenario CSV |
| `Output_path` | Directory to write output to |
| `Output_file_name` | Filename for the output file |
| `Base_year` | Base year for the analysis |
| `Output_indicators` | List of indicators to include in output |

## Global options

| Option | Description |
|---|---|
| `--version`, `-v` | Show version and exit |
| `--help`, `-h` | Show help and exit |

## Tab completion

```bash
goals-sa --install-completion
```
