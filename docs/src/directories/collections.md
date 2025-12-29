# Collections

> Collections are a distribution format for Ansible content that can include playbooks, roles, modules, and plugins. You can install and use collections through a distribution server, such as Ansible Galaxy, or a Pulp 3 Galaxy server.
>
> [*Ansible docs: Using Ansible collections*](https://docs.ansible.com/ansible/latest/collections_guide/index.html)

Collections in [`./ansible_collections/my/`](https://github.com/redjax/ansible_homelab/tree/main/ansible_collections/my) are built & installed using the [`requirements.yml`](https://github.com/redjax/ansible_homelab/blob/main/requirements.yml) file. Any time a collection changes, it must be rebuilt.

The [`noxfile.py`]([./noxfile.py](https://github.com/redjax/Ansible/blob/main/noxfile.py)) included in this repository has some pre-defined sessions for automating repetitive tasks like building collections. The `CUSTOM_COLLECTIONS` list in `noxfile.py` must be updated if/when new collections are added to the `my` namespace.

When [`nox`](https://nox.thea.codes/) is called with no parameters, the following sessions are executed:

- `lint`: The `noxfile` is linted with `ruff`.
- `build-my-collections`: The script loops over all collections in [`./ansible_collections/my/](https://github.com/redjax/ansible_homelab/tree/main/ansible_collections/my) and builds each one with `ansible-galaxy collection build`.
  - The built distribution file is outputted to `./build/`, a directory which is ignored in [`.gitignore`](https://github.com/redjax/ansible_homelab/blob/main/.gitignore) and will be created if it does not already exist.
- `install-ansible-requirements`: Installs collections and roles defined in [`./requirements.yml`](https://github.com/redjax/ansible_homelab/blob/main/requirements.yml).