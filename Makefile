
# include core make support
include .make/base.mk

PYTHON_LINE_LENGTH = 99
OCI_BUILD_ADDITIONAL_ARGS=--build-arg OCI_IMAGE_VERSION=$(SKA_K8S_TOOLS_BUILD_DEPLOY)
PYTHON_RUNNER := poetry run
DOCS_SPHINXBUILD := poetry run python -m sphinx

ifneq ($(CI_JOB_ID),)
DEV_TAG := $(VERSION)-dev.c$(CI_COMMIT_SHORT_SHA)
OCI_BUILD_ADDITIONAL_TAGS += $(DEV_TAG)
endif

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

# include your own private variables for custom deployment configuration
-include PrivateRules.mak

python-do-publish:
	echo "OVERRIDEN"
	$(PYTHON_RUNNER) twine upload --verbose --username ${PYTHON_PUBLISH_USERNAME} --password ${PYTHON_PUBLISH_PASSWORD} --repository-url $(PYTHON_PUBLISH_URL) dist/*
