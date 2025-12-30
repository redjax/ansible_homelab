# Taskfile

## Overview

[`go-task/task`](https://taskfile.dev) is a build tool inspired by `Make`. You can define tasks in a `Taskfile.yml`, then run them with `task <task-name>`. This can be for simple things like running a repeatable command, or a dynamic build chain to compile apps.

This repository uses `task` to expose conveniences for the user. Run `task -l` to list the tasks available in the [repository's `Taskfile.yml`](https://github.com/redjax/Ansible/tree/main/Taskfile.yml).

## Tasks dir

While it is acceptable/valid to put all task definitions in the root `Taskfile.yml`, for maintainability this repository keeps tasks in a [`.tasks/`](https://github.com/redjax/Ansible/tree/main/.tasks/) directory. The `.tasks/*.yml` file defines the "business logic" for the task, and the `Taskfile` creates a command the user can run, passing CLI args with `task <name> -- [args]` or `ENV_VAR="value" task <name>`.

## Common Usage

Here are some examples of running the tasks included with this repository.

```shell title="Example task commands" linenums="1"
## Install Ansible requirements.yml file
task ansible-requirements

## Default: Setup MkDocs environment
task mkdocs-setup

## Start local MkDocs development server
MKDOCS_RELOAD=true mkdocs-serve

## Ping all hosts with Ansible
task ping

## Ping a specific host with Ansible
task ping -- <hostname>

## Call Ansible system update play
task update
```
