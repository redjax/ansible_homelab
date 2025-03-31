from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
import importlib.util
import logging
import logging.config
import os
from pathlib import Path
import platform
import secrets
import shutil
import typing as t

import nox
import nox.command

## Create logger for this module
log: logging.Logger = logging.getLogger("nox")

## Set nox options
if importlib.util.find_spec("uv"):
    nox.options.default_venv_backend = "uv|virtualenv"
else:
    nox.options.default_venv_backend = "virtualenv"
nox.options.reuse_existing_virtualenvs = True
nox.options.error_on_external_run = False
nox.options.error_on_missing_interpreters = False
# nox.options.report = True

nox.options.sessions = ["build-my-collections", "install-ansible-requirements"]

########
# Vars #
########

## Detect container env, or default to False
if "CONTAINER_ENV" in os.environ:
    CONTAINER_ENV: bool = os.environ["CONTAINER_ENV"]
else:
    CONTAINER_ENV: bool = False

## Define versions to test
PY_VERSIONS: list[str] = ["3.12", "3.11"]
## Get tuple of Python ver ('maj', 'min', 'mic')
PY_VER_TUPLE: tuple[str, str, str] = platform.python_version_tuple()
## Dynamically set Python version
DEFAULT_PYTHON: str = f"{PY_VER_TUPLE[0]}.{PY_VER_TUPLE[1]}"

# this VENV_DIR constant specifies the name of the dir that the `dev`
# session will create, containing the virtualenv;
# the `resolve()` makes it portable
VENV_DIR = Path("./.venv").resolve()

COLLECTIONS_PATH: Path = Path("./collections")
ANSIBLE_COLLECTIONS_PATH: Path = Path(f"{COLLECTIONS_PATH}/ansible_collections")
MY_COLLECTIONS_PATH: Path = Path(f"{COLLECTIONS_PATH}/my")
COLLECTION_BUILD_OUTPUT_PATH: Path = Path("./build")

## Set paths to lint with the lint session
LINT_PATHS: list[str] = ["scripts"]

## MKDocs
DOCS_REQUIREMENTS_FILE: Path = Path("docs/requirements.txt")
DOCS_VENV_PATH: Path = Path(".mkdocs-venv")
MKDOCS_DEV_PORT: int = 8000
MKDOCS_DEV_ADDR: str = "0.0.0.0"

###########
# Classes #
###########

@dataclass
class CustomAnsibleCollection:
    """Define a custom Ansible collection for Nox sessions.

    Params:
        name (str): The simple name of the role, mainly used for logging messages.
        fqcn (str): The fully-qualified collection name, i.e. `my.collection`
        path (Path): The local file path to the Ansible collection.

    """

    name: str = field(default=None)
    fqcn: str = field(default=None)
    path: Path | None = field(default=None)

    @property
    def path_exists(self) -> bool:
        if self.path:
            return self.path.exists()
        else:
            return False

    def __post_init__(self):
        if self.path:
            _path: Path = Path(f"{self.path}")

            self.path = _path

        _log = logging.getLogger("nox.CustomAnsibleCollection")
        self.logger = _log


## Define custom Ansible collection objects. The build-my-collections session iterates over this list, building
#  the distribution package for each collection in the list.
CUSTOM_COLLECTIONS: t.List[CustomAnsibleCollection] = [
    CustomAnsibleCollection(
        name="homelab", fqcn="my.homelab", path=Path(f"{MY_COLLECTIONS_PATH}/homelab")
    ),
    CustomAnsibleCollection(
        name="weather-monorepo",
        fqcn="my.weather_monorepo",
        path=Path(f"{MY_COLLECTIONS_PATH}/weather_monorepo"),
    ),
]

###########
# Methods #
###########

def install_uv_project(session: nox.Session, external: bool = False) -> None:
    """Method to install uv and the current project in a nox session."""
    log.info("Installing uv in session")
    session.install("uv")
    log.info("Syncing uv project")
    session.run("uv", "sync", external=external)
    log.info("Installing project")
    session.run("uv", "pip", "install", ".", external=external)


@contextmanager
def cd(newdir):
    """Context manager to change a directory before executing command."""
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)


def check_path_exists(p: t.Union[str, Path] = None) -> bool:
    """Check the existence of a path.

    Params:
        p (str | Path): The path to the directory/file to check.

    Returns:
        (True): If Path defined in `p` exists.
        (False): If Path defined in `p` does not exist.

    """
    p: Path = Path(f"{p}")
    if "~" in f"{p}":
        p = p.expanduser()

    _exists: bool = p.exists()

    if not _exists:
        log.error(FileNotFoundError(f"Could not find path '{p}'."))

    return _exists


