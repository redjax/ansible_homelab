# Ansible Collections <!-- omit in toc -->

> Collections are a distribution format for Ansible content that can include playbooks, roles, modules, and plugins. You can install and use collections through a distribution server, such as Ansible Galaxy, or a Pulp 3 Galaxy server.
>
> [*Ansible Docs: Using Ansible Collections*](https://docs.ansible.com/ansible/latest/collections_guide/index.html)

Collections can group a collection of roles, plugins, and metadata into a single module. This makes it useful for group a set of tasks around a specific set of infrastructure. For example, a collection `my.homelab` might contain roles for quickly setting up common configurations and installed programs across all hosts defined in a `homelab/inventory.yml` Ansible inventory.

## Table of Contents <!-- omit in toc -->

- [Initialize a new collection](#initialize-a-new-collection)
- [Use Collections in Other Repos](#use-collections-in-other-repos)

## Initialize a new collection

Collections must exist within a "namespace," which just means a directory. This project stores collections in the [`collections/`](../collections/) path, under the [`my`](../collections/my/) namespace/directory.

Creating a new collection is as simple as creating a new directory, or `cd`-ing into an existing directory, and running the following command:

```shell
ansible-galaxy collection init <collection_name>
```

This will initialize a collection directory with some default directories and files, like `docs/`, `plugins/`, and `roles/`.

Adding roles to a collection makes them accessible to playbooks with the following notation:

```yaml
## Example playbook calling a collection's role
- name: "Call a role from a collection"
  hosts: all

  tasks:
    - name: "Call the my.homelab.setup role, include only tmux setup tasks"
      ansible.builtin.import_role:
        name: my.homelab.setup
        tasks_from: install-tmux.yml

```

## Use Collections in Other Repos

You can provide a git URL in your Ansible's `requirements.yml` to install collections from other repositories. For example, to install the [`my.homelab` collection from this repo](./my/homelab/), add this to `requirements.yml` in another repo:

```yaml
collections:
  - name: git+https://github.com/redjax/ansible_homelab.git#/collections/my/homelab,main

```

Then run the following command to install:

> [!TIP]
> Add `--upgrade` to the end of this command to update requirements you've already installed.

```yaml
ansible-galaxy collection install -r requirements.yml -p path/to/collections/dir
```
