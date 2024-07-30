ARG OCI_IMAGE_VERSION
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
WORKDIR /home/${USER}
ENV PATH=/usr/bin:$PATH
RUN python3 -m pip install poetry==$POETRY_VERSION
RUN python3 -m pip install build
RUN poetry config virtualenvs.in-project true
RUN python3 -mpip install virtualenv

WORKDIR /build/ska-telescope/ska-mid-itf

FROM base as tools

#Commands below require root privileges
USER root

RUN apt-get update && \
    apt-get install gnupg2 gawk yamllint vim telnet expect sshpass inetutils-ping netcat wget -y && \
    wget https://github.com/infrahq/infra/releases/download/v0.21.0/infra_0.21.0_amd64.deb && \
    apt install ./infra_*.deb && \
    apt-get clean && apt clean

FROM tools

ENV PATH=/build/ska-telescope/ska-mid-itf/.venv/bin/:$PATH

COPY . .

RUN poetry shell && poetry install

CMD ["bash"]
