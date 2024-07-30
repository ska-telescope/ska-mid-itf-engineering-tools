ARG OCI_IMAGE_VERSION=artefact.skao.int/ska-cicd-k8s-tools-build-deploy:0.13.2
FROM $OCI_IMAGE_VERSION as base

ARG POETRY_VERSION=1.8.2
ARG DEBIAN_FRONTEND=noninteractive
ARG TZ=Etc/UTC

ENV USER=tango
ENV HOME /home/${USER}
RUN useradd --create-home --home-dir ${HOME} ${USER}
RUN usermod -u 1000 -g 1000 ${USER}
ENV PATH=/home/${USER}/.local/bin:$PATH

USER ${USER}
WORKDIR ${HOME}
ENV PATH=/usr/bin:$PATH
RUN python3 -m pip install poetry==$POETRY_VERSION
RUN python3 -m pip install build
RUN poetry config virtualenvs.in-project true
RUN python3 -m pip install virtualenv
RUN python3 -m pip install --user pipx
RUN python3 -m pipx ensurepath

ENV PYTHONPATH="/app/src:${PYTHONPATH}" 

COPY . /app

WORKDIR /app

FROM base
COPY . /app

RUN poetry install --no-interaction --no-root

ENV PYTHONPATH="/app/src:${PYTHONPATH}:/app/.venv/lib/python3.10/site-packages"
ENV PATH=/app/bin:/app/.venv/bin:/root/.local/bin:$PATH

#Commands below require root privileges
USER root

RUN apt-get update && \
    apt-get install gnupg2 gawk yamllint vim telnet expect sshpass inetutils-ping netcat wget -y && \
    wget https://github.com/infrahq/infra/releases/download/v0.21.0/infra_0.21.0_amd64.deb && \
    apt install ./infra_*.deb && \
    apt-get clean && apt clean

ENV PATH=/app/.venv/bin:$PATH

CMD ["bash"]
