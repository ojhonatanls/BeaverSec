"""Base module system for BeaverSec framework."""

import importlib
import inspect
import pkgutil
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Type
from pathlib import Path

from beaversec.core.security import SecurityContext
from beaversec.core.exceptions import ModuleNotFoundError, ModuleExecutionError
from beaversec.utils.audit_logger import AuditLogger
from beaversec.utils.credential_manager import CredentialManager
from beaversec.utils.rate_limiter import RateLimiter


class BaseModule(ABC):
    """
    Abstract base class for all BeaverSec modules.

    Attributes:
        name: Module identifier
        description: Human-readable module description
        version: Module version string
        security_context: Security validation context
        rate_limiter: Rate limiting instance for module operations
    """

    def __init__(self):
        """Initialize the module with security context."""
        self.name = self.__class__.__name__
        self.description = self.__doc__ or "No description provided"
        self.version = "1.0.0"
        self.security_context = SecurityContext()
        self.credential_manager = CredentialManager()
        self.rate_limiter = RateLimiter()
        self.logger = AuditLogger.get_logger(self.name)

    @abstractmethod
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the module with validated parameters.

        Args:
            params: Dictionary of validated parameters

        Returns:
            Dict[str, Any]: Module execution results

        Raises:
            ModuleExecutionError: If execution fails
            ValidationError: If parameters are invalid
        """
        pass

    @abstractmethod
    def validate_params(self, params: Dict[str, Any]) -> bool:
        """
        Validate module parameters before execution.

        Args:
            params: Parameters to validate

        Returns:
            bool: True if valid, False otherwise

        Raises:
            ValidationError: If parameters are invalid
        """
        pass

    def get_info(self) -> Dict[str, Any]:
        """
        Get module metadata information.

        Returns:
            Dict[str, Any]: Module metadata
        """
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "module_class": self.__class__.__name__,
        }


class ModuleManager:
    """
    Manages module discovery, loading, and execution.

    Attributes:
        modules: Dictionary of loaded modules
        module_path: Path to modules directory
    """

    def __init__(self):
        """Initialize the module manager."""
        self.modules: Dict[str, BaseModule] = {}
        self.module_path = Path(__file__).parent.parent / "modules"
        self.logger = AuditLogger.get_logger("module_manager")

    def discover_modules(self) -> Dict[str, Type[BaseModule]]:
        """
        Discover all available modules in the modules directory.

        Returns:
            Dict[str, Type[BaseModule]]: Dictionary of module classes
        """
        discovered = {}
        module_dir = self.module_path

        if not module_dir.exists():
            self.logger.warning(f"Modules directory not found: {module_dir}")
            return discovered

        # Use Path object for module discovery
        for module_info in pkgutil.iter_modules([str(module_dir)]):
            module_name = module_info.name

            try:
                module = importlib.import_module(
                    f"beaversec.modules.{module_name}"
                )
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if (issubclass(obj, BaseModule) and
                            obj != BaseModule and
                            not inspect.isabstract(obj)):
                        discovered[name] = obj
            except Exception as e:
                self.logger.error(f"Failed to load module {module_name}: {e}")

        return discovered

    def get_module(self, module_name: str) -> Optional[BaseModule]:
        """
        Get a module instance by name.

        Args:
            module_name: Name of the module to retrieve

        Returns:
            Optional[BaseModule]: Module instance or None if not found
        """
        if module_name in self.modules:
            return self.modules[module_name]

        discovered = self.discover_modules()
        if module_name in discovered:
            module_instance = discovered[module_name]()
            self.modules[module_name] = module_instance
            return module_instance

        return None

    def list_modules(self) -> Dict[str, Dict[str, Any]]:
        """
        List all available modules with their metadata.

        Returns:
            Dict[str, Dict[str, Any]]: Module metadata dictionary
        """
        discovered = self.discover_modules()
        result = {}

        for name, module_class in discovered.items():
            try:
                # Create temporary instance to get info
                temp_instance = module_class()
                result[name] = temp_instance.get_info()
            except Exception as e:
                self.logger.error(f"Error getting info for {name}: {e}")

        return result
