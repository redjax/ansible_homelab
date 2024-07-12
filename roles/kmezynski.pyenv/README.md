# Ansible Role: Pyenv

Installs and configures [Pyenv](https://github.com/pyenv/pyenv) with
given plugins and Python versions on RHEL or Debian/Ubuntu servers.

## Requirements

None.

## Role Variables

Available variables are listed below, along with default values (refer to
[defaults/main](defaults/main) and [vars](vars) directories).

```yaml
pyenv_global: false
pyenv_git_ref: master
pyenv_owner: "{{ ansible_user_id }}"
pyenv_group: pyenv
pyenv_path: "{{ '/opt/pyenv' if pyenv_global else ansible_user_dir + '/.pyenv' }}"

pyenv_config_path: "{{ '/etc/pyenv' if pyenv_global else ansible_user_dir + '/.dotfiles' }}"
pyenv_init_options: "{{ '--no-rehash' if not pyenv_global }}"
shell_init_paths: "{{ shell_init.global if pyenv_global else shell_init.local }}"
```

These are variables that control entire Pyenv installation process. Key one is
`pyenv_global` which by deafult determines:

- `pyenv_path` - Pyenv installation path (system-wide/local).
- `pyenv_config_path` - Pyenv configuration script path.
- `pyenv_init_options` - flags for `pyenv init` command added to
  Pyenv configuration script.
- `shell_init_paths` - list of user's shell initialization files that sources
  `pyenv_config_path` file.

For the time being **only** `bash`, `zsh` and `fish` shells are detected
automatically. These variables along with Pyenv git ref `pyenv_git_ref` are
fully customizable according to target server's needs.

`pyenv_owner` and `pyenv_group` variables are especially critical for
system-wide installation to set proper permissions so that every user can use
Pyenv freely.

```yaml
pyenv_autocompletion: true
pyenv_default_python: 3.11.2
pyenv_python_versions:
  - 3.11.2
```

Above variables configures Pyenv after it is installed:

- `pyenv_autocompletion` - enables Pyenv commands autocompletion for user's
  shell.
- `pyenv_default_python` - Python version to be set as a default interpreter.
- `pyenv_python_versions` - list of Python versions, supported by given version
  of Pyenv, to be installed on the server.

```yaml
pyenv_plugins:
  - name: pyenv-virtualenv
    repo: https://github.com/pyenv/pyenv-virtualenv.git
  - name: pyenv-update
    repo: https://github.com/pyenv/pyenv-update.git
pyenv_virtualenvs: {}
pyenv_update: false
```

Above variables allows installation of Pyenv plugins and configures them:

- `pyenv_plugins` - list of Pyenv plugins to be installed on the server. Both
  `name` and `repo` have to be provided for each plugin, `version` is optional
  and indicates revision of a plugin repository.
- `pyenv_virtualenvs` - list of Pyenv virtualenvs to be created on the server.
  Both `name` and `version` from `pyenv_python_versions` have to be provided.
- `pyenv_update` - updates of Pyenv and its plugins to the latest version.

## Dependencies

None.

## Example Playbook

```yaml
- hosts: all
  roles:
    - role: kmezynski.pyenv
      pyenv_global: true
      pyenv_path: /usr/local/share
      pyenv_default_python: false
      pyenv_python_versions:
        - 3.11.2
        - 3.10.9
```

## License

This role is distributed under the terms of [MIT](https://opensource.org/license/mit/)
license.

## Author Information

This role was created in 2023 by [Kamil Mężyński](https://github.com/kmezynski).
