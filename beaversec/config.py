"""beaversec.config

Config loader for beaversec. Reads config.yaml from repository root by default.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict

import yaml

logger = logging.getLogger(__name__)

_DEFAULT_PATH = Path("config.yaml")


def get_config(path: Path | str | None = None) -> Dict[str, Any]:
    """Load YAML configuration and return as dict.

    Args:
        path: Optional path to config.yaml. Defaults to ./config.yaml.

    Returns:
        Configuration dictionary (empty dict on error).
    """
    p = Path(path) if path else _DEFAULT_PATH
    if not p.exists():
        logger.debug("Config file %s not found, returning empty config", p)
        return {}
    try:
        with p.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
            return dict(data)
    except Exception as exc:  # pragma: no cover - safety fallback
        logger.exception("Failed to load config: %s", exc)
        return {}
