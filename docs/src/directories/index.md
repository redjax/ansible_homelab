# Repository Directories

!!! tip
    Use the left-hand navigation to read more about the directories in this repository and how they come together to form Ansible automations.

## Overview

- [Collections](./collections)
    - These are like packages for Ansible.
    - Group multiple roles into a collection, then you can import a full collection using a `requirements.yml` file.
    - Most of my roles are in the [`my` collection](https://github.com/redjax/tree/main/ansible_collections/my).
- [Inventories](./inventories)
    - Define Ansible-managed hosts.
    - Each inventory has a `group_vars/` directory with an `all.yml` file defining common/shared variables for that inventory.
- [Playbooks](./plays)
    - Call collections/roles to run actions on remote hosts with Ansible.
