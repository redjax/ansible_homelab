# Homelab <!-- omit in toc -->

<!-- Repo image -->
<p align="center">
  <picture>
    <source media="(prefer-color-scheme: dark)" srcset="./docs/img/github-header-img.png">
    <img src="./docs/img/github-header-image.png" height="200">
  </picture>
</p>

<!-- Badges -->
<p align="center">
  <img alt="GitHub Created At" src="https://img.shields.io/github/created-at/redjax/ansible_homelab">
  <img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/redjax/ansible_homelab">
  <img alt="GitHub commit activity" src="https://img.shields.io/github/commit-activity/y/redjax/ansible_homelab">
  <img alt="GitHub repo size" src="https://img.shields.io/github/repo-size/redjax/ansible_homelab">
  <img alt="GitHub code size in bytes" src="https://img.shields.io/github/languages/code-size/redjax/ansible_homelab">
</p>

> [!WARNING]
> This project is undergoing a fairly significant refactor. The documentation will probably lag behind a bit. Until this message is removed, some of the commands and setup instructions may no longer work.

My Ansible monorepo, with collections, roles, and playbooks, [`mise`](https://mise.jdx.dev) for tools installation, [`go-task/task`](https://taskfile.dev/) for automations, and [`direnv`](https://direnv.net) for environment variables.

## Table of Contents <!-- omit in toc -->

- [Requirements](#requirements)
- [Setup](#setup)
  - [SSH setup](#ssh-setup)
- [Usage](#usage)
- [Project directories](#project-directories)
  - [Inventories](#inventories)
  - [Plays](#plays)
  - [Collections](#collections)
- [Using Ansible Vault](#using-ansible-vault)
  - [Vault Setup](#vault-setup)
    - [Password file](#password-file)
- [Devpod/Devcontainer](#devpoddevcontainer)
- [Links](#links)

## Requirements

[`mise`](https://mise.jdx.dev) is really the only requirement for this repository. The included [`.mise.toml`](./.mise.toml) handles installing all the other tools.

If you are not using `mise`, the requirements are:

- [`Python`](https://python.org)
- [`uv`](https://docs.astral.sh/uv) - `uv` is used to manage the [MkDocs site](./docs/)'s dependencies.
- [`ansible`]([https://](https://docs.ansible.com/projects/ansible/latest/index.html))
- [`direnv`](https://direnv.net)
- [`go-task/task`](https://taskfile.dev)

## Setup

If you are using `mise`, just run:

```shell
mise trust
mise install

direnv allow

task ansible-requirements
```

If you are not using `mise`, make sure you install all of the [requirements](#requirements). You can use a Python virtualenv to install Ansible, if you want:

```shell
direnv allow

python -m pip install -U virtualenv
python -m virtualenv .venv
./.venv/bin/activate
pip install -U ansible

task ansible-requirements
```

> [!NOTE]
> You can install Ansible's requirements manually with `ansible-galaxy install -r .config/ansible/requirements.yml`.


### SSH setup

**TODO**:

- [ ] Document generating SSH keypairs
- [ ] Document the `~/.ssh/config` file
- [ ] Document the `ansible_svc` SSH account
- [ ] Document the [`create-ansible-svc-user.yml`](./plays/maint/create-ansible-svc-user.yml) playbook

## Usage

**TODO**:

- [ ] Document using `ansible-playbook` to run plays in `./plays/`
- [ ] Document using `ansible-galaxy {collection,role} init` to create new collections/roles.
- [ ] Document using `ansible-galaxy build` to build collections.
- [ ] Document running [`nox`](https://nox.thea.codes/) sessions defined in `noxfile.py`
  - [ ] Document adding new sesions

## Project directories

### Inventories

The [`inventories/`](./inventories/) path is where server infrastructure can be configured. Use an inventory's `group_vars/all.yml` to set variables for the inventory group, then use `ansible-playbook -i inventories/<inventory_name>/inventory.yml ...`.

To create a new inventory, create a new directory and add inventory and vars files:

- `mkdir inventories/new_inventory/group_vars`
  - Create the inventory directory, "new_inventory/", and the `group_vars/` directory, where variables for the inventory group are set.
- `touch inventories/new_inventory/inventory.yml`
  - The inventory file where hosts are declared and grouped.
  - When setting a variable for an inventory, check the Ansible documentation to determine where to set and override variables: [Variable precedence: Where should I put a variable?](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_variables.html#variable-precedence-where-should-i-put-a-variable).
- `touch inventories/new_inventory/group_vars/all.yml`
  - Create the group variables file, where you can define variables that apply to the whole inventory.

Example inventory.yml

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

### Plays

Playbooks join collections and roles into repeatable steps/tasks that can be applied to an inventory.

For example, the [`plays/maint/update-system.yml`](./plays/maint/update-system.yml) playbook will run `apt` or `dnf` updates/upgrades, and reboot the remote host if required after an update. The playbook uses variables from the inventory's [`group_vars/all.yml`](./inventories/homelab/group_vars/all.example.yml) file, and pulls in the [`update_system`](./collections/my/homelab/roles/update_system/) role from the [`my.homelab` collection](./collections/my/homelab/).

### Collections

> Collections are a distribution format for Ansible content that can include playbooks, roles, modules, and plugins. You can install and use collections through a distribution server, such as Ansible Galaxy, or a Pulp 3 Galaxy server.
>
> [*Ansible docs: Using Ansible collections*](https://docs.ansible.com/ansible/latest/collections_guide/index.html)

Collections in [`./collections/my/`](./collections/my/) are built & installed using the [`requirements.yml](./requirements.yml) file. Any time a collection changes, it must be rebuilt.

## Using Ansible Vault

- [Ansible Vault documentation](https://docs.ansible.com/ansible/latest/vault_guide/index.html)

Encrypting secret variables with Ansible Vault allows for passing secrets like passwords to playbooks/roles. Your vault is encrypted with a [vault password](https://docs.ansible.com/ansible/latest/vault_guide/vault_managing_passwords.html#storing-and-accessing-vault-passwords), which can be read a number of ways. This project [stores the password in a file](https://docs.ansible.com/ansible/latest/vault_guide/vault_managing_passwords.html#storing-passwords-in-files).

### Vault Setup

#### Password file

This project is relatively small, and with only a single user (me). I've [opted to store my password in a file (option 2, 'configuring vault_password_file' in ansible.cfg)](https://www.golinuxcloud.com/ansible-vault-example-encrypt-string-playbook/#Running_Playbooks_with_Vaulted_Files).

Steps:

- Edit `ansible.cfg` and specify the `vault_password_file` in the `[defaults]` section:

```cfg
[defaults]
vault_password_file = /path/to/vault_password_file
```

- (Optional) You can also set your vault password as an environment variable, and set `vault_password_file` to a Bash script that echoes your Ansible vault password:

```shell
#!/bin/bash
#
# Assumes you have set an env variable $ANSIBLE_VAULT_PASS to a value matching your vault password
#

echo $ANSIBLE_VAULT_PASS

```

Each time you run your playbook, Ansible will unlock the vault by reading from the `vault_password_file`, or echoing the value from the environment (if you set the value to a Bash script).

## Devpod/Devcontainer

This repository includes a [`devcontainer.json`](./.devcontainer/devcontainer.json). This file is compatible with [VSCode Devcontainers](https://code.visualstudio.com/docs/devcontainers/create-dev-container) and [Devpod](https://devpod.sh). The devcontainer builds an environment from [the included Dockerfile](./.devcontainer/Dockerfile), then runs it in an isolated environment.

If you're using Devpod, you can setup the environment with the following steps:

- Add the Docker provider: `devpod provider add docker`
- Build/run the workspace: `devpod up . --id devpod-ansible`
  - To build the workspace & open in VSCode: `devpod up . --id devpod-ansible --ide vscode`

You can also open the repository in the Devpod GUI, if you've installed that.

## Links

- [DigitalOcean: How to use Ansible vault to protect sensitive data](https://www.digitalocean.com/community/tutorials/how-to-use-vault-to-protect-sensitive-ansible-data)
- [Linode: Using fail2ban to secure your server](https://www.linode.com/docs/guides/using-fail2ban-to-secure-your-server-a-tutorial/)
