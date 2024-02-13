ARG OCI_IMAGE_VERSION
FROM $OCI_IMAGE_VERSION as base

ARG POETRY_VERSION=1.3.2
ARG DEBIAN_FRONTEND=noninteractive
ARG TZ=Etc/UTC

RUN apt-get update && \
    apt-get install gnupg2 gawk yamllint vim telnet expect sshpass inetutils-ping netcat -y && \
    apt-get clean && apt clean

ENV PATH=/root/.local/bin:$PATH

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

USER root

ENV PATH=/app/.venv/bin/:$PATH

CMD ["bash"]
