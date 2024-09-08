import typing as t
from pathlib import Path
import os
import secrets
import subprocess

import logging

log = logging.getLogger(__name__)


def init_ansible_vault(
    vault_pass_file: str = ".vault/vault_pass",
    vault_file: str = ".vault/vault.yml",
):
    if not Path(f"{vault_pass_file}").exists():
        ## Vault password file does not exist.
        #  Generate & save password
        vault_password: str = gen_vault_password()

        save_vault_password(
            vault_pass_file=vault_pass_file, vault_password=vault_password
        )
    else:
        ## Vault password file exists.
        #  Read password from file
        with open(vault_pass_file, "r") as f:
            vault_password = f.read().strip()

    if not Path(vault_file).exists():
        create_vault_file(vault_file=vault_file, vault_pass_file=vault_pass_file)


def save_vault_password(
    vault_pass_file: str = ".vault/vault_pass", vault_password: str = None
):
    vault_pass_file: Path = Path(f"{vault_pass_file}")

    if vault_pass_file.exists():
        log.warning(
            f"Vault file '{vault_pass_file}' already exists. Skipping password generation."
        )

        return

    if not vault_pass_file.parent.exists():
        try:
            vault_pass_file.parent.mkdir(exist_ok=True, parents=True)
        except Exception as exc:
            msg = f"({type(exc)}) Unhandled exception creating path '{vault_pass_file.parent}'. Details: {exc}"
            log.error(msg)

            raise exc

    if vault_password is None:
        vault_password = gen_vault_password()

    with open(vault_pass_file, "w") as f:
        f.write(vault_password)


def gen_vault_password(length: int = 32) -> str:
    # Generate a secure random password
    alphabet = (
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+"
    )
    password = "".join(secrets.choice(alphabet) for _ in range(length))
    return password


def create_vault_file(
    vault_file: str = ".vault/vault.yml", vault_pass_file: str = ".vault/vault_pass"
):
    if vault_pass_file is None:
        vault_password = gen_vault_password()
        save_vault_password(
            vault_pass_file=vault_pass_file, vault_password=vault_password
        )

    vault_file: Path = Path(f"{vault_file}")

    if not vault_file.parent.exists():
        try:
            vault_file.parent.mkdir(exist_ok=True, parents=True)
        except Exception as exc:
            msg = f"({type(exc)}) Unhandled exception creating path '{vault_file.parent}'. Details: {exc}"
            log.error(msg)
            raise exc

    vault_content = "---\n# Add your vault content here\n"
    with open(vault_file, "w") as f:
        f.write(vault_content)

    # Encrypt the vault file with the vault password
    try:
        subprocess.run(
            [
                "ansible-vault",
                "encrypt",
                str(vault_file),
                "--vault-password-file",
                vault_pass_file,
            ],
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        log.error(f"Failed to encrypt vault file: {exc}")
        raise


if __name__ == "__main__":
    init_ansible_vault()
