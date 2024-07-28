ARG OCI_IMAGE_VERSION=artefact.skao.int/ska-cicd-k8s-tools-build-deploy:0.11.0
FROM $OCI_IMAGE_VERSION as base

ARG POETRY_VERSION=1.3.2
ARG DEBIAN_FRONTEND=noninteractive
ARG TZ=Etc/UTC



ENV PATH=/root/.local/bin:$PATH

#Change from root user
ENV USER=newuser
RUN adduser --system --home /home/${USER} --shell /usr/bin --gid 0 ${USER}
#RUN adduser -D ${USER}
USER ${USER}
WORKDIR /home/${USER}

RUN python3 -m pip install --user pipx && \
    python3 -m pipx ensurepath && \
    python3 -m pipx install poetry==$POETRY_VERSION && \
    python3 pipx install build && \
    poetry config virtualenvs.in-project true && \
    pip install virtualenv

WORKDIR /app

FROM base
COPY . /app

RUN poetry install

USER root

ENV PATH=/app/.venv/bin/:$PATH

CMD ["bash"]
