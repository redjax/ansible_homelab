# Inventories

The [`inventories/`](https://github.com/redjax/Ansible/tree/main/inventories) path is where server infrastructure can be configured. Use an inventory's `group_vars/all.yml` to set variables for the inventory group, then use `ansible-playbook -i inventories/<inventory_name>/inventory.yml ...`.

To create a new inventory, create a new directory and add inventory and vars files:

- `mkdir inventories/new_inventory/group_vars`
  - Create the inventory directory, "new_inventory/", and the `group_vars/` directory, where variables for the inventory group are set.
- `touch inventories/new_inventory/inventory.yml`
  - The inventory file where hosts are declared and grouped.
  - When setting a variable for an inventory, check the Ansible documentation to determine where to set and override variables: [Variable precedence: Where should I put a variable?](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_variables.html#variable-precedence-where-should-i-put-a-variable).
- `touch inventories/new_inventory/group_vars/all.yml`
  - Create the group variables file, where you can define variables that apply to the whole inventory.

## Example inventory.yml

```yaml
---
## Define a cluster group, with 2 agents and 2 servers
all:
  hosts:
    cl-ag1:
      ansible_host: "192.168.1.61"
    cl-ag2:
      ansible_host: "192.168.1.62"
    cl-srv1:
      ansible_host: "192.168.1.60"
    cl-srv2:
      ansible_host: "192.168.1.64"
  ## Variables set here apply to the hosts above across all inventory groups
  vars:
    ## Set remote user for all hosts
    ansible_user: "ubuntu"

## Create a group specifically for onboarding into Ansible management.
onboard:
  hosts:
    ## Re-declare hosts from above. Variables like ansible_host and ansible_user are inherited from the "all" group.
    rpi-cl-ag1:
    rpi-cl-ag2:
    rpi-cl-srv1:
    rpi-cl-srv2:
  ## Vars set here will only apply when ansible-playbook -i ... --limit onboard is used
  vars:
    ## Set private key to use for connections.
    ansible_ssh_private_key_file: "~/.ssh/ansible_id_rsa"
    ## Set public key variable, which is used in the onboard play
    ansible_ssh_public_key_file: "~/.ssh/ansible_id_rsa.pub"

```