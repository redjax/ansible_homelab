# Repository Directories

!!! tip
    Use the left-hand navigation to read more about the directories in this repository and how they come together to form Ansible automations.

## Overview

- [Collections](./collections)
    - These are like packages for Ansible.
    - Group multiple roles into a collection, then you can import a full collection using a `requirements.yml` file.
- [Inventories](./inventories)
    - Define Ansible-managed hosts.
    - Each inventory has a `group_vars/` directory with an `all.yml` file defining common/shared variables for that inventory.
- [Playbooks](./plays)
    - Call collections/roles to run actions on remote hosts with Ansible.
- [Roles](./roles)
    - **WARNING**: The repository currently has roles grouped under collections, instead of in the `roles/` directory. I will fix that in a future commit.
    - The "business logic" for Ansible collections/playbooks.
    - Each role is responsible for a specific domain, i.e. the [`docker]
