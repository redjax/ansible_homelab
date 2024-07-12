# Homelab

This repository contains my Ansible code (collections, roles, playbooks, inventories, etc) for setting up/maintaining my homelab. The project is driven by [`nox`](https://nox.thea.codes/)-based session automation.

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

**Example inventory.yml**

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

The [`noxfile.py`](./noxfile.py) included in this repository has some pre-defined sessions for automating repetitive tasks like building collections. The `CUSTOM_COLLECTIONS` list in `noxfile.py` must be updated if/when new collections are added to the `my` namespace.

When [`nox`](https://nox.thea.codes/) is called with no parameters, the following sessions are executed:

- `lint`: The `noxfile` is linted with `ruff`.
- `build-my-collections`: The script loops over all collections in [`./collections/my/](./collections/my/) and builds each one with `ansible-galaxy collection build`.
  - The built distribution file is outputted to `./build/`, a directory which is ignored in [`.gitignore`](./.gitignore) and will be created if it does not already exist.
- `install-ansible-requirements`: Installs collections and roles defined in [`./requirements.yml`](./requirements.yml).

## Nox automation

The [`noxfile.py`](./noxfile.py) file defines [`nox`](https://nox.thea.codes/) sessions to automate tasks like building & installing collections, and executing some playbooks. Note that for the playbook sessions, your host must already be configured with an SSH connection to the remote host (see [SSH setup](#ssh-setup) for instructions).

### Add new collections to build automation

When adding a new Ansible collection, if you want [`nox`](https://nox.thea.codes/) to handle building & installing the collection when you make changes, you must create an instance of `CustomAnsibleCollection()` and add it to the `CUSTOM_COLLECTIONS` list. In the example below, we will add a new collection named "my.base_setup" to the automated build list:

```python
## noxfile.py

# other nox code
...


## Note: do not make changes to this class, just take note of the parameters
#  for when you create an instance of this object in CUSTOM_COLLECTIONS
@dataclass
class CustomAnsibleCollection:
    """Define a custom Ansible collection for Nox sessions.
    
    Params:
        name (str): The simple name of the role, mainly used for logging messages.
        fqcn (str): The fully-qualified collection name, i.e. `my.collection`
        path (Path): The local file path to the Ansible collection.
    
    """

    name: str = field(default=None)
    fqcn: str = field(default=None)
    path: Path | None = field(default=None)
    
    @property
    def path_exists(self) -> bool:
        if self.path:
            return self.path.exists()
        else:
            return False
    
    def __post_init__(self):
        if self.path:
            _path: Path = Path(f"{self.path}")
            
            self.path = _path
            
        _log = logging.getLogger("nox.CustomAnsibleCollection")
        self.logger = _log

CUSTOM_COLLECTIONS: t.List[CustomAnsibleCollection] = [
    ## Existing collection named "my.homelab"
    CustomAnsibleCollection(name="homelab", fqcn="my.homelab", path=Path(f"{MY_COLLECTIONS_PATH}/homelab")),
    ## New collection, we will initialize it on the fly. You could also create a variable for the class and use
    #  CUSTOM_COLLECTIONS.append(custom_collection)
    CustomAnsibleCollection(name="base_setup", fcqn="my.base_setup", path=Path(f"{MY_COLLECTIONS_PATH}/base_setup"))
]

```

### Sessions

**TODO**:

- [ ] Document existing sessions & usage
- [ ] Document adding new sessions
