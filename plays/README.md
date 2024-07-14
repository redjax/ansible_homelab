# Ansible Playbooks

Playbooks bring together roles defined in [collections/](../collections/) or [roles/](../roles/) to build a set of instructions for Ansible. Running `ansible-playbook -i <path/to/inventory.yml> --limit <inventory-group-or-hostname <path/to/playbook.yml>` to call a playbook applies variables defined at the inventory and playbook level (in the `vars:` section), then runs tasks defined in the role(s) called by the playbook.

## Calling a role defined in a collection

To call a role that's been defined in a collection, use the `ansible.builtin.import_role:` syntax:

```yaml
## example playbook
---
- name: "Run a role defined in a collection"
  hosts: all

  vars:
    ## Vars define here will override defaults and group_vars
    var1: "val1"

  tasks:
    ## Import all tasks defined in a role called "example_role" in the my.homelab collection
    - name: "Include homelab collection's example_role role"
      ansible.builtin.import_role:
        name: my.homelab.example_role

```

You can also call specific tasks within a role, instead of running all tasks in the role, using `tasks_from:`

```yaml
## example playbook, call a single task from a role
- name: "Run a single task from a role defined in a collection"
  hosts: all

  tasks:
    - name: "Include a single task from the example role in the homelab collection"
      ansible.builtin.import_role:
        name: my.homelab.example_role
        ## Call a specific .yml file from the role's tasks/ directory
        tasks_from: example-tasks.yml

```
