"""Configuration loader for BeaverSec."""

import yaml
from pathlib import Path

def load_config(path: str) -> dict:
    """Load YAML config from given path."""
    config_file = Path(path)
    if not config_file.exists():
        return {}
    with open(config_file, "r") as f:
        return yaml.safe_load(f) or {}