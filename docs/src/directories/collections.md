# Collections

## Overview

Collections are a distribution format for Ansible content that can include playbooks, roles, modules, and plugins. You can install and use collections through a distribution server, such as Ansible Galaxy, or a Pulp 3 Galaxy server.

Collections in [`./ansible_collections/my/`](https://github.com/redjax/Ansible/tree/main/ansible_collections/my) are built & installed using the [`requirements.yml`](https://github.com/redjax/Ansible/blob/main/requirements.yml) file. Any time a collection changes, it must be rebuilt.
