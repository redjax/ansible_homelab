# Usage

## Overview

After creating an inventory, you can install the `my` collection and use it in Playbooks to run automations against the infrastructure defined in your inventory.

!!! tip "Relationship between collections, roles, playbooks, and inventories"

    - Roles are defined in a collection (or separately in a `roles/` path, but this repository uses collections to encapsulate roles).
    - Playbooks import roles/role tasks from a collection using dot notation (i.e. `my.homelab.debug` with optional scoping to the `debug-cpu.yml` task)
    - Inventories define your infrastructure and pass variables to playbooks to alter the way a role runs.
