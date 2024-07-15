ARG OCI_IMAGE_VERSION=harbor.skao.int/production/ska-cicd-k8s-tools-build-deploy:0.13.1
ARG TANGO_BUILD_IMAGE="harbor.skao.int/production/ska-tango-images-pytango-builder:9.5.0"
ARG TANGO_BASE_IMAGE="harbor.skao.int/production/ska-tango-images-pytango-runtime:9.5.0"
FROM $OCI_IMAGE_VERSION as base

USER root

ARG POETRY_VERSION=1.8.2
ARG DEBIAN_FRONTEND=noninteractive
ARG TZ=Etc/UTC

RUN apt-get update && \
    apt-get install gnupg2 gawk yamllint vim telnet expect sshpass inetutils-ping netcat wget -y && \
    wget https://github.com/infrahq/infra/releases/download/v0.21.0/infra_0.21.0_amd64.deb && \
    apt install ./infra_*.deb && \
    apt-get clean && apt clean

RUN poetry self update -n ${POETRY_VERSION} && \
    poetry config virtualenvs.create false && \
    pip install --upgrade pip


# ENV PATH=/app/bin:/root/.local/bin:$PATH

# ENV PYTHONPATH="/app/src:${PYTHONPATH}"

# RUN python3 -m pip install --user pipx && \
#     python3 -m pipx ensurepath && \
#     pipx install poetry==$POETRY_VERSION && \
#     pipx install build && \
#     poetry config virtualenvs.in-project true && \
#     pip install virtualenv

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry export --format requirements.txt --output poetry-requirements.txt --without-hashes && \
    pip install -r poetry-requirements.txt && \
    rm poetry-requirements.txt 

# COPY --chown=tango:tango src ./

FROM base

COPY . /app

# FROM $TANGO_BUILD_IMAGE AS buildenv
# FROM $TANGO_BASE_IMAGE AS base_env
# USER tango

ENV PYTHONPATH=/app/src:/usr/local/lib/python3.10/site-packages

# RUN poetry install

# ENV PYTHONPATH="/app/src:${PYTHONPATH}:/app/.venv/lib/python3.10/site-packages"
# ENV PATH=/app/bin:/app/.venv/bin:/root/.local/bin:$PATH

# USER root

# ENV PATH=/app/.venv/bin/:$PATH

CMD ["bash"]
