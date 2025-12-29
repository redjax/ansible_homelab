# Homelab <!-- omit in toc -->

<!-- Repo image -->
<p align="center">
  <picture>
    <source media="(prefer-color-scheme: dark)" srcset="./docs/src/img/github-header-img.png">
    <img src="./docs/src/img/github-header-image.png" height="200">
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
  - [Direnv setup](#direnv-setup)
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

Now you're ready to [create an inventory](#inventories) and run some [playbooks](#plays).

### SSH setup

> [!NOTE]
> If you are using `direnv`, the [`.envrc` file](./.envrc) sets the `ANSIBLE_SSH_DIR` variable for you.

This repository uses a [`.ssh/` directory](./.ssh/) to define SSH sessions. This keeps Ansible-specific SSH sessions isolated from your `~/.ssh/config`, and your Ansible keys contained in this repository. You can tell Ansible to look in another directory for SSH configuration using the `ANSIBLE_SSH_DIR` environment variable.

On a new machine, if you are setting up fresh managed infrastructure and do not already have an SSH keypair, start by generating an `ansible_svc` key (you can use whatever name you want for the keys, I just use `ansible_svc`/`ansible_svc.pub`):

```shell
ssh-keygen -t ed25519 -b 4096 -f .ssh/ansible_svc -N ""
```

Copy this key to the host(s) you want to manage with Ansible. Then, copy `.ssh/example_config` to `.ssh/config` and edit with your host(s) you want to manage with Ansible.

> [!TIP]
> You can use the [`run-onboarding.yml` playbook](./plays/onboard/run-onboarding.yml) to automatically copy your `ansible_svc` SSH key to the remote during onboarding. This assumes the remote host has password connections enabled so Ansible can prompt you for the remote connection's password.
>
> The onboarding playbook requires a user with root or sudo privileges. If you provision a machine with just a `root` account, use the `root` user in your `.ssh/config` file and pass `-k` to your commands.
>
> Example (asssumes you have created an [onboarding inventory](./inventories/onboard/example.inventory.yml)):
> ```shell
> ansible-playbook -i inventories/onboard/inventory.yml [--limit <limit-name>] plays/onboard/run-onboarding.yml -k
> ```
>
> You can also tell Ansible to prompt you for sudo password when required by passing an uppercase `-K` along with `-k` (prompt for SSH connection password).

The onboarding playbook will create an `ansible_svc` user on the remote. You cannot use a password to authenticate as this user, you must use the `ansible_svc` SSH key. After running the onboarding playbook, you can run `ssh -i .ssh/ansible_svc ansible_svc@<your-hostname-or-ip>` to ensure connectivity.

To validate Ansible's SSH connection, run `ansible <hostname-or-inventory-group> -m ansible.builtin.ping`, or run the [`ping` playbook](./plays/ping.yml).

### Direnv setup

The [`.envrc` file](./.envrc) sets default environment variables to configure the repository. You can create a `.envrc.local` (copy the contents at the bottom of the `.envrc` file into the `.envrc.local` file) and override individual settings.

Whenever you make a change to either `.envrc` or `.envrc.local`, you will need to re-run `direnv allow`.

Whenever you `cd` into this repository after allowing the `.envrc` file, `direnv` will automatically source the file and set your environment variables, and when you leave the repository path it will unset them.

## Usage

- Run `task -l` to see predefined Ansible tasks.
- Run individual playbooks with `ansible-playbook [--limit <hostname-in-inventory>] plays/path/to/playbook-name.yml`
  - By default, the [`homelab` inventory](./inventories/homelab/example.inventory.yml) is used.
  - You can target a different inventory with `ansible-playbook -i inventories/inventoryName/inventory.yml`.
  - Instead of passing `-i path/to/inventory.yml`, you can also set the `ANSIBLE_INVENTORY` environment variable.
  - You can also set the value of `ANSIBLE_INVENTORY` in a [`.envrc.local` file](#direnv-setup) to override the default inventory.

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

> [!TIP]
> If you use an existing directory in [`inventories/`](./inventories/), you should be able to just copy the `example.inventory.yml` to `inventory.yml` and edit it.

Example inventory.yml

```yaml
---
## Define a cluster group, with 2 agents and 2 servers
all:
  hosts:
    ## Add localhost to allow running plays against this machine
    localhost:
      ansible_connection: local
      ansible_python_interpreter: "{{ ansible_playbook_python }}"
    host1:
      ansible_host: "192.168.1.15"
    host2:
      ansible_host: "192.168.1.16"
      ## Remote has SSH on a different port than 22
      ansible_ssh_port: 222
    host3:
      ansible_host: "192.168.1.60"
      ## Login as the root user on this machine
      ansible_user: root
    host4:
      ansible_host: "192.168.1.64"
      ## One of the roles can enable passwordless sudo
      setup_user_passwordless_sudo: true
      ## This host defines ports to allow through a UFW firewall
      ufw_tcp_allowed_ports: ["80", "443", "29281"]
    host5:
      ## This machine was configured before and can use an SSH key for connection.
      #  Tell Ansible where to find that key.
      ansible_ssh_private_key_file: "/home/username/.ssh/id_rsa"
  ## Variables set here apply to the hosts above across all inventory groups
  vars:
    ## Assumes the SSH user for setup is 'root', and that the playbook
    #  will disable SSH login as root
    ansible_user: "root"

## Create a group specifically for onboarding into Ansible management.
onboard:
  hosts:
    ## Re-declare hosts from above. Variables like ansible_host and ansible_user are inherited from the "all" group.
    host1:
    host2:
    host3:
    host4:

  ## Vars set here will only apply when ansible-playbook -i ... --limit onboard is used
  vars:

    ## NOTE: Both of these are set with direnv. They are only here as an example.

    ## Set private key to use for connections.
    ansible_ssh_private_key_file: ".ssh/ansible_svc"
    ## Set public key variable, which is used in the onboard play
    ansible_ssh_public_key_file: ".ssh/ansible_svc.pub"

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
