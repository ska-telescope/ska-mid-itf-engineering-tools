ARG OCI_IMAGE_VERSION=artefact.skao.int/ska-cicd-k8s-tools-build-deploy:0.13.2
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
ENV TANGO_GRP 1001
RUN useradd --create-home --home-dir ${HOME} ${USER}
RUN usermod -u ${TANGO_GRP} -g ${TANGO_GRP} ${USER}
ENV PATH=${HOME}/.local/bin:$PATH

USER ${USER}
WORKDIR ${HOME}

ENV PATH=/app/bin:/app/.local/bin:$PATH

ENV PYTHONPATH="/app/src:${PYTHONPATH}"

#RUN chown tango:1000 /app/.venv/bin/python

RUN python3 -m pip install poetry==$POETRY_VERSION && \
    python3 -m pip install build && \
    poetry config virtualenvs.in-project true && \
    python3 -m pip install virtualenv

COPY --chown=${USER} . /app

WORKDIR /app

FROM base

COPY --chown=${USER} . /app

RUN poetry install --no-interaction --no-root

ENV PYTHONPATH="/app/src:${PYTHONPATH}/app/.venv/lib/python3.10/site-packages"
ENV PATH=/app/bin:/app/.venv/bin:/app/.local/bin:$PATH

ENV PATH=/app/.venv/bin:$PATH

USER root

#Ensure all non users can run poetry and python binaries
RUN chown -R ${USER}:${TANGO_GRP} /root

CMD ["bash"]
