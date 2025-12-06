import logging
import os
from typing import Any

import yaml


def load_config(path: str) -> dict[str, Any]:
    with open(path, "r", encoding="ascii") as cfg_file:
        return yaml.safe_load(cfg_file)


def resolve_env_placeholders(config: dict[str, Any]) -> dict[str, Any]:
    resolved = dict(config)
    if "postgres" in resolved:
        resolved["postgres"] = {
            key: os.getenv(key.upper(), value)
            for key, value in resolved["postgres"].items()
        }
    return resolved


def setup_logging(level: str | int = "INFO") -> None:
    numeric_level = getattr(logging, str(level).upper(), logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
