# goals-scenario

[![Release](https://img.shields.io/github/v/release/avenirhealth-org/goals-scenario)](https://img.shields.io/github/v/release/avenirhealth-org/goals-scenario)
[![Build status](https://img.shields.io/github/actions/workflow/status/avenirhealth-org/goals-scenario/main.yml?branch=main)](https://github.com/avenirhealth-org/goals-scenario/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/avenirhealth-org/goals-scenario/branch/main/graph/badge.svg)](https://codecov.io/gh/avenirhealth-org/goals-scenario)
[![Commit activity](https://img.shields.io/github/commit-activity/m/avenirhealth-org/goals-scenario)](https://img.shields.io/github/commit-activity/m/avenirhealth-org/goals-scenario)
[![License](https://img.shields.io/github/license/avenirhealth-org/goals-scenario)](https://img.shields.io/github/license/avenirhealth-org/goals-scenario)

# Goals scenario analysis

- **Github repository**: <https://github.com/avenirhealth-org/goals-scenario/>
- **Documentation**: <https://avenirhealth-org.github.io/goals-scenario/>

## Installation

```bash
pip install avenir_goals_scenario
```

After installation, the `goals-scenario` command is available on your PATH.

## Quick start

For full details of the CLI please see the [CLI reference](https://avenirhealth-org.github.io/goals-scenario/cli/)

```bash
goals-scenario --help      # or -h
goals-scenario --version
```

### Generate scenario simulations

```bash
goals-scenario simulations scenario_definition.csv scenario_simulations.json
# optionally override the number of simulations (default 100):
goals-scenario simulations scenario_definition.csv scenario_simulations.json -n 500
```

#### File formats

Scenario definition CSV

Multiple rows sharing the same `Number` represent multiple target populations for that
intervention - all parameter columns must be identical across those rows, only `Target Population`
and `Sex` may differ. A combined scenario has the IDs to combine joined by `+` in the `Product`
column. Column headers are case-insensitive.

```
Number,Product,Efficacy mean,Efficacy STD,Adherence mean,Adherence STD,Target Coverage mean,Target Coverage STD,Target Year mean,Target Year STD,Target Population,Sex
1,One month pill for PrEP,0.95,0.03,0.95,0.03,0.20,0.05,2028,2,High risk heterosexual,Female
1,One month pill for PrEP,0.95,0.03,0.95,0.03,0.20,0.05,2028,2,Men who have sex with men,Male
2,Daily PrEP,0.95,0.03,0.80,0.20,0.10,0.05,2027,2,High risk heterosexual,Female
...
25,1+2,,,,,,,,,,
...
```

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
  ]
}
```

### Run scenario analysis

Analysis is configured via a JSON config file:

```bash
goals-scenario run config.json
```

#### Config file format

Field names are case-insensitive.

```json
{
  "pjnz_dir": "path/to/pjnz/files",
  "scenario_path": "path/to/scenario_simulations.json",
  "output_dir": "path/to/output",
  "base_year": 2025,
  "output_indicators": [
    "p_hivpop",
    "p_infections",
    "p_hiv_deaths",
    "h_artpop"
  ]
}
```

| Field | Description |
|---|---|
| `pjnz_dir` | Directory containing `.PJNZ` files |
| `scenario_path` | Path to the scenario simulations JSON file |
| `output_dir` | Directory to write results to (created if absent; parent must exist) |
| `base_year` | First year of the output projection range |
| `output_indicators` | Goals output indicator names to extract |

### Tab completion

To install shell tab completion:

```bash
goals-scenario --install-completion
```

## Development

### Architecture

![architecture diagram](images/goals_scenario_architecture.png)

### Prerequisites

* [uv](https://docs.astral.sh/uv/) for installing Python, package management
* (Optionally) [make](https://www.gnu.org/software/make/). Should be installed by default, except on windows, where it is easiest to install it via [Chocolatey](https://chocolatey.org/install) `choco install make`

### Development with make

There is a `Makefile` which wraps some common `uv` commands you will need during development.

#### Set Up Your Development Environment

Install the environment and the pre-commit hooks with

```bash
make install
```

This will also generate your `uv.lock` file.

#### Run code checks

```bash
make check
```

#### Run tests

```bash
make test
```

#### Build docs site

```bash
make docs
```

### Development with uv

If you choose not to use make, you can use `uv` directly.

#### Set Up Your Development Environment

Install the environment and the pre-commit hooks with

```bash
uv sync
uv run pre-commit install
```

This will also generate your `uv.lock` file.

#### Run code checks

Run pre-commit checks, include ruff linting and formatting

```bash
uv run pre-commit run -a
```

Run type checking

```bash
uv run ty check
```

Check for vulnerabilities in pypi dependencies

```bash
uv run pip-audit --desc -s osv
```

#### Run tests

```bash
uv run pytest
```

#### Build docs site

```bash
uv run mkdocs serve
```

#### Run compatibility tests

Compatability tests with tox are configured. Run them with

```bash
uv run tox
```

These are also run on CI, so not the end of the world if you don't do it locally.

### Vendored SpectrumEngine import code

We need to re-use some of the PJNZ import code from SpectrumEngine. At the moment, this is vendored here directly. There is a script to update the vendored code which should be run before a release. The script uses a file `./scripts/spectrum_engine_ref` to clone the specified branch or ref.

With make:

```bash
make pjnz-import-code
```

Run script directly
```bash
uv run ./scripts/update_pjnz_import_code.py
```

### CLI

The CLI is built using [typer](https://typer.tiangolo.com/) which builds CLI docs automatically from python type hints and decorators. It also gives us some neat things like auto completion. And progress bars down the line!

## Release process

Creating a release will

1. Build & push the package to PyPI
2. Build an updated docs site

To create a release you need to

1. Update the version number in the `pyproject.toml` or ensure it has updated since the last release
2. Go to the [releases page](https://github.com/AvenirHealth-org/goals-scenario/releases) and "Draft a new release"
3. Create a new tag, I usually use a tag which matches the version number you are releasing. Set a release title and text. Usually useful to include in the text a summary of the changes since the last release.
4. Publish the release. This will trigger a GitHub action which will push the package to PyPI and update the docs site.
