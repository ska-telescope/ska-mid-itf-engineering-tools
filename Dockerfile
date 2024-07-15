ARG OCI_IMAGE_VERSION=ubuntu:22.04
FROM $OCI_IMAGE_VERSION as base

ARG POETRY_VERSION=1.8.2
ARG DEBIAN_FRONTEND=noninteractive
ARG TZ=Etc/UTC

RUN apt-get update && \
    apt-get install gnupg2 gawk yamllint vim telnet expect sshpass inetutils-ping netcat wget -y && \
    wget https://github.com/infrahq/infra/releases/download/v0.21.0/infra_0.21.0_amd64.deb && \
    apt install ./infra_*.deb && \
    apt-get clean && apt clean

ENV PATH=/app/bin:/root/.local/bin:$PATH

ENV PYTHONPATH="/app/src:${PYTHONPATH}"

RUN python3 -m pip install --user pipx && \
    python3 -m pipx ensurepath && \
    pipx install poetry==$POETRY_VERSION && \
    pipx install build && \
    poetry config virtualenvs.in-project true && \
    pip install virtualenv

WORKDIR /app

FROM base
COPY . /app

RUN poetry install

ENV PYTHONPATH="/app/src:${PYTHONPATH}:/app/.venv/lib/python3.10/site-packages"
ENV PATH=/app/bin:/app/.venv/bin:/root/.local/bin:$PATH

USER root

ENV PATH=/app/.venv/bin/:$PATH

CMD ["bash"]
