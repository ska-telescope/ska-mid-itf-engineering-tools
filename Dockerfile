ARG OCI_IMAGE_VERSION
FROM $OCI_IMAGE_VERSION as base

ARG POETRY_VERSION=1.3.2
ARG DEBIAN_FRONTEND=noninteractive
ARG TZ=Etc/UTC

ENV USER=newuser
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

WORKDIR /app

FROM base
COPY . /app

USER root

ENV PATH=/app/.venv/bin/:$PATH

CMD ["bash"]
