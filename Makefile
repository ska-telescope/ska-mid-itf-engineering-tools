PYTHON_LINE_LENGTH = 99

OCI_BUILD_ADDITIONAL_ARGS=--build-arg OCI_IMAGE_VERSION=$(SKA_K8S_TOOLS_BUILD_DEPLOY)

# include OCI Images support
include .make/oci.mk

# include k8s support
include .make/k8s.mk

# include Helm Chart support
include .make/helm.mk

# Include Python support
include .make/python.mk

# include raw support
include .make/raw.mk

# include core make support
include .make/base.mk

# supporting scripts for changelog generation using git-chglog and GitLab release pages
include .make/release.mk

# include your own private variables for custom deployment configuration
-include PrivateRules.mak
