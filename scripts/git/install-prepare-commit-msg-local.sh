#!/bin/bash

set -eu
set -o pipefail

# Adds a prepare-commit-msg hook to the local (repo) git configuration.

script_dir=$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")
source ${script_dir}/install-prepare-commit-msg.sh

export hook_file=${script_dir}/../../.git/hooks/prepare-commit-msg

install_prepare_commit_msg

git config core.hooksPath $(dirname ${hook_file})
