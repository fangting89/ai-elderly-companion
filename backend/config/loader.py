"""Loads every YAML file in conf/ into one validated Settings object, and
configures logging as a side effect.
"""

import logging
from pathlib import Path

import yaml

from backend.config.schemas import Settings

CONF_DIR = Path(__file__).resolve().parent.parent.parent / "conf"


# Reads every conf/*.yaml file into one dict, keyed by filename
def _read_conf_dir(conf_dir: Path) -> dict:
    config_dict = {}
    for yaml_file in sorted(conf_dir.glob("*.yaml")):
        with open(yaml_file) as f:
            config_dict[yaml_file.stem] = yaml.safe_load(f) or {}
    return config_dict


# Turns the configured level/destination into an actual logging setup
def _configure_logging(logging_config: dict) -> None:
    handlers: list[logging.Handler] = [logging.StreamHandler()]
    log_file = logging_config.get("log_file", "")
    if log_file:
        log_path = Path(__file__).resolve().parent.parent.parent / log_file
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_path))
    logging.basicConfig(
        level=logging_config.get("level", "INFO"),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        handlers=handlers,
        force=True,
    )


# Loads and validates every conf/*.yaml file into one Settings object
def load_config(conf_dir: Path = CONF_DIR) -> Settings:
    """Load and validate every conf/*.yaml file into one Settings object.

    Also configures logging (level, and an optional log file) from
    conf/logging.yaml, so this is called once, before any other backend
    module runs.

    Args:
        conf_dir: directory containing the config's YAML files.

    Returns:
        Settings: the validated, typed configuration.

    Raises:
        pydantic.ValidationError: if a YAML file is missing a required
            field or has a value of the wrong type.
    """
    config_dict = _read_conf_dir(conf_dir)
    _configure_logging(config_dict.get("logging", {}))
    return Settings(**config_dict)
