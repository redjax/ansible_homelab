FROM debian:bookworm-slim AS base

ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="/home/dev/.local/bin:${PATH}"

FROM base AS system

RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    ca-certificates \
    curl \
    git \
    openssh-client \
    python3 \
    python3-venv \
    python3-pip \
    sudo \
    && rm -rf /var/lib/apt/lists/*

FROM system AS user

## Create non-root user
RUN useradd -m -s /bin/bash coder \
    && echo "coder ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/coder

USER coder
WORKDIR /workspace

FROM user AS uv

## Install uv
RUN curl -Ls https://astral.sh/uv/install.sh | bash

FROM uv AS tooling

RUN uv sync --dev --all-extras

FROM tooling AS runtime

USER coder
WORKDIR /workspace

CMD ["bash"]
