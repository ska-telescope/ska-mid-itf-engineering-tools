FROM artefact.skao.int/ska-cicd-k8s-tools-build-deploy:0.9.0

ARG POETRY_VERSION=1.3.2
ARG DEBIAN_FRONTEND=noninteractive
ARG TZ=Etc/UTC

RUN apt-get update && \
    apt-get install gnupg2 gawk yamllint vim telnet expect sshpass inetutils-ping netcat -y

ENV PATH=/root/.local/bin:$PATH

RUN python3 -m pip install --user pipx && \
    python3 -m pipx ensurepath && \
    pipx install poetry==$POETRY_VERSION && \
    pipx install build && \
    poetry config virtualenvs.in-project true && \
    pip install virtualenv

WORKDIR /app

COPY . /app

RUN poetry install

USER root

CMD ["bash"]
