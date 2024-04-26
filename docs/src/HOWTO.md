# ska-mid-itf-engineering-tools

[![Documentation Status](https://readthedocs.org/projects/ska-mid-itf-engineering-tools/badge/?version=latest)](https://developer.skatelescope.org/projects/ska-mid-itf-engineering-tools/en/latest/?badge=latest)

## Introduction

This repo provides a suite of utilities for use in the Mid ITF environment:

* *dependency_checker*, a utility to check Helm and Poetry dependencies
* *cbf_config*, a utility for configuring the CBF
* *tmc_config*, a utility for configuring the TMC with the correct Dishes in the SUT.

## How to Use

Clone this repo:

```
git clone https://gitlab.com/ska-telescope/ska-mid-itf-engineering-tools.git
cd ska-mid-itf-engineering-tools
git submodule update --init --recursive
```

## How to make a release

The following steps happen in different locations.

1. Complete the feature/story/bug related branch MR(s) and get it approved and merged.
2. JIRA:
   1. create a release (REL) ticket in [REL JIRA project](https://jira.skatelescope.org/secure/Dashboard.jspa?selectPageId=15204)
   2. set ticket status to `IN PROGRESS`
3. Local repo:
   1. `git checkout main && git pull`
   2. show current version: `make show-version`
   3. create release branch: `git checkout -b rel-1319-release-v0-5-2`
   4. bump version: `make bump-<major|minor|patch>-release`
   5. Manually edit whatever is not yet up-to-date
   6. `git push` (and convince Git to create the remote branch by running the suggested command)
4. Gitlab:
   1. Create new MR and get it
   2. approved and
   3. merged
5. Local repo:
   1. `git checkout main && git pull`
   2. Tag step 1: `make git-create-tag`
   3. Tag step 2: `make git-push-tag`
6. Gitlab:
   1. Check if your new tag pipeline successfully ran and automatically linked the new Release to the Jira ticket
7. Jira:
   1. Mark the ticket as `READY FOR RELEASE`
8. Downstream repo / local test bed & Jira:
   1. install/use the new artifact and convince yourself that this release is fit for use
   2. If not fit for use:
      1. Set JIRA ticket status to `DO NOT USE`
      2. Notify colleagues / collaborators
   3. If fit for use:
      1. Set JIRA ticket status to `RELEASED`

*NOTE: Step 8 should be carried out by the Product Owner, not Developers.*

## Testing

Build a new Docker image for the project:

```
$ make oci-build
[...]
[+] Building 111.7s (14/14) FINISHED 
[...]
```

Install python requirements:

```
poetry install
```

Run python-test:

```
$ poetry shell
$ make python-test

pytest 6.2.5
PYTHONPATH=/home/ubuntu/ska-mid-itf-engineering-tools/src:/app/src:  pytest  \
 --cov=src --cov-report=term-missing --cov-report html:build/reports/code-coverage --cov-report xml:build/reports/code-coverage.xml --junitxml=build/reports/unit-tests.xml tests/
=============================================================================================== test session starts ================================================================================================
platform linux -- Python 3.10.12, pytest-6.2.5, py-1.11.0, pluggy-1.3.0
rootdir: /home/ubuntu/ska-mid-itf-engineering-tools, configfile: pyproject.toml
plugins: cov-4.1.0, metadata-2.0.4, bdd-5.0.0, json-report-1.5.0, repeat-0.9.3, ska-ser-skallop-2.29.6
collected 4 items                                                                                                                                                                                                  

tests/functional/tmc/test_deployment.py ....                                                                                                                                                                 [100%]

----------------------------------------------------------- generated xml file: /home/ubuntu/ska-mid-itf-engineering-tools/build/reports/unit-tests.xml ------------------------------------------------------------

---------- coverage: platform linux, python 3.10.12-final-0 ----------
Name                                                Stmts   Miss  Cover   Missing
---------------------------------------------------------------------------------
src/ska_mid_itf_engineering_tools/__init__.py           0      0   100%
src/ska_mid_itf_engineering_tools/tmc_dish_ids.py      47     12    74%   74, 167, 169, 171, 173, 199-205, 209-214
---------------------------------------------------------------------------------
TOTAL                                                  47     12    74%
Coverage HTML written to dir build/reports/code-coverage
Coverage XML written to file build/reports/code-coverage.xml

================================================================================================ 4 passed in 0.10s =================================================================================================

```

Python linting:

```
$ make python-lint
[...]
--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)
```

## Dependency Checker

The dependency checker is a tool which looks at a project's dependencies and reports any stale dependencies to a Slack channel. It checks both Poetry dependencies and dependencies present in Helm charts.

### Configuration

The only configuration needed is to set the environment variable `DEPENDENCY_CHECKER_WEBHOOK_URL`. This is typically set as a masked Gitlab variable.

### Execution

The dependency checker Gitlab job, *check-dependencies*, is run as part of a scheduled pipeline on a weekly basis. It can also be executed manually from any pipeline. For this project, it reports stale dependencies to the [#atlas-dependencies](https://skao.slack.com/archives/C06MR162K24) channel.
