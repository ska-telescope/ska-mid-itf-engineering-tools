ARG OCI_IMAGE_VERSION
FROM $OCI_IMAGE_VERSION as base

ARG POETRY_VERSION=1.8.2
ARG DEBIAN_FRONTEND=noninteractive
ARG TZ=Etc/UTC

#Commands below require root privileges
USER root

RUN apt-get update && \
    apt-get install gnupg2 gawk yamllint vim telnet expect sshpass inetutils-ping netcat wget -y && \
    wget https://github.com/infrahq/infra/releases/download/v0.21.0/infra_0.21.0_amd64.deb && \
    apt install ./infra_*.deb && \
    apt-get clean && apt clean

ENV USER=tango
ENV HOME /app
RUN useradd --create-home --home-dir ${HOME} ${USER}
RUN usermod -u 1000 -g 1000 ${USER}
ENV PATH=${HOME}/.local/bin:$PATH

USER ${USER}
WORKDIR ${HOME}

ENV PATH=/app/bin:/app/.local/bin:$PATH

ENV PYTHONPATH="/app/src:${PYTHONPATH}"

RUN python3 -m pip install poetry==$POETRY_VERSION && \
    python3 -m pip install build && \
    poetry config virtualenvs.in-project true && \
    python3 -m pip install virtualenv

COPY . /app

WORKDIR /app

FROM base

COPY . /app

RUN poetry install --no-interaction --no-root

ENV PYTHONPATH="/app/src:${PYTHONPATH}/app/.venv/lib/python3.10/site-packages"
ENV PATH=/app/bin:/app/.venv/bin:/app/.local/bin:$PATH

ENV PATH=/app/.venv/bin:$PATH

RUN chown -R tango:1000 /app

USER root

CMD ["bash"]