def install_uv_project(session: nox.Session, external: bool = False) -> None:
    """Method to install uv and the current project in a nox session."""
    log.info("Installing uv in session")
    session.install("uv")
    log.info("Syncing uv project")
    session.run("uv", "sync", external=external)
    log.info("Installing project")
    session.run("uv", "pip", "install", ".", external=external)


############
# Sessions #
############

@nox.session(python=[DEFAULT_PYTHON], name="vulture-check", tags=["quality"])
def run_vulture_check(session: nox.Session):
    session.install(f"vulture")

    log.info("Checking for dead code with vulture")
    session.run("vulture", "scripts/", "--min-confidence", "100")
    session.run("vulture", "./noxfile.py", "--min-confidence", "100")
    

@nox.session(python=[DEFAULT_PYTHON], name="uv-export")
def export_requirements(session: nox.Session):
    ## Ensure REQUIREMENTS_OUTPUT_DIR path exists
    session.install(f"uv")

    log.info("Exporting production requirements")
    # session.run(
    #     "uv",
    #     "pip",
    #     "compile",
    #     "pyproject.toml",
    #     "-o",
    #     "requirements.txt",
    # )
    session.run(
        "uv",
        "export",
        "--no-dev",
        "-o",
        "requirements.txt"
    )

    
    log.info("Exporting development requirements")
    session.run(
        "uv",
        "export",
        "-o",
        "requirements.dev.txt"   
    )


@nox.session(name="update-uv-requirements", tags=["requirements", "update"])
def update_uv_requirements(session: nox.Session):
    session.install("uv")
    
    log.info("Updating uv requirements")
    session.run("uv", "sync", "--dev", "--all-extras", "--upgrade")


@nox.session(python=[DEFAULT_PYTHON], name="lint", tags=["style"])
@nox.parametrize("lint_paths", [LINT_PATHS])
def run_linter(session: nox.Session, lint_paths: list[Path]):
    session.install("ruff", "black")

    log.info("Linting code")

    if lint_paths:
        for d in LINT_PATHS:
            if not Path(d).exists():
                log.warning(f"Skipping lint path '{d}', could not find path")
                pass
            else:
                lint_path: Path = Path(d)
                log.info(f"Running ruff imports sort on '{d}'")
                session.run(
                    "ruff",
                    "--select",
                    "I",
                    "--fix",
                    lint_path,
                )

                log.info(f"Formatting '{d}' with Black")
                session.run(
                    "black",
                    lint_path,
                )

                log.info(f"Running ruff checks on '{d}' with --fix")
                session.run(
                    "ruff",
                    "check",
                    # "--config",
                    # "ruff.ci.toml",
                    lint_path,
                    "--fix",
                )

    log.info("Linting noxfile.py")
    session.run(
        "ruff",
        "check",
        f"{Path('./noxfile.py')}",
        "--fix",
    )

    log.info(f"Running ruff imports sort on noxfile.py")
    session.run(
        "ruff",
        "check",
        f"{Path('./noxfile.py')}",
        "--select",
        "I",
        "--fix",
    )


@nox.session(name="upgrade-packages", tags=["update", "security"])
def upgrade_pkgs(session: nox.Session):
    install_uv_project(session, external=True)
    
    log.info("Synchronizing packages")
    session.run("uv", "lock", "--upgrade")
    log.info("Synchronizing packages after upgrade")
    session.run("uv", "sync", "--all-extras", "--dev")
    
    
@nox.session(name="init-clone-setup")
def run_init_clone_setup(session: nox.Session):
    install_uv_project(session)

    copy_paths = [
        {
            "src": "./inventories/homelab/inventory.example.yml",
            "dest": "./inventories/homelab/inventory.yml"
        },
        {
            "src": "./inventories/homelab/group_vars/all.example.yml",
            "dest": "./inventories/homelab/group_vars/all.yml"
        }
    ]
    
    for p in copy_paths:
        if not Path(p["dest"]).exists():
            log.info(f"Copying {p['src']} to {p['dest']}")
            shutil.copyfile(p["src"], p["dest"])

        else:
            log.info(f"{p['dest']} already exists, skipping copy")

###########
# Ansible #
###########

