#!/bin/bash

## Path where this script is
THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
## Path to root of Architecture repository from the script's path
REPO_ROOT=$(realpath -m "$THIS_DIR/../../")

echo "Repository root path: ${REPO_ROOT}"
echo ""

## Append bin dirs to PATH
export PATH="$PATH:/home/$USER/.local/bin:/usr/local/bin:/usr/bin:/bin"

## Set path to Ansible inventories
INVENTORIES_DIR="${REPO_ROOT}/inventories"
## Set path to plays
PLAYS_DIR="${REPO_ROOT}/plays"

## Set path to onboarding inventory.yml
ONBOARD_INVENTORY_FILE="$INVENTORIES_DIR/onboard/inventory.yml"
## SSet path to homelab inventory.yml
HOMELAB_INVENTORY_FILE="$INVENTORIES_DIR/homelab/inventory.yml"

## Set --limit arg
LIMIT=""

## Defaults
RUN_ONBOARDING="false"
DRY_RUN="false"

## Playbooks to run
PLAYS=(
    ${PLAYS_DIR}/installs/install-mosh.yml
    ${PLAYS_DIR}/installs/install-crontab.yml
    ${PLAYS_DIR}/security/firewall/install-and-configure-firewall.yml
    ${PLAYS_DIR}/security/fail2ban/install-configure-fail2ban.yml
    ${PLAYS_DIR}/config/setup-zram.yml
)

## Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --onboard)
      RUN_ONBOARDING="true"
      shift
      ;;
    --dry-run)
      DRY_RUN="true"
      shift
      ;;
    *)
      echo "[ERROR] Invalid argument: $1"
      exit 1
      ;;
  esac
done

## Test if uv is installed
if ! command -v uv &>/dev/null; then
  echo "[ERROR] uv is not installed."
  exit 1
fi

if [[ "$DRY_RUN" == "true" ]]; then
  echo "Dry run enabled"
fi

## Create base command
BASE_CMD=(uv run ansible-playbook)

## Do onboarding if --onboard is true
if [[ "$RUN_ONBOARDING" == "true" ]]; then
  ONBOARD_CMD=("${BASE_CMD[@]}")
  ONBOARD_CMD+=(-i "$ONBOARD_INVENTORY_FILE" --limit "$LIMIT" "${PLAYS_DIR}/onboard/run-onboarding.yml")

  echo ""
  
  if [[ "$DRY_RUN" == "true" ]]; then
    echo "[DRY RUN] Would run command:"
    echo "  ${ONBOARD_CMD[@]}"
  else
    echo "Running onboard command:"
    echo "  ${ONBOARD_CMD[@]}"
    echo ""

    "${ONBOARD_CMD[@]}"
  fi
fi

#################
# Ansible Plays #
#################

for play in "${PLAYS[@]}"; do
  ANSIBLE_CMD=("${BASE_CMD[@]}")

  ANSIBLE_CMD+=(-i "${HOMELAB_INVENTORY_FILE}")
  ANSIBLE_CMD+=(--limit "${LIMIT}")
  ANSIBLE_CMD+=("$play")

  if [[ "$DRY_RUN" == "true" ]]; then
    echo ""
    echo "[DRY RUN] Would run command:"
    echo "  ${ANSIBLE_CMD[@]}"

    echo "============================="
  else
    echo "Ansible command:"
    echo "  ${ANSIBLE_CMD[@]}"
    echo "============================="
    echo ""

    "${ANSIBLE_CMD[@]}"
  fi
done

echo ""
