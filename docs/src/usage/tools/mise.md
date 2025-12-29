# Mise

The [repository](https://github.com/redjax/Ansible) uses `mise` to install and manage tools, like Ansible itself and the [`go-task/task` program](), which runs automations for the repository. See the [`mise` getting started guide](https://mise.jdx.dev/getting-started.html#installing-mise-cli) for platform-specific installation instructions.

You can install tools with `mise` in any path that has a `.mise.toml` file:

```shell title="Install tools with mise" linenums="1"
mise trust
mise install
```

## Activating Mise

Mise needs to be ['activated'](https://mise.jdx.dev/getting-started.html#activate-mise) before you can use it. On Linux, that means adding this to your `~/.bashrc`:

```shell title="Mise ~/.bashrc activation"
echo 'eval "$(~/.local/bin/mise activate bash)"' >> ~/.bashrc
```

On Windows, add this to your `$PROFILE`:

```powershell title="Mise Powershell activation"
$shimPath = "$env:USERPROFILE\AppData\Local\mise\shims"
$currentPath = [Environment]::GetEnvironmentVariable('Path', 'User')
$newPath = $currentPath + ";" + $shimPath
[Environment]::SetEnvironmentVariable('Path', $newPath, 'User')
```

In Bash scripts/Docker, you need to run `eval "$(~/.local/bin/mise activate bash)"` once, early in the script, to activate Mise before running other commands. For example, in a Bash script:

```shell title="Mise activation in Bash script" linenums="1"
#!/usr/bin/env bash
set -euo pipefail

if ! command -v mise &>/dev/null; then
  eval "$(~/.local/bin/mise activate bash)"
fi

## Add the latest Python, just for this script
mise use python@latest

## Show path to Python, should be a ~/.local/share/mise/ path
which python
python --version
```

## Adding tools

Find the tool you want to install on the [mise-tools site](https://mise-tools.jdx.dev), i.e. [`python`](https://mise-tools.jdx.dev/tools/python). Note the package name, i.e. `core:python`, and the `Install with mise:` example command.

Edit your `.mise.toml` and add the tool, either a pinned version (recommended) or the latest version with `latest`:

```toml title="Mise toml tool definition" linenums="1"
[tools]
python = "latest"  # or a specfic version, i.e. python = 3.14.2
```
