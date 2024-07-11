from __future__ import annotations

import logging
import logging.config
import os
from pathlib import Path
import platform
import typing as t

import nox

## Detect container env, or default to False
if "CONTAINER_ENV" in os.environ:
    CONTAINER_ENV: bool = os.environ["CONTAINER_ENV"]
else:
    CONTAINER_ENV: bool = False

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


nox.options.default_venv_backend = "venv"
nox.options.reuse_existing_virtualenvs = True
nox.options.error_on_external_run = False
nox.options.error_on_missing_interpreters = False
# nox.options.report = True

nox.sessions = ["lint"]

COLLECTIONS_PATH: Path = Path("./collections")
ANSIBLE_COLLECTIONS_PATH: Path = Path(f"{COLLECTIONS_PATH}/ansible_collections")
MY_COLLECTIONS_PATH: Path = Path(f"{COLLECTIONS_PATH}/my")
COLLECTION_BUILD_OUTPUT_PATH: Path = Path(f"{COLLECTIONS_PATH}/build")

## Set paths to lint with the lint session
LINT_PATHS: list[str] = []

CUSTOM_COLLECTIONS: t.List[dict[str, t.Any]] = [
    {
        "collection_name": "homelab",
        "collection_uri": "my.homelab",
        "collection_path": Path(f"{MY_COLLECTIONS_PATH}/homelab")
    }
]

## Define versions to test
PY_VERSIONS: list[str] = ["3.12", "3.11"]
## Get tuple of Python ver ('maj', 'min', 'mic')
PY_VER_TUPLE = platform.python_version_tuple()
## Dynamically set Python version
DEFAULT_PYTHON: str = f"{PY_VER_TUPLE[0]}.{PY_VER_TUPLE[1]}"

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
def build_custom_collections(session: nox.Session, custom_collections: dict, collection_build_output_path: Path):
    if not collection_build_output_path.exists():
        try:
            collection_build_output_path.mkdir(parents=True, exist_ok=True)
        except Exception as exc:
            msg = Exception(f"({type(exc)}) Unhandled exception creating build output path '{collection_build_output_path}'. Details: {exc}")
            log.error(msg)
            
            raise exc
    
    session.install("ansible-core")
    
    for _collection in custom_collections:
        log.info(f"Building collection '{_collection['collection_name']}' at path: {_collection['collection_path']}")
        
        if not _collection["collection_path"].exists():
            _exc = FileNotFoundError(f"Could not find collection at path '{_collection['collection_path']}'")
            log.error(_exc)
            
            raise _exc
        
        log.debug(f"Found collection '{_collection['collection_name']}' at path: {_collection['collection_path']}")
        
        try:
            session.run("ansible-galaxy", "collection", "build", f"{_collection['collection_path']}", "--output-path", f"{collection_build_output_path}", "--force")
        except Exception as exc:
            msg = Exception(f"({type(exc)}) Unhandled exception building collection '{_collection['collection_name']}'. Details: {exc}")
            log.error(msg)
            
            continue
        
        
@nox.session(python=DEFAULT_PYTHON, name="install-collection-requirements", tags=["ansible", "install"])
def install_collections(session: nox.Session):
    assert Path("requirements.yml").exists(), FileNotFoundError("Could not find Ansible project requirements.yml.")
    
    session.install("ansible-core")
    
    log.info("Installing collections, roles from requirements.yml")
    
    try:
        session.run("ansible-galaxy", "collection", "install", "-r", "requirements.yml", "--force")
    except Exception as exc:
        msg = Exception(f"({type(exc)}) Unhandled exception installing Ansible Galaxy requirements from requirements.yml. Details: {exc}")
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