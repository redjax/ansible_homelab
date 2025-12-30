# Usage

## Overview

After creating an inventory, you can install the `my` collection and use it in Playbooks to run automations against the infrastructure defined in your inventory.

!!! tip "Relationship between collections, roles, playbooks, and inventories"

    - Roles are defined in a collection (or separately in a `roles/` path, but this repository uses collections to encapsulate roles).
    - Playbooks import roles/role tasks from a collection using dot notation (i.e. `my.homelab.debug` with optional scoping to the `debug-cpu.yml` task)
    - Inventories define your infrastructure and pass variables to playbooks to alter the way a role runs.

Read more in-depth documentation on each of the [tools used in this repository](./tools/).

## Running playbooks

After finishing the [setup steps](../setup/), you can run [playbooks](https://github.com/redjax/Ansible/tree/main/plays) using the following syntax:

```shell title="Ansible playbook syntax" linenums="1"
ansible-playbook [-i <inventory-name>] plays/path/to/playbook.yml
```

The `[-i <inventory-name>]` is optional; if you do not specify an inventory, the default [`inventories/homelab/inventory.yml`](https://github.com/redjax/Ansible/tree/main/inventories/homelab/example.inventory.yml). The `ANSIBLE_INVENTORY` environment variable defined in the [direnv `.envrc`](https://github.com/redjax/Ansible/tree/main/.envrc) also sets the default inventory. You can [override it with a `.envrc.local` file](tools/direnv.md#local-envrc-file).

Finally, if you want to override the environment variable, you can use the `-i` arg for the `ansible-playbook` command. For example, to use an inventory defined in `inventories/example/inventory.yml`:

```shell title="Ansible playbook inventory override"
ansible-playbook -i inventories/example/inventory.yml plays/path/to/playbook-name.yml
```
