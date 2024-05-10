# ska-mid-itf-engineering-tools

[![Documentation Status](https://readthedocs.org/projects/ska-mid-itf-engineering-tools/badge/?version=latest)](https://developer.skatelescope.org/projects/ska-mid-itf-engineering-tools/en/latest/?badge=latest)

## Introduction

This repo provides a suite of utilities for use in the Mid ITF environment:

* *dependency_checker*, a utility to check Helm and Poetry dependencies
* *cbf_config*, a utility for configuring the CBF
* *tmc_config*, a utility for configuring the TMC with the correct Dishes in the SUT.
* *git*, tools for working with git. Currently contains a hook for adding Jira issue IDs to commit messages.

## How to Use

Clone this repo:

```
git clone https://gitlab.com/ska-telescope/ska-mid-itf-engineering-tools.git
cd ska-mid-itf-engineering-tools
git submodule update --init --recursive
```

Build the image

```
make oci-build
```

Install python requirements

```
poetry install
```

Run tests

```
poetry shell
make python-test
```

Lint code

```
make python-lint
```

### Making a release

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

## Dependency Checker

The dependency checker is a tool which looks at a project's dependencies and reports any stale dependencies to a Slack channel. It checks both Poetry dependencies and dependencies present in Helm charts.

### Configuration

The only configuration needed is to set the environment variable `DEPENDENCY_CHECKER_WEBHOOK_URL`. This is typically set as a masked Gitlab variable.

### Execution

The dependency checker Gitlab job, *check-dependencies*, is run as part of a scheduled pipeline on a weekly basis. It can also be executed manually from any pipeline. For this project, it reports stale dependencies to the [#atlas-dependencies](https://skao.slack.com/archives/C06MR162K24) channel.

## Commit Message Preparer

The Commit Message Preparer is used to prepend a Jira issue ID to your commit message, if there is one present.
You can install it as follows:

```
# Installs it for this repo only
make install-prepare-commit-msg-local
# Installs it globally
make install-prepare-commit-msg-global
```

**The global install will only affect working with SKA repositories.**
The tool uses a whitelist of origin prefixes to determine which repos it should be used in and it is configured to only work with SKA repos.

**The tool only works on branches prefixed with the Jira issue ID.**

**The tool will not add the Jira issue ID if the commit message already starts with one.**
