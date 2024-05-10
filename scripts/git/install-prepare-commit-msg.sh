set -eu
set -o pipefail


# install_prepare_commit_msg adds a prepare-commit-msg hook which
# inserts the Jira ID of your branch to your commit message.
#
# Environment Variables (REQUIRED):
#   hook_file: file location to install the hook.
install_prepare_commit_msg () {
    script_dir=$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")
    command='poetry run prepare_commit_msg ${1}'

    if grep -q "${command}" "${hook_file}"; then
        echo "Hook already installed at ${hook_file}, not installing it again."
        exit 1
    fi
    echo "Installing prepare-commit-msg at ${hook_file}"

    mkdir -p "$(dirname "${hook_file}")"

    if [ -f ${hook_file} ]; then
        cat <<EOF >> ${hook_file}
(cd ${script_dir}/../../ && ${command})
EOF
    else
        cat <<EOF >> ${hook_file}
#!/bin/bash

set -eu
set -o pipefail

echo "commit msg file: \${1}"
(cd ${script_dir}/../../ && ${command})
cp \${1} ../../commit-msg.txt
EOF
    fi

    chmod +x ${hook_file}
    echo "Installed prepare-commit-msg at ${hook_file}"
    git config core.hooksPath $(dirname ${hook_file})
}