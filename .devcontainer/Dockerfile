ARG UV_VER=0.9.17
ARG PYTHON_VER=3.14

FROM python:${PYTHON_VER}-slim AS base
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    ca-certificates \
    curl \
    git \
    sudo \
    openssh-client \
    iputils-ping \
    build-essential \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

FROM base AS user

RUN useradd -m -s /bin/bash coder \
    && echo "coder ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/coder

USER coder
WORKDIR /workspace

ENV PATH="/home/coder/.local/bin:${PATH}"

## Install uv from astral-sh/uv container
FROM ghcr.io/astral-sh/uv:${UV_VER} AS uv
FROM user AS stage

WORKDIR /workspace
COPY pyproject.toml uv.lock README.md ./

FROM user AS build

WORKDIR /workspace

## Copy uv binaries from uv stage
COPY --from=uv /uv /usr/bin/uv

## Copy project files
COPY --from=stage /workspace /workspace

RUN uv --version

FROM user AS runtime
WORKDIR /workspace

## Copy uv binaries
COPY --from=uv /uv /usr/bin/uv

CMD ["bash"]