@nox.session(
    python=DEFAULT_PYTHON, name="build-my-collections", tags=["ansible", "build"]
)
@nox.parametrize("custom_collections", [CUSTOM_COLLECTIONS])
@nox.parametrize("collection_build_output_path", [COLLECTION_BUILD_OUTPUT_PATH])
def build_custom_collections(
    session: nox.Session,
    custom_collections: list[CustomAnsibleCollection],
    collection_build_output_path: Path,
):
    if not collection_build_output_path.exists():
        try:
            collection_build_output_path.mkdir(parents=True, exist_ok=True)
        except Exception as exc:
            msg = Exception(
                f"({type(exc)}) Unhandled exception creating build output path '{collection_build_output_path}'. Details: {exc}"
            )
            log.error(msg)

            raise exc

    # session.install("ansible-core")
    install_uv_project(session=session)

    for _collection in custom_collections:
        log.info(
            f"Building collection '{_collection.name}' at path: {_collection.path}"
        )

        if not _collection.path_exists:
            _exc = FileNotFoundError(
                f"Could not find collection at path '{_collection.path}'"
            )
            log.error(_exc)

            raise _exc

        log.debug(f"Found collection '{_collection.name}' at path: {_collection.path}")

        try:
            session.run(
                "uv",
                "run",
                "ansible-galaxy",
                "collection",
                "build",
                f"{_collection.path}",
                "--output-path",
                f"{collection_build_output_path}",
                "--force",
            )
        except Exception as exc:
            msg = Exception(
                f"({type(exc)}) Unhandled exception building collection '{_collection.name}'. Details: {exc}"
            )
            log.error(msg)

            continue



@nox.session(
    python=DEFAULT_PYTHON,
    name="install-ansible-requirements",
    tags=["ansible", "install"],
)
def install_collections(session: nox.Session):
    assert Path("requirements.yml").exists(), FileNotFoundError(
        "Could not find Ansible project requirements.yml."
    )

    install_uv_project(session=session)

    try:
        session.run(
            "uv",
            "run",
            "ansible-galaxy",
            "collection",
            "install",
            "-r",
            "requirements.yml",
        )
    except Exception as exc:
        msg = Exception(
            f"({type(exc)}) Unhandled exception installing Ansible Galaxy requirements from requirements.yml. Details: {exc}"
        )
        log.error(msg)

        raise exc

    log.info("Installing roles from requirements.yml")

    try:
        session.run(
            "uv", "run", "ansible-galaxy", "role", "install", "-r", "requirements.yml"
        )
    except Exception as exc:
        msg = Exception(
            f"({type(exc)}) Unhandled exception installing Ansible Galaxy requirements from requirements.yml. Details: {exc}"
        )
        log.error(msg)

        raise exc

    if Path("requirements.private.yml").exists():
        log.info(
            "Ensuring local collections are installed from requirements.private.yml with --force"
        )
        try:
            session.run(
                "uv",
                "run",
                "ansible-galaxy",
                "collection",
                "install",
                "-r",
                "requirements.private.yml",
                "--force",
            )
        except Exception as exc:
            msg = Exception(
                f"Unhandled exception installing packages from 'requirements.private.yml'. Details: {exc}"
            )
            log.error(msg)

            raise exc


@nox.session(python=DEFAULT_PYTHON, name="playbook-debug-all", tags=["debug"])
def ansible_playbook_debug_all(session: nox.Session):
    session.install("ansible-core")

    log.info("Running debug-all.yml playbook on homelab inventory")

    try:
        session.run(
            "ansible-playbook",
            "-i",
            "inventories/homelab/inventory.yml",
            "plays/debug/debug-all.yml",
        )
    except Exception as exc:
        msg = Exception(
            f"({type(exc)}) Unhandled exception running playbook. Details: {exc}"
        )
        log.error(msg)

        raise exc


@nox.session(python=DEFAULT_PYTHON, name="update-systems", tags=["maint"])
def ansible_playbook_update_systems(session: nox.Session):
    session.install("ansible-core")

    log.info(
        "Running maint/update-system.yml playbook on homelab inventory, limit 'autoReboot'."
    )

    try:
        session.run(
            "ansible-playbook",
            "-i",
            "inventories/homelab/inventory.yml",
            "--limit",
            "autoReboot",
            "plays/maint/update-reboot-system.yml",
        )
    except Exception as exc:
        msg = Exception(
            f"({type(exc)}) Unhandled exception running system update playbook. Details: {exc}"
        )
        log.error(msg)

        raise exc


