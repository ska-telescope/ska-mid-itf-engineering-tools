ARG OCI_IMAGE_VERSION=artefact.skao.int/ska-cicd-k8s-tools-build-deploy:0.11.0
FROM $OCI_IMAGE_VERSION as base

ARG POETRY_VERSION=1.3.2
ARG DEBIAN_FRONTEND=noninteractive
ARG TZ=Etc/UTC



#ENV PATH=/root/.local/bin:$PATH

#Change from root user
ENV USER=newuser
#RUN adduser --system --home /home/${USER} --shell /usr/bin --gid 0 ${USER}
ENV HOME /home/${USER}
RUN useradd --create-home --home-dir ${HOME} ${USER}
RUN usermod -u 1000 -g 1000 ${USER}
ENV PATH=/home/${USER}/.local/bin:$PATH

#RUN adduser -D ${USER}
USER ${USER}
WORKDIR /home/${USER}
ENV PATH=/usr/bin:$PATH
#RUN python3 -m pip install pipx
#RUN python3 -m pipx ensurepath
#RUN  python3 -m pipx install poetry==$POETRY_VERSION
RUN python3 -m pip install poetry==$POETRY_VERSION
RUN python3 -m pip install build
RUN poetry config virtualenvs.in-project true
RUN python3 -mpip install virtualenv

WORKDIR /app

FROM base
COPY . /app

#RUN poetry install

USER root

ENV PATH=/app/.venv/bin/:$PATH

CMD ["bash"]
