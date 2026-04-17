# goals-scenario

[![Release](https://img.shields.io/github/v/release/avenirhealth-org/goals-scenario)](https://img.shields.io/github/v/release/avenirhealth-org/goals-scenario)
[![Build status](https://img.shields.io/github/actions/workflow/status/avenirhealth-org/goals-scenario/main.yml?branch=main)](https://github.com/avenirhealth-org/goals-scenario/actions/workflows/main.yml?query=branch%3Amain)
[![Commit activity](https://img.shields.io/github/commit-activity/m/avenirhealth-org/goals-scenario)](https://img.shields.io/github/commit-activity/m/avenirhealth-org/goals-scenario)
[![License](https://img.shields.io/github/license/avenirhealth-org/goals-scenario)](https://img.shields.io/github/license/avenirhealth-org/goals-scenario)

`goals-scenario` runs scenario analysis with the [leapfrog Goals model](https://github.com/hivtools/leapfrog). Given a set of intervention scenarios and a directory of PJNZ files, it samples intervention parameters across simulations, runs the Goals model for each draw, and writes the results to HDF5 files.

There are two ways to use it:

- **CLI** - drive runs from a JSON config file with the `goals-scenario run` command. See the [CLI reference](cli.md) for full command documentation and config format.
- **Python API** - call [`run_scenario_analysis`][avenir_goals_scenario.run_scenario_analysis] and [`generate_simulations`][avenir_goals_scenario.generate_simulations] directly from Python. See the [API reference](reference.md).
