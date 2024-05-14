set -eu
set -o pipefail


# install_prepare_commit_msg adds a prepare-commit-msg hook which
# inserts the Jira ID of your branch to your commit message.
#
# Environment Variables (REQUIRED):
#   hook_file: file location to install the hook.
install_prepare_commit_msg () {
    command='prepare_commit_msg ${1}'
    venv_dir=$(poetry env info -p)
    full_command=${venv_dir}/bin/${command}

    if grep -q "${command}" "${hook_file}"; then
        echo "Hook already installed at ${hook_file}, not installing it again."
        exit 1
    fi
    echo "Installing prepare-commit-msg at ${hook_file}"

    mkdir -p "$(dirname "${hook_file}")"

    if [ -f ${hook_file} ]; then
        cat <<EOF >> ${hook_file}
${full_command}
EOF
    else
        cat <<EOF >> ${hook_file}
#!/bin/bash

set -eu
set -o pipefail

${full_command}
EOF
    fi

    chmod +x ${hook_file}
    echo "Installed prepare-commit-msg at ${hook_file}"
}