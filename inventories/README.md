# Inventories

Ansible inventories describe the hosts to be managed by Ansible. There are multiple ways to describe an Ansible inventory (see [Ansible docs: Building an Inventory](https://docs.ansible.com/ansible/latest/getting_started/get_started_inventory.html) for examples of a `.ini` and `.yml` inventory).

This project uses the `.yml` format for inventories. The project has 2 "main" inventories, [`homelab`](./homelab/) and [`onboard`](./onboard/). The `onboard` inventory describes machines that need to be set up/"enrolled" into Ansible management. Add new machines here and run the `plays/onboard/create-ansible-svc-user.yml` playbook to create the Ansible service user (default: `ansible_svc`) and authorize SSH key(s) for the service user. Once a machine has been enrolled with the onboarding process, add it to the `homelab` inventory to manage it alongside other machines.

## Creating a new inventory

- Create a directory in the [`inventories/`](./) directory
  - As an example, if you're building a Raspberry Pi cluster running Kubernetes to be managed by Ansible, you might create a directory named `rpi_k8s_cluster/`
- Within the `inventories/<new_inventory_name>/` path, create the following:
  - `inventory.yml`: The Ansible inventory file where you will define your hosts
  - `group_vars/`: A directory where you can define variables that will apply to hosts in the `inventory.yml` file
  - `group_vars/all.yml`: The file where Ansible variables can be declared

### Example inventory.yml

```yaml
---
all:
  ## Put all of the hosts you want to manage in all:
  #  Note that you can add variables per-host or per-group
  hosts:
    hostname1:
      ## Address/FQDN to remote ehost
      ansible_host: "192.168.1.xxx"
    hostname2:
      ansible_host: "192.168.1.xxx"
      ## Define the user Ansible should use for connections to the remote
      ansible_user: "remoteLinuxUsername"
    hostname3:
      ansible_host: "192.168.1.xxx"
      ## Set a variable that will only apply to hostname3
      python_version: "3.12.4"

## You can create extra inventory groups following a similar syntax above.
#  When running playbooks, use --limit <group_name> to run plays only against
#    hosts in the specified group
debian:
  hosts:
    ## Values defined in the all: inventory will be used
    hostname1:
    hostname2:
      ## Set/override vars only when --limit debian is used
      vars:
        ex_var: true
  ## Set/override variables for all hosts defined in this group
  vars:
    ex_var2: false

```

### Example group_vars/all.yml

Variables declared here are assigned to any host in the `inventory.yml` file, whenever an Ansible command specifies that inventory (i.e. `ansible-playbook -i inventories/<inventory_name>/inventory.yml ...`).

```yaml
## Set path to Python executable on remote host(s)
ansible_python_interpreter: "/usr/bin/python3"

## Give the Ansible service account created with create-ansible-svc-user.yml a name
ansible_svc_user: "ansible_svc"

## Define a list of packages to install on all hosts. Reference {{ common_debian_packages }} in a role or playbook task
common_debian_packages: ["curl", "wget", "git", "neovim", "zip", "unzip"]

```
