#!/bin/bash

set -eu
set -o pipefail

script_dir=$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")
source ${script_dir}/install-prepare-commit-msg.sh

export hook_file=${HOME}/.git/hooks/prepare-commit-msg

install_prepare_commit_msg

