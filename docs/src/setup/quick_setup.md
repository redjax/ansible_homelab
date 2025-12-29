# Quick Setup

!!! note
    This setup guide assumes you are using [`mise`](https://mise.jdx.dev).

    You only have to do this setup once when you first clone the repository. After that, you can just edit the existing SSH config and inventories to add hosts.

- Trust & install `mise` file and source Direnv `.envrc`:

```shell linenums="1" title="Mise, direnv, go-task/task setup"
mise trust
mise install
direnv allow
task ansible-requiements

## If developing the docs, run this too
task mkdocs-setup
```

- Create SSH keys
  - If you already have a key you've copied to the remote host(s) you want to manage, you can copy that into the `.ssh/` directory and use that key instead of creating a new one.

```shell title="Generate Ansible SSH keys"
ssh-keygen -t ed25519 -b 4096 -f .ssh/ansible_svc -N ""
```

- Copy the example SSH config [`./.ssh/example_config`](https://github.com/redjax/Ansible/tree/main/.ssh/example_config) to a new file:
    - `cp .ssh/example_config .ssh/config`
    - Edit this file with your host(s), using the included example as a reference

!!! note
    After copying the example inventory and `group_vars/all.yml` files, make sure to edit them with the data for your host/SSH keys/etc.

- Create your onboarding inventory
    - Start by copying [`inventories/onboard/example.inventory.yml`](https://github.com/redjax/Ansible/tree/main/inventories/onboard/example.inventory.yml) to `inventories/onboard/inventory.yml` and [`inventories/onboard/group_vars/example.all.yml`](https://github.com/redjax/Ansible/tree/main/inventories/onboard/group_vars/example.all.yml) to `inventories/onboard/group_vars/all.yml`.
        - This inventory assumes you can connect to the remote with a password or your host's `id_rsa` SSH key.
        - The [`plays/onboard/run-onboarding.yml`](https://github.com/redjax/Ansible/tree/main/plays/onboard/run-onboarding.yml) playbook will create the `ansible_svc` user on the remote host and copy the `.ssh/ansible_ssh` SSH key you created.
        - Use the example hosts as a reference to add the hosts you want to manage with Ansible.
    - Run the onboarding playbook, using `-k` to prompt for connection password if you have not already copied an SSH key to connect to the remote host:

```shell linenums="1" title="Run onboarding playbook"
ansible-playbook \
    -i inventories/onboard/inventory.yml \
    --limit <inventory-host-or-group> \
    plays/onboard/run-onboarding.yml \
    -k
```

- Create the main/"homelab" inventory
    - Copy [`inventories/homelab/example.inventory.yml`](https://github.com/redjax/Ansible/tree/main/inventories/homelab/example.inventory.yml) to `inventories/homelab/inventory.yml` and [`inventories/homelab/group_vars/example.all.yml`](https://github.com/redjax/Ansible/tree/main/inventories/homelab/group_vars/example.all.yml) to `inventories/homelab/group_vars/all.yml`
    - Add the host(s) from your onboarding inventory, removing any `ansible_user` or `ansible_ssh_private_key` vars.

- Test the new inventory by running the [`plays/ping.yml`](https://github.com/redjax/Ansible/tree/main/plays/ping.yml) playbook:

```shell linenums="1" title="Run ping playbook"
ansible-playbook \
    -i inventories/homelab/inventory.yml \
    --limit <inventory-host-or-group> \
    plays/ping.yml
```

If the setup was done correctly, you should be able to ping the remote host using the `ansible_svc` SSH key.
