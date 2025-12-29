# Ansible Control Host Setup

This page documents the process for setting this repository up on a new Ansible control host.

## Requirements

[`mise`](https://mise.jdx.dev) is really the only requirement for this repository. The included [`.mise.toml`](./.mise.toml) handles installing all the other tools.

If you are not using `mise`, the requirements are:

- [`Python`](https://python.org)
- [`uv`](https://docs.astral.sh/uv) - `uv` is used to manage the [MkDocs site](./docs/)'s dependencies.
- [`ansible`]([https://](https://docs.ansible.com/projects/ansible/latest/index.html))
- [`direnv`](https://direnv.net)
- [`go-task/task`](https://taskfile.dev)

## Initial Clone Setup

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

!!! info
    You can install Ansible's requirements manually with `ansible-galaxy install -r .config/ansible/requirements.yml`.

## SSH setup

!!! note
    If you are using `direnv`, the [`.envrc` file](./.envrc) sets the `ANSIBLE_SSH_DIR` variable for you.

This repository uses a [`.ssh/` directory](./.ssh/) to define SSH sessions. This keeps Ansible-specific SSH sessions isolated from your `~/.ssh/config`, and your Ansible keys contained in this repository. You can tell Ansible to look in another directory for SSH configuration using the `ANSIBLE_SSH_DIR` environment variable.

On a new machine, if you are setting up fresh managed infrastructure and do not already have an SSH keypair, start by generating an `ansible_svc` key (you can use whatever name you want for the keys, I just use `ansible_svc`/`ansible_svc.pub`):

```shell
ssh-keygen -t ed25519 -b 4096 -f .ssh/ansible_svc -N ""
```

Copy this key to the host(s) you want to manage with Ansible. Then, copy `.ssh/example_config` to `.ssh/config` and edit with your host(s) you want to manage with Ansible.

!!! tip
    You can use the [`run-onboarding.yml` playbook](./plays/onboard/run-onboarding.yml) to automatically copy your `ansible_svc` SSH key to the remote during onboarding. This assumes the remote host has password connections enabled so Ansible can prompt you for the remote connection's password.

    The onboarding playbook requires a user with root or sudo privileges. If you provision a machine with just a `root` account, use the `root` user in your `.ssh/config` file and pass `-k` to your commands.
    
    Example (assumes you have created an [onboarding inventory](./inventories/onboard/example.inventory.yml)):

    ```shell
    ansible-playbook \
        -i inventories/onboard/inventory.yml \
        [--limit <limit-name>] \
        plays/onboard/run-onboarding.yml \
        -k
    ```

    You can also tell Ansible to prompt you for sudo password when required by passing an uppercase `-K` along with `-k` (prompt for SSH connection password).

The onboarding playbook will create an `ansible_svc` user on the remote. You cannot use a password to authenticate as this user, you must use the `ansible_svc` SSH key. After running the onboarding playbook, you can run `ssh -i .ssh/ansible_svc ansible_svc@<your-hostname-or-ip>` to ensure connectivity.

To validate Ansible's SSH connection, run `ansible <hostname-or-inventory-group> -m ansible.builtin.ping`, or run the [`ping` playbook](./plays/ping.yml).

## Direnv setup

The [`.envrc` file](./.envrc) sets default environment variables to configure the repository. You can create a `.envrc.local` (copy the contents at the bottom of the `.envrc` file into the `.envrc.local` file) and override individual settings.

Whenever you make a change to either `.envrc` or `.envrc.local`, you will need to re-run `direnv allow`.

Whenever you `cd` into this repository after allowing the `.envrc` file, `direnv` will automatically source the file and set your environment variables, and when you leave the repository path it will unset them.

## VSCode Setup

If you're editing in VSCode, you need to tell Code where to find your `python`, `ansible`, and `ansible-config` executables. If you are using `mise`, you can copy the [`.vscode/example.settings.json` file](.vscode/example.settings.json) to `.vscode/settings.json` and use `mise`'s shim paths for the executables.

Links to the binaries for `mise`-managed tools are in `~/.local/share/mise/shims`, but VSCode doesn't expand `~`, `$HOME`, or `${env:HOME}`/`${userHome}` vars in `settings.json`. That's why you need to create your own `settings.json`, to paste the path to your `mise/shims/` directory:

```json
{
    // ---- Python (used by language server, linting, etc.) ----
    "python.defaultInterpreterPath": "/home/YOUR-USERNAME/.local/share/mise/shims/python",
    // ---- Ansible extension (actual executables) ----
    "ansible.ansible.path": "/home/YOUR-USERNAME/.local/share/mise/shims/ansible",
    "ansible.ansibleConfig.path": "/home/YOUR-USERNAME/.local/share/mise/shims/ansible-config",
    "ansible.python.interpreterPath": "/home/YOUR-USERNAME/.local/share/mise/shims/python",
    // ---- Project defaults ----
    "ansible.inventory": "inventories/homelab/inventory.yml",
    "ansible.playbookDir": "plays",
    "ansible.useFullyQualifiedCollectionNames": true
}
```

## Docs dir setup

If using `mise` and `go-task/task`, run the following `task` command:

```shell
task mkdocs-setup
```

This will build the `docs/.venv` virtual environment and install the MkDocs requirements.

If not using `mise`, change directories into `docs/` and run:

```shell
python -m virtualenv .venv

# Linux
. .venv/bin/activate

# Windows
. .venv\\Scripts\\activate

pip install -r requirements.txt
```

Now you can run `task mkdocs-serve` or `mkdocs serve -f mkdocs.yml --live-reload -a 127.0.0.1:8000` to start a local development server. To load your docs from other machines on your network, change `-a 127.0.0.1:8000` to `0.0.0.0:8000`.
