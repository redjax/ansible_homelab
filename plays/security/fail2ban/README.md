# Fail2Ban Playbooks

Install & configure [`fail2ban`](github.com/fail2ban/fail2ban). The role sets up fail2ban's default configurations (configurable by variable), and also supports adding custom jails from a local Ansible template file.

## Custom fail2ban jails

Place fail2ban jail templates (`.j2` files) in this directory. In a playbook, i.e. `copy-custom-jails.yml`, use the template below to describe where Ansible should render the template on the remote server; note that the jails are defined in a directory at the same path as the playbook.

Jail paths are hardcoded in the role to begin with `/etc/fail2ban/jail.d/`, so any value you use for `dest` will end up appended to that path.

```yaml
---
- name: "Add extra fail2ban jails using the homelab.fail2ban role"
  hosts: all

  vars:
    custom_jails:
      [{ "template": "custom_jails/example.local.j2", "dest": "example.local" }]

  tasks:
    - name: "Copy jails"
      ansible.builtin.import_role:
        name: my.homelab.security.fail2ban
        tasks_from: add-custom-jail.yml

```

Note that if you nest templates on the remote, i.e. `/etc/fail2ban/jail.d/ssh/sshd.local`, the middle directory (`.../ssh/...`) must already exist on the remote.
