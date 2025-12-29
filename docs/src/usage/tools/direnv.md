# Direnv

## Overview

[Direnv](https://direnv.net) is a tool that lets you source environment variables each time you enter a path with a `.envrc` file, and unloads them when you leave that path.

This repository includes a [`.envrc`](https://github.com/redjax/Ansible/.envrc), which adds Ansible configurations for the repository to the environment.

For example, when entering the root of the repository, the following environment variables will be set to tell Ansible where to find your inventory, collections, etc (note, this is just a snippet from the main `.envrc`):

```env title="Root .envrc" linenums="1"
## Ansible cache
ANSIBLE_LOCAL_TMP="${REPO_ROOT}/.ansible"

## Ensure Ansible dirs exist
mkdir -p "${ANSIBLE_LOCAL_TMP}/collections" "${ANSIBLE_LOCAL_TMP}/tmp"

## Override ansible.cfg values
export ANSIBLE_ROLES_PATH="${REPO_ROOT}/roles"
export ANSIBLE_INVENTORY="${REPO_ROOT}/inventories/homelab/inventory.yml"
export ANSIBLE_COLLECTIONS_PATHS="${REPO_ROOT}/ansible_collections:${ANSIBLE_LOCAL_TMP}/collections"
export ANSIBLE_LOCAL_TMP="${ANSIBLE_LOCAL_TMP}/tmp"
```

When you run an `ansible-playbook` command with no args, it will look for the inventory file at `inventories/homelab/inventory.yml` (unless you override it), and looks in `ansible_collections` for local collections. When `ansible-galaxy` installs collections, it will install them to `.ansible/collections`.

### Local .envrc file

You can set machine-specific vars or override defaults in `.envrc` by creating a `.envrc.local` file. This file is ignored by the repository's `.gitignore` file, so you can put whatever you want in it safely, git will not track changes to the local `.envrc`.

For example, to set a different inventory as the default, create a `.envrc.local` with:

```env title="Direnv .envrc.local" linenums="1"
## Set a different inventory as the default on this machine only
export ANSIBLE_INVENTORY="${REPO_ROOT}/inventories/anotherInventory/inventory.yml"
```
