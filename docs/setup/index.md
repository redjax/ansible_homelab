# Ansible Control Host Setup

This page documents the process for setting this repository up on a new Ansible control host.

## Requirements

- Python
  - `nox` and Ansible both depend on Python.
  - (Optional) Use [pyenv](https://github.com/pyenv/pyenv) to install Python.
      - 📚 [My documentation on pyenv](https://redkb.readthedocs.io/en/latest/programming/python/pyenv.html)
- `virtualenv` Python package
    - Install with pip: `pip install --user virtualenv`
    - Install with [`pipx`](https://github.com/pypa/pipx): `pipx install virtualenv`

## Setup

- Create virtual environment with `virtualenv .venv`
- Activate environment
    - Linux: `. .venv/bin/activate`
    - Windows: `. .venv\Scripts\activate`
- Install requirements
    - `pip install -r requirements.yml`
- Install Ansible requirements
    - (with [`nox`](https://nox.thea.codes/)): Simply run [`nox`](https://nox.thea.codes/) from the command line with no arguments to run the build/install commands.
    - (with `ansible-galaxy`): `ansible-galaxy collection install -r requirements.yml`

### Docs setup

This project uses `nox` sessions to build, serve, and publish this `mkdocs` site. You can also do this manually:

- Create a virtualenv just for the docs site
    - `virtualenv .mkdocs-venv`
- Activate the `mkdocs` venv
    - Linux: `. .mkdocs-venv/bin/activate`
    - Windows: `. .mkdocs-venv\Scripts\activate`
- Install `mkdocs` requirements
    - `pip install -r docs/requirements.txt`

### SSH setup

**TODO**:

- [ ] Document generating SSH keypairs
- [ ] Document the `~/.ssh/config` file
- [ ] Document the `ansible_svc` SSH account
- [ ] Document the [`create-ansible-svc-user.yml`](./plays/maint/create-ansible-svc-user.yml) playbook
