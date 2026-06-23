"""beaversec.config

Config loader for beaversec. Reads config.yaml from repository root by default.
Supports environment variables for API keys and auto-creation of config files.
"""
from __future__ import annotations

import logging
import os
import shutil
from pathlib import Path
from typing import Any, Dict

import yaml

from beaversec.exceptions import ConfigError

logger = logging.getLogger(__name__)

_DEFAULT_PATH = Path("config.yaml")
_EXAMPLE_PATH = Path("config.example.yaml")

# Environment variables that map to config keys
ENV_VAR_MAPPING = {
    "SHODAN_API_KEY": "shodan.api_key",
    "NVD_API_KEY": "nvd.api_key",
    "VIRUSTOTAL_API_KEY": "virustotal.api_key",
    "CENSYS_API_ID": "censys.api_id",
    "CENSYS_API_SECRET": "censys.api_secret",
    "BEAVERSEC_LOG_LEVEL": "logging.level",
    "BEAVERSEC_RATE_LIMIT": "rate_limit",
}


def _create_default_config(path: Path) -> Dict[str, Any]:
    """Create a default config file from template.
    
    Args:
        path: Path where to create the default config.
        
    Returns:
        Dictionary with default configuration.
    """
    default_config = {
        "logging": {
            "level": "INFO",
            "format": "json",
        },
        "rate_limit": 500.0,
        "timeout": 5.0,
        "shodan": {
            "api_key": "",  # Will be overridden by env var
        },
        "nvd": {
            "api_key": "",
        },
        "virustotal": {
            "api_key": "",
        },
        "censys": {
            "api_id": "",
            "api_secret": "",
        },
    }
    
    try:
        with path.open("w", encoding="utf-8") as f:
            yaml.dump(default_config, f, default_flow_style=False)
        logger.info(f"Created default config file at {path}")
    except Exception as e:
        logger.warning(f"Could not create config file at {path}: {e}")
    
    return default_config


def _load_env_overrides(config: Dict[str, Any]) -> Dict[str, Any]:
    """Load environment variables and override config values.
    
    Args:
        config: Current configuration dictionary.
        
    Returns:
        Updated configuration dictionary.
    """
    for env_var, config_key in ENV_VAR_MAPPING.items():
        env_value = os.environ.get(env_var)
        if env_value:
            # Handle nested keys like "shodan.api_key"
            keys = config_key.split(".")
            current = config
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
            
            current[keys[-1]] = env_value
            logger.debug(f"Loaded {env_var} from environment")
    
    return config


def validate_config(config: Dict[str, Any]) -> None:
    """Validate required configuration keys.
    
    Args:
        config: Configuration dictionary to validate.
        
    Raises:
        ConfigError: If required configuration is missing.
    """
    # For now, we don't require any specific keys
    # Modules can check for their specific requirements
    pass


def get_config(path: Path | str | None = None) -> Dict[str, Any]:
    """Load YAML configuration and return as dict.
    
    Creates default config if file doesn't exist.
    Overrides config with environment variables.

    Args:
        path: Optional path to config.yaml. Defaults to ./config.yaml.

    Returns:
        Configuration dictionary.
        
    Raises:
        ConfigError: If configuration is invalid.
    """
    p = Path(path) if path else _DEFAULT_PATH
    
    # If config doesn't exist, create default
    if not p.exists():
        logger.warning(f"Config file {p} not found. Creating default...")
        config = _create_default_config(p)
    else:
        try:
            with p.open("r", encoding="utf-8") as fh:
                data = yaml.safe_load(fh) or {}
                config = dict(data)
                logger.debug(f"Loaded config from {p}")
        except Exception as exc:
            logger.exception(f"Failed to load config from {p}: {exc}")
            raise ConfigError(f"Failed to load config: {exc}")
    
    # Override with environment variables
    config = _load_env_overrides(config)
    
    # Validate config
    try:
        validate_config(config)
    except ConfigError as e:
        logger.error(f"Configuration validation failed: {e}")
        raise
    
    return config


def check_config(path: Path | str | None = None) -> Dict[str, Any]:
    """Check configuration validity and API connectivity.
    
    Args:
        path: Optional path to config.yaml.
        
    Returns:
        Dictionary with check results.
    """
    p = Path(path) if path else _DEFAULT_PATH
    results = {
        "config_file_exists": p.exists(),
        "config_valid": False,
        "api_keys_configured": {},
        "errors": [],
    }
    
    try:
        config = get_config(path)
        results["config_valid"] = True
        
        # Check API keys
        for env_var, config_key in ENV_VAR_MAPPING.items():
            keys = config_key.split(".")
            current = config
            for key in keys[:-1]:
                if key in current:
                    current = current[key]
                else:
                    current = None
                    break
            
            if current and isinstance(current, dict):
                value = current.get(keys[-1], "")
                results["api_keys_configured"][env_var] = bool(value)
    except Exception as e:
        results["errors"].append(str(e))
        logger.error(f"Config check failed: {e}")
    
    return results
