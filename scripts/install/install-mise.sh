#!/usr/bin/env bash

set -uo pipefail

## Mise Installer Script
#  Installs the Mise CLI to /usr/local/bin/mise (requires sudo)
#  For documentation see: https://mise.jdx.dev/installing-mise.html

INSTALL_PATH="/usr/local/bin/mise"
RUN_URL="https://mise.run"

echo "Installing Mise CLI to ${INSTALL_PATH}"

## Check dependencies
for cmd in curl shasum tar; do
  if ! command -v $cmd >/dev/null 2>&1; then
    echo "Error: $cmd is required but not installed." >&2

    if [[ "$cmd" == "shasum" ]]; then
      echo "Install SHASUM on Fedora: dnf install perl-Digest-SHA"
    fi

    exit 1
  fi
done

## Run the installer with elevated privileges if necessary
if [ "$EUID" -ne 0 ]; then
  echo "Running installation with sudo"
  curl -fsSL "$RUN_URL" | sudo MISE_INSTALL_PATH="$INSTALL_PATH" sh
else
  curl -fsSL "$RUN_URL" | MISE_INSTALL_PATH="$INSTALL_PATH" sh
fi

## Check installation
if [ -x "$INSTALL_PATH" ]; then
  echo "Mise installed successfully."
  "$INSTALL_PATH" --version
else
  echo "Installation failed — binary not found at ${INSTALL_PATH}" >&2
  exit 1
fi