@nox.session(python=DEFAULT_PYTHON, name="onboard", tags=["ansible", "onboard"])
def run_ansible_onboarding(session: nox.Session):
    session.install("ansible-core")

    log.info("Running Ansible onboarding playbook")

    try:
        session.run(
            "ansible-playbook",
            "-i",
            "inventories/onboard/inventory.yml",
            "--limit",
            "onboard",
            "plays/onboard/create-ansible-svc-user.yml",
        )
    except Exception as exc:
        msg = Exception(
            f"Unhandled exception running Ansible onboarding playbook. Details: {exc}"
        )
        log.error(msg)

        raise exc


@nox.session(
    python=DEFAULT_PYTHON,
    name="init-ansible-vault",
    tags=["ansible", "security", "vault"],
)
@nox.parametrize("vault_pass_file", [".vault/vault_pass"])
@nox.parametrize("vault_file", [".vault/vault.yam"])
def initialize_ansible_vault(
    session: nox.Session, vault_pass_file: str, vault_file: str
):
    session.install("ansible-core")

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
        alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+"
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
            session.run(
                "ansible-vault",
                "encrypt",
                str(vault_file),
                "--vault-password-file",
                vault_pass_file,
                check=True,
            )
        except nox.command.CommandFailed as exc:
            log.error(f"({type(exc)} Failed to encrypt vault file: {exc}")
            raise

    init_ansible_vault()


##########
# MkDocs #
##########

@nox.session(python=DEFAULT_PYTHON, name="setup-mkdocs", tags=["mkdocs", "docs"])
@nox.parametrize("docs_requirements_file", [DOCS_REQUIREMENTS_FILE])
@nox.parametrize("docs_venv_path", [DOCS_VENV_PATH])
def run_mkdocs_venv_setup(
    session: nox.Session,
    docs_requirements_file: t.Union[str, Path],
    docs_venv_path: t.Union[str, Path],
):
    if not docs_requirements_file.exists():
        raise FileNotFoundError(
            f"Could not find mkdocs requirements file at '{docs_requirements_file}'."
        )

    # session.install("-r", f"{DOCS_REQUIREMENTS_FILE}")
    session.install("virtualenv")

    log.info(f"Creating MKDocs virtual environment at path: {docs_venv_path}")
    try:
        session.run("virtualenv", f"{docs_venv_path}")
    except Exception as exc:
        msg = Exception(
            f"({type(exc)}) Unhandled exception creating mkdocs virtual environment. Details: {exc}"
        )
        log.error(msg)

        raise exc

    log.warning(
        f"!!! [MANUAL STEP REQUIRED]\nMKDocs virtual environment created at path '{docs_venv_path}'. Activate with '. {docs_venv_path}/bin/activate', then install requirements  with 'pip install -r docs/requirements.txt'."
    )


@nox.session(
    python=[DEFAULT_PYTHON], name="build-mkdocs", tags=["mkdocs", "docs", "build"]
)
@nox.parametrize("docs_requirements_file", [DOCS_REQUIREMENTS_FILE])
def run_mkdocs_build(session: nox.Session, docs_requirements_file: t.Union[str, Path]):
    if not docs_requirements_file.exists():
        raise FileNotFoundError(
            f"Could not find mkdocs requirements file at path: '{docs_requirements_file}'"
        )

    session.install("-r", f"{docs_requirements_file}")

    log.info("Building MKDocs site")
    try:
        session.run("mkdocs", "build")
    except Exception as exc:
        msg = Exception(
            f"({type(exc)}) Unhandled exception building MKDocs site. Details: {exc}"
        )
        log.error(msg)

        raise exc


@nox.session(
    python=[DEFAULT_PYTHON], name="serve-mkdocs", tags=["mkdocs", "docs", "serve"]
)
@nox.parametrize("docs_requirements_file", [DOCS_REQUIREMENTS_FILE])
@nox.parametrize("mkdocs_dev_port", [MKDOCS_DEV_PORT])
@nox.parametrize("mkdocs_dev_addr", [MKDOCS_DEV_ADDR])
def run_mkdocs_serve(
    session: nox.Session,
    docs_requirements_file: t.Union[str, Path],
    mkdocs_dev_addr: str,
    mkdocs_dev_port: int,
):
    if not docs_requirements_file.exists():
        raise FileNotFoundError(
            f"Could not find mkdocs requirements file at path: '{docs_requirements_file}'"
        )

    session.install("-r", f"{docs_requirements_file}")

    log.info("Serving MKDocs site")
    try:
        session.run(
            "mkdocs", "serve", "--dev-addr", f"{mkdocs_dev_addr}:{mkdocs_dev_port}"
        )
    except Exception as exc:
        msg = Exception(
            f"({type(exc)}) Unhandled exception serving MKDocs site. Details: {exc}"
        )
        log.error(msg)

        raise exc
