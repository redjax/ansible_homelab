my.homelab.fail2ban
=========

Install & configure fail2ban on remote servers. Copies the default `/etc/fail2ban/jail.conf` and `/etc/fail2ban/fail2ban.conf` before any modifications are made. Copies templated `fail2ban.local` and `jail.local` files.

**TODO**

- [ ] Add support for custom jails using the `jail.d/` directory on the remote.
    - [ ] Allow user to pass jails via playbook

Requirements
------------



Role Variables
--------------

```
## fail2ban.local
fail2ban_default_loglevel: INFO
fail2ban_default_logtarget: /var/log/fail2ban.log
fail2ban_default_syslogsocket: auto
fail2ban_default_socket: /var/run/fail2ban/fail2ban.sock
fail2ban_default_pidfile: /var/run/fail2ban/fail2ban.pid
fail2ban_default_dbmaxmatches: 10
fail2ban_default_dbpurgeage: 1d
fail2ban_default_dbfile: /var/lib/fail2ban/fail2ban.sqlite3
fail2ban_default_allowipv6: auto
fail2ban_default_stacksize: 0

## jail.local
jail_default_bantime_increment: true
jail_default_bantime_rndtime:
jail_default_bantime_maxtime:
jail_default_bantime_factor: 1
jail_default_local_bantime_formula: ban.Time * (1<<(ban.Count if ban.Count<20 else 20)) * banFactor
jail_default_bantime_multipliers: 1 5 30 60 300 720 1440 2880
jail_default_bantime_overalljails: false
jail_default_ignoreself: true
jail_default_ignoreip: 127.0.0.1/8 ::1
jail_default_bantime: 10m
jail_default_findtime: 10m
jail_default_maxretry: 5m
jail_default_maxmatches: "%(maxretry)s"
jail_default_backend: auto
jail_default_usedns: warn
jail_default_logencoding: auto
jail_default_filter_mode: normal
jail_default_filter: "%(__name__)s[mode=%(mode)s]"

jail_sshd_filter_mode: normal
jail_sshd_port: ssh
jail_ssh_logpath: "%(sshd_log)s"
jail_ssh_backend: "%(sshd_backend)s"

jail_dropbear_filter_mode: normal
jail_dropbear_port: ssh
jail_dropbear_logpath: "%(dropbear_log)s"
jail_dropbear_backend: "%(dropbear_backend)s"

jail_selinux_ssh_filter_mode: normal
jail_selinux_ssh_port: ssh
jail_selinux_ssh_logpath: "%(auditd_log)s"

```

Dependencies
------------



Example Playbook
----------------

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

    - hosts: servers
      roles:
         - { role: username.rolename, x: 42 }

License
-------

BSD

Author Information
------------------

An optional section for the role authors to include contact information, or a website (HTML is not allowed).