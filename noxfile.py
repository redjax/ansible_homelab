from __future__ import annotations

from dataclasses import dataclass, field
import logging
import logging.config
import os
from pathlib import Path
import platform
import typing as t

import nox

nox.options.default_venv_backend = "venv"
nox.options.reuse_existing_virtualenvs = True
nox.options.error_on_external_run = False
nox.options.error_on_missing_interpreters = False
# nox.options.report = True

nox.options.sessions = ["build-my-collections", "install-ansible-requirements"]

## Detect container env, or default to False
if "CONTAINER_ENV" in os.environ:
    CONTAINER_ENV: bool = os.environ["CONTAINER_ENV"]
else:
    CONTAINER_ENV: bool = False
    
COLLECTIONS_PATH: Path = Path("./collections")
ANSIBLE_COLLECTIONS_PATH: Path = Path(f"{COLLECTIONS_PATH}/ansible_collections")
MY_COLLECTIONS_PATH: Path = Path(f"{COLLECTIONS_PATH}/my")
COLLECTION_BUILD_OUTPUT_PATH: Path = Path("./build")

## Set paths to lint with the lint session
LINT_PATHS: list[str] = []

## MKDocs
DOCS_REQUIREMENTS_FILE: Path = Path("docs/requirements.txt")
DOCS_VENV_PATH: Path = Path(".mkdocs-venv")
MKDOCS_DEV_PORT: int = 8000
MKDOCS_DEV_ADDR: str = "0.0.0.0"

def setup_nox_logging(
    level_name: str = "DEBUG", disable_loggers: list[str] | None = []
) -> None:
    """Configure a logger for the Nox module.

    Params:
        level_name (str): The uppercase string repesenting a logging logLevel.
        disable_loggers (list[str] | None): A list of logger names to disable, i.e. for 3rd party apps.
            Note: Disabling means setting the logLevel to `WARNING`, so you can still see errors.

    """
    ## If container environment detected, default to logging.DEBUG
    if CONTAINER_ENV:
        level_name: str = "DEBUG"

    logging_config: dict = {
        "version": 1,
        "disable_existing_loggers": False,
        "loggers": {
            "nox": {
                "level": level_name.upper(),
                "handlers": ["console"],
                "propagate": False,
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "nox",
                "level": "DEBUG",
                "stream": "ext://sys.stdout",
            }
        },
        "formatters": {
            "nox": {
                "format": "[NOX] [%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
                "datefmt": "%Y-%m-%D %H:%M:%S",
            }
        },
    }

    ## Configure logging. Only run this once in an application
    logging.config.dictConfig(config=logging_config)

    ## Disable loggers by name. Sets logLevel to logging.WARNING to suppress all but warnings & errors
    for _logger in disable_loggers:
        logging.getLogger(_logger).setLevel(logging.WARNING)
        
setup_nox_logging(level_name="DEBUG", disable_loggers=[])
log = logging.getLogger("nox")

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
    CustomAnsibleCollection(name="homelab", fqcn="my.homelab", path=Path(f"{MY_COLLECTIONS_PATH}/homelab"))
]

## Define versions to test
PY_VERSIONS: list[str] = ["3.12", "3.11"]
## Get tuple of Python ver ('maj', 'min', 'mic')
PY_VER_TUPLE = platform.python_version_tuple()
## Dynamically set Python version
DEFAULT_PYTHON: str = f"{PY_VER_TUPLE[0]}.{PY_VER_TUPLE[1]}"

@nox.session(python=[DEFAULT_PYTHON], name="setup-mkdocs", tags=["mkdocs", "docs"])
@nox.parametrize("docs_requirements_file", [DOCS_REQUIREMENTS_FILE])
@nox.parametrize("docs_venv_path", [DOCS_VENV_PATH])
def run_mkdocs_venv_setup(session: nox.Session, docs_requirements_file: t.Union[str, Path], docs_venv_path: t.Union[str, Path]):
    if not docs_requirements_file.exists():
        raise FileNotFoundError(f"Could not find mkdocs requirements file at '{docs_requirements_file}'.")
    
    # session.install("-r", f"{DOCS_REQUIREMENTS_FILE}")
    session.install("virtualenv")
    
    log.info(f"Creating MKDocs virtual environment at path: {docs_venv_path}")
    try:
        session.run("virtualenv", f"{docs_venv_path}")
    except Exception as exc:
        msg = Exception(f"({type(exc)}) Unhandled exception creating mkdocs virtual environment. Details: {exc}")
        log.error(msg)
        
        raise exc
    
    log.warning(f"!!! [MANUAL STEP REQUIRED]\nMKDocs virtual environment created at path '{docs_venv_path}'. Activate with '. {docs_venv_path}/bin/activate', then install requirements  with 'pip install -r docs/requirements.txt'.")

@nox.session(python=[DEFAULT_PYTHON], name="build-mkdocs", tags=["mkdocs", "docs", "build"])
@nox.parametrize("docs_requirements_file", [DOCS_REQUIREMENTS_FILE])
def run_mkdocs_build(session: nox.Session, docs_requirements_file: t.Union[str, Path]):
    if not docs_requirements_file.exists():
        raise FileNotFoundError(f"Could not find mkdocs requirements file at path: '{docs_requirements_file}'")

    session.install("-r", f"{docs_requirements_file}")
    
    log.info("Building MKDocs site")
    try:
        session.run("mkdocs", "build")
    except Exception as exc:
        msg = Exception(f"({type(exc)}) Unhandled exception building MKDocs site. Details: {exc}")
        log.error(msg)
        
        raise exc

@nox.session(python=[DEFAULT_PYTHON], name="serve-mkdocs", tags=["mkdocs", "docs", "serve"])
@nox.parametrize("docs_requirements_file", [DOCS_REQUIREMENTS_FILE])
@nox.parametrize("mkdocs_dev_port", [MKDOCS_DEV_PORT])
@nox.parametrize("mkdocs_dev_addr", [MKDOCS_DEV_ADDR])
def run_mkdocs_serve(session: nox.Session, docs_requirements_file: t.Union[str, Path], mkdocs_dev_addr: str, mkdocs_dev_port: int):
    if not docs_requirements_file.exists():
        raise FileNotFoundError(f"Could not find mkdocs requirements file at path: '{docs_requirements_file}'")

    session.install("-r", f"{docs_requirements_file}")
    
    log.info("Serving MKDocs site")
    try:
        session.run("mkdocs", "serve", "--dev-addr", f"{mkdocs_dev_addr}:{mkdocs_dev_port}")
    except Exception as exc:
        msg = Exception(f"({type(exc)}) Unhandled exception serving MKDocs site. Details: {exc}")
        log.error(msg)
        
        raise exc

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

@nox.session(python=DEFAULT_PYTHON, name="build-my-collections", tags=["ansible", "build"])
@nox.parametrize("custom_collections", [CUSTOM_COLLECTIONS])
@nox.parametrize("collection_build_output_path", [COLLECTION_BUILD_OUTPUT_PATH])
def build_custom_collections(session: nox.Session, custom_collections: list[CustomAnsibleCollection], collection_build_output_path: Path):
    if not collection_build_output_path.exists():
        try:
            collection_build_output_path.mkdir(parents=True, exist_ok=True)
        except Exception as exc:
            msg = Exception(f"({type(exc)}) Unhandled exception creating build output path '{collection_build_output_path}'. Details: {exc}")
            log.error(msg)
            
            raise exc
    
    session.install("ansible-core")
    
    for _collection in custom_collections:
        log.info(f"Building collection '{_collection.name}' at path: {_collection.path}")
        
        if not _collection.path_exists:
            _exc = FileNotFoundError(f"Could not find collection at path '{_collection.path}'")
            log.error(_exc)
            
            raise _exc
        
        log.debug(f"Found collection '{_collection.name}' at path: {_collection.path}")
        
        try:
            session.run("ansible-galaxy", "collection", "build", f"{_collection.path}", "--output-path", f"{collection_build_output_path}", "--force")
        except Exception as exc:
            msg = Exception(f"({type(exc)}) Unhandled exception building collection '{_collection.name}'. Details: {exc}")
            log.error(msg)
            
            continue
        
        
@nox.session(python=DEFAULT_PYTHON, name="install-ansible-requirements", tags=["ansible", "install"])
def install_collections(session: nox.Session):
    assert Path("requirements.yml").exists(), FileNotFoundError("Could not find Ansible project requirements.yml.")
    
    session.install("ansible-core")
    
    log.info("Installing collections from requirements.yml")
    
    try:
        session.run("ansible-galaxy", "collection", "install", "-r", "requirements.yml")
    except Exception as exc:
        msg = Exception(f"({type(exc)}) Unhandled exception installing Ansible Galaxy requirements from requirements.yml. Details: {exc}")
        log.error(msg)
        
        raise exc
    
    log.info("Installing roles from requirements.yml")
    
    try:
        session.run("ansible-galaxy", "role", "install", "-r", "requirements.yml")
    except Exception as exc:
        msg = Exception(f"({type(exc)}) Unhandled exception installing Ansible Galaxy requirements from requirements.yml. Details: {exc}")
        log.error(msg)
        
        raise exc
    
    if Path("requirements.private.yml").exists():
        log.info("Ensuring local collections are installed from requirements.private.yml with --force")
        try:
            session.run("ansible-galaxy", "collection", "install", "-r", "requirements.private.yml", "--force")
        except Exception as exc:
            msg = Exception(f"Unhandled exception installing packages from 'requirements.private.yml'. Details: {exc}")
            log.error(msg)
            
            raise exc

@nox.session(python=DEFAULT_PYTHON, name="playbook-debug-all", tags=["debug"])
def ansible_playbook_debug_all(session: nox.Session):
    session.install("ansible-core")
    
    log.info("Running debug-all.yml playbook on homelab inventory")
    
    try:
        session.run("ansible-playbook", "-i", "inventories/homelab/inventory.yml", "plays/debug/debug-all.yml")
    except Exception as exc:
        msg = Exception(f"({type(exc)}) Unhandled exception running playbook. Details: {exc}")
        log.error(msg)
        
        raise exc
    
@nox.session(python=DEFAULT_PYTHON, name="update-systems", tags=["maint"])
def ansible_playbook_update_systems(session: nox.Session):
    session.install("ansible-core")
    
    log.info("Running maint/update-system.yml playbook on homelab inventory, limit 'autoReboot'.")
    
    try:
        session.run("ansible-playbook", "-i", "inventories/homelab/inventory.yml", "--limit", "autoReboot", "plays/maint/update-system.yml")
    except Exception as exc:
        msg = Exception(f"({type(exc)}) Unhandled exception running system update playbook. Details: {exc}")
        log.error(msg)
        
        raise exc
    
@nox.session(python=DEFAULT_PYTHON, name="onboard", tags=["ansible", "onboard"])
def run_ansible_onboarding(session: nox.Session):
    session.install("ansible-core")
    
    log.info("Running Ansible onboarding playbook")
    
    try:
        session.run("ansible-playbook", "-i", "inventories/onboard/inventory.yml", "--limit", "onboard", "plays/onboard/create-ansible-svc-user.yml")
    except Exception as exc:
        msg  = Exception(f"Unhandled exception running Ansible onboarding playbook. Details: {exc}")
        log.error(msg)
        
        raise exc