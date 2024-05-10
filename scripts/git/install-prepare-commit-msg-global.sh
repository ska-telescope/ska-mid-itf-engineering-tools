#!/bin/bash

set -eu
set -o pipefail

# Adds a prepare-commit-msg hook to the global git configuration.

script_dir=$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")
source ${script_dir}/install-prepare-commit-msg.sh

export hook_file=${HOME}/.git/hooks/prepare-commit-msg

install_prepare_commit_msg

git config --unset core.hooksPath
git config --global core.hooksPath $(dirname ${hook_file})

