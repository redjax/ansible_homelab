# Plays

Playbooks join collections and roles into repeatable steps/tasks that can be applied to an inventory. I store my plays in the [`plays/` directory](https://github.com/redjax/Ansible/tree/main/plays).

For example, the [`plays/maint/update-system.yml`](https://github.com/redjax/Ansible/blob/main/plays/maint/update-system.yml) playbook will run `apt` or `dnf` updates/upgrades, and reboot the remote host if required after an update. The playbook uses variables from the inventory's [`group_vars/all.yml`](https://github.com/redjax/Ansible/blob/main/inventories/homelab/group_vars/example.all.yml) file, and pulls in the [`update_system`](./collections/my/homelab/roles/update_system/) role from the [`my.homelab` collection](https://github.com/redjax/Ansible/tree/main/collections/my/homelab/roles/update_system).
