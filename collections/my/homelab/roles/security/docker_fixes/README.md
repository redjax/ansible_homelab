# docker_fixes

Tasks to fix Docker issues, i.e. security vulnerabilities.

## Example Playbook

```yaml
---
- name: "Remediate Docker + UFW vulnerability"
  hosts: all

  tasks:
    - name: "Gather facts"
      ansible.builtin.import_role:
        name: my.homelab.facts

    - name: "Fix Docker UFW vulnerability"
      ansible.builtin.import_role:
        name: my.homelab.security.docker_fixes
        tasks_from: fix_ufw_vuln.yml
```


## Tasks

### fix_ufw_vuln.yml

Fixes the [Docker + UFW vulnerability](https://github.com/chaifeng/ufw-docker). Checks for the presence of a line, `DOCKER_OPTS=--iptables="false"`, in the file `/etc/default/docker`, appends the line if it does not exist, and restarts the `docker` daemon, if the file was modified.
