# Homelab

This repository contains my Ansible code (collections, roles, playbooks, inventories, etc) for setting up/maintaining my homelab.

TODO:
    
- [ ] Document directories
    - [ ] `collections/`
    - [ ] `inventories/`
    - [ ] `plays/`
- [ ] Document project setup
    - [ ] `virtualenv .venv && . .venv/bin/activate`
    - [ ] `pip install -r requirements.txt`
- [ ] Document using `nox` to run playbook sessions
    - [ ] `nox -s <session_name>`
    - [ ] Document adding new sessions to `noxfile.py`

## Setup

- Create virtual environment with `virtualenv .venv`
- Activate environment
  - Linux: `. .venv/bin/activate`
  - Windows: `. .venv\Scripts\activate`
- Install requirements
  - `pip install -r requirements.yml`
- Install Ansible requirements
  - (with `nox`): `nox -s install-collection-requirements`
  - (with `ansible-galaxy`): `ansible-galaxy collection install -r requirements.yml`

## Project directories

**TODO**

### Inventories

**TODO**

### Plays

**TODO**

### Collections

**TODO**
