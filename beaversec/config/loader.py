"""Configuration loader for BeaverSec.

This loader now uses the XDG standard config location: ~/.config/beaversec/config.yaml
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional

from beaversec.core.exceptions import ConfigurationError
from beaversec.utils.audit_logger import AuditLogger


class ConfigLoader:
    """
    Loads and validates configuration from multiple sources.

    Priority: Environment variables > Config file (XDG) > Defaults
    """

    DEFAULT_CONFIG_PATH = Path(os.path.expanduser("~")) / ".config" / "beaversec" / "config.yaml"

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize configuration loader.

        Args:
            config_path: Optional path to configuration file
        """
        # If a config_path was explicitly provided, use it. Otherwise use XDG default
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self.logger = AuditLogger.get_logger("config")
        self._config: Dict[str, Any] = {}
        self._loaded = False

    def load(self) -> Dict[str, Any]:
        """
        Load configuration from file and environment.

        Returns:
            Dict[str, Any]: Merged configuration

        Raises:
            ConfigurationError: If configuration is invalid
        """
        if self._loaded:
            return self._config

        # Ensure config dir exists with secure permissions
        try:
            config_dir = self.config_path.parent
            config_dir.mkdir(parents=True, exist_ok=True)
            # set permissions to 700
            os.chmod(str(config_dir), 0o700)
        except Exception:
            # If we cannot create or set permissions, log a warning but continue
            self.logger.warning(f"Could not ensure config directory permissions for {config_dir}")

        # If a config file does not exist, create an empty file with 600 permissions
        if not self.config_path.exists():
            try:
                self.config_path.write_text("# BeaverSec configuration\n")
                os.chmod(str(self.config_path), 0o600)
            except Exception:
                self.logger.warning(f"Could not create default config file at {self.config_path}")

        # Load from file
        config = self._load_file()

        # Apply environment variables
        env_config = self._load_env()

        # Merge configurations
        self._config = self._merge_configs(config, env_config)

        # Validate configuration
        self._validate_config(self._config)

        self._loaded = True
        self.logger.info("Configuration loaded successfully")
        return self._config

    def _load_file(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if not self.config_path.exists():
            self.logger.info(f"Config file not found: {self.config_path}")
            return {}

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML configuration: {e}")

    def _load_env(self) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        config = {}

        # Map environment variables to config keys
        env_map = {
            "BEAVERSCAN_THREADS": "threads",
            "BEAVERSCAN_TIMEOUT": "timeout",
            "BEAVERSCAN_RATE_LIMIT": "rate_limit",
            "BEAVERSCAN_VERBOSE": "verbose",
            "PROXY_URL": "proxy.url",
            "PROXY_USERNAME": "proxy.username",
            "PROXY_PASSWORD": "proxy.password",
            "USE_TOR": "proxy.use_tor",
            "TOR_PROXY": "proxy.tor_proxy",
            "LOG_LEVEL": "log_level",
            "MAX_RESULTS": "max_results",
            "SHODAN_API_KEY": "shodan.api_key",
            "NVD_API_KEY": "nvd.api_key",
            "SECURITYTRAILS_API_KEY": "securitytrails.api_key",
        }

        for env_key, config_key in env_map.items():
            value = os.getenv(env_key)
            if value is not None:
                self._set_nested(config, config_key, self._parse_value(value))

        return config

    def _parse_value(self, value: str) -> Any:
        """Parse environment variable value."""
        # Boolean
        if value.lower() in ("true", "false"):
            return value.lower() == "true"

        # Integer
        try:
            return int(value)
        except ValueError:
            pass

        # Float
        try:
            return float(value)
        except ValueError:
            pass

        # String (default)
        return value

    def _set_nested(self, config: Dict, key: str, value: Any) -> None:
        """Set nested dictionary value."""
        keys = key.split(".")
        current = config

        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        current[keys[-1]] = value

    def _merge_configs(self, base: Dict, override: Dict) -> Dict:
        """Deep merge two configuration dictionaries."""
        result = base.copy()

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value

        return result

    def _validate_config(self, config: Dict[str, Any]) -> None:
        """Validate configuration values."""
        # Check required sections
        required_sections = ["threads", "timeout", "rate_limit"]
        for section in required_sections:
            if section not in config:
                self.logger.warning(f"Config missing '{section}', using default")

        # Validate numeric values
        if "threads" in config:
            try:
                threads = int(config["threads"])
                if threads < 1 or threads > 100:
                    raise ConfigurationError(f"Invalid threads value: {threads}")
            except (ValueError, TypeError):
                raise ConfigurationError("Invalid threads value, must be integer")

        if "timeout" in config:
            try:
                timeout = float(config["timeout"])
                if timeout <= 0:
                    raise ConfigurationError(f"Invalid timeout value: {timeout}")
            except (ValueError, TypeError):
                raise ConfigurationError("Invalid timeout value, must be number")

        if "rate_limit" in config:
            try:
                rate_limit = float(config["rate_limit"])
                if rate_limit <= 0:
                    raise ConfigurationError(f"Invalid rate_limit value: {rate_limit}")
            except (ValueError, TypeError):
                raise ConfigurationError("Invalid rate_limit value, must be number")
