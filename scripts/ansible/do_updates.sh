#!/bin/bash

THIS_DIR="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")" && pwd)"
REPO_ROOT="$(cd "${THIS_DIR}/../.." && pwd)"

INVENTORY_DIR="$REPO_ROOT/inventories"
PLAYBOOKS_DIR="$REPO_ROOT/plays"

ANSIBLE_INVENTORY="$INVENTORY_DIR/homelab/inventory.yml"
ANSIBLE_PLAYBOOK="$PLAYBOOKS_DIR/maint/update-reboot-system.yml"

ANSIBLE_LIMIT="autoReboot"

DRY_RUN="false"

echo "[DEBUG] Script dir: $THIS_DIR"
echo "[DEBUG] Repository root dir: $REPO_ROOT"

if ! command -v uv &>/dev/null; then
    echo "[error] uv is not installed."
    exit 1
fi

echo "[DEBUG] uv is installed"
echo "[DEBUG] Parsing arguments"

while [[ $# -gt 0 ]]; do
    case "$1" in
    --dry-run)
        DRY_RUN="true"
        shift
        ;;
    -l | --limit)
        if [[ -z "$2" ]]; then
            echo "[ERROR] --limit provided, but no limit string granted"
            exit 1
        fi

        ANSIBLE_LIMIT="$2"
        shift 2
        ;;
    *)
        echo "invalid argument: $1"
        exit 1
        ;;
    esac
done

echo "[DEBUG] Dry run enabled: $DRY_RUN"
echo "[DEBUG] Inventory dir: $INVENTORY_DIR"
echo "[DEBUG] Playbooks dir: $PLAYBOOKS_DIR"
echo "[DEBUG] Ansible inventory: $ANSIBLE_INVENTORY"
echo "[DEBUG] Ansible playbook: $ANSIBLE_PLAYBOOK"
echo "[DEBUG] Ansible limit: $ANSIBLE_LIMIT"

## Check inventory file exists
if [[ ! -f "$ANSIBLE_INVENTORY" ]]; then
    echo "[ERROR] Could not find Ansible inventory at path: ${ANSIBLE_INVENTORY}"
    exit 1
fi

## Check playbook file exists
if [[ ! -f "${ANSIBLE_PLAYBOOK}" ]]; then
    echo "[ERROR] Could not find Ansible playbook at path: ${ANSIBLE_PLAYBOOK}"
    exit 1
fi

cmd=(uv run ansible-playbook -i "$ANSIBLE_INVENTORY" --limit "$ANSIBLE_LIMIT" "$ANSIBLE_PLAYBOOK")

if [[ "$DRY_RUN" == "true" ]]; then
    echo ""
    echo "[DRY RUN] Would run update/reboot command:"
    echo "  ${cmd[*]}"
    echo ""

    exit 0
else
    echo ""
    echo "Running Ansible playbook to auto-update machines in the '${ANSIBLE_LIMIT}' group"
    echo ""
    echo "Command:"
    echo "${cmd[*]}"
    echo ""

    "${cmd[@]}"
    if [[ $? -ne 0 ]]; then
        echo ""
        echo "[error] failed to run auto updates."
        echo ""

        exit $?
    else
        echo ""
        echo "updated ansible machines via playbook"
        echo ""

        exit 0
    fi
fi
