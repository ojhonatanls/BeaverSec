"""Base module system for BeaverSec framework."""

import importlib
import inspect
import pkgutil
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Type
from pathlib import Path

# Try to use importlib.metadata for entry points (py3.8+). Fallback to pkg_resources
try:
    from importlib.metadata import entry_points  # type: ignore
except Exception:  # pragma: no cover - runtime fallback
    try:
        import pkg_resources  # type: ignore
    except Exception:
        pkg_resources = None
    entry_points = None  # type: ignore

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

    def _load_entrypoint_modules(self) -> Dict[str, Type[BaseModule]]:
        """Load modules registered as setuptools entry points (beaversec.modules).

        Returns mapping name -> module class (or adapter class wrapping callables).
        """
        discovered: Dict[str, Type[BaseModule]] = {}

        # Prefer importlib.metadata.entry_points when available
        if entry_points is not None:
            try:
                # Newer API supports group= parameter
                eps = entry_points(group="beaversec.modules")  # type: ignore
            except TypeError:
                # Older API: get all and filter by .group attribute
                all_eps = entry_points()  # type: ignore
                eps = [ep for ep in all_eps if getattr(ep, "group", None) == "beaversec.modules"]

            for ep in eps:
                name = ep.name
                try:
                    obj = ep.load()
                    # If it's a class subclassing BaseModule, keep it
                    if inspect.isclass(obj) and issubclass(obj, BaseModule):
                        discovered[name] = obj
                    elif callable(obj):
                        # Wrap callables (legacy run() functions) into adapter classes
                        def make_adapter(func, public_name):
                            class FuncAdapter(BaseModule):
                                def __init__(self):
                                    super().__init__()
                                    self.name = public_name
                                    self._func = func

                                def validate_params(self, params: Dict[str, Any]) -> bool:  # pragma: no cover - simple passthrough
                                    return True

                                def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
                                    # Attempt to call common signatures: run(target, **kwargs) or run(**params)
                                    try:
                                        if isinstance(params, dict) and "target" in params:
                                            result = self._func(params["target"], **{k: v for k, v in params.items() if k != "target"})
                                        else:
                                            result = self._func(**params) if isinstance(params, dict) else self._func(params)
                                        # Normalize result to a dict-ish response
                                        if result is None:
                                            return {"success": True}
                                        if isinstance(result, dict):
                                            return result
                                        return {"result": result}
                                    except Exception as e:
                                        raise ModuleExecutionError(str(e))

                            return FuncAdapter

                        adapter = make_adapter(obj, name)
                        discovered[name] = adapter
                    else:
                        self.logger.warning(f"Entry point {name} loaded but is not callable or class")
                except Exception as e:
                    self.logger.error(f"Failed to load entry point {name}: {e}")

            return discovered

        # Fallback to pkg_resources if available
        if pkg_resources is not None:
            try:
                for ep in pkg_resources.iter_entry_points(group="beaversec.modules"):
                    name = ep.name
                    try:
                        obj = ep.load()
                        if inspect.isclass(obj) and issubclass(obj, BaseModule):
                            discovered[name] = obj
                        elif callable(obj):
                            # same adapter as above
                            def make_adapter(func, public_name):
                                class FuncAdapter(BaseModule):
                                    def __init__(self):
                                        super().__init__()
                                        self.name = public_name
                                        self._func = func

                                    def validate_params(self, params: Dict[str, Any]) -> bool:
                                        return True

                                    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
                                        try:
                                            if isinstance(params, dict) and "target" in params:
                                                result = self._func(params["target"], **{k: v for k, v in params.items() if k != "target"})
                                            else:
                                                result = self._func(**params) if isinstance(params, dict) else self._func(params)
                                            if result is None:
                                                return {"success": True}
                                            if isinstance(result, dict):
                                                return result
                                            return {"result": result}
                                        except Exception as e:
                                            raise ModuleExecutionError(str(e))

                                return FuncAdapter

                            adapter = make_adapter(obj, name)
                            discovered[name] = adapter
                        else:
                            self.logger.warning(f"Entry point {name} loaded but is not callable or class")
                    except Exception as e:
                        self.logger.error(f"Failed to load entry point {name}: {e}")
            except Exception:
                pass

        return discovered

    def discover_modules(self) -> Dict[str, Type[BaseModule]]:
        """
        Discover all available modules either via entry points or by scanning the
        modules directory. Entry points are preferred; directory scanning is used
        as a fallback for development installs.

        Returns:
            Dict[str, Type[BaseModule]]: Dictionary of module classes
        """
        discovered: Dict[str, Type[BaseModule]] = {}

        # First try entry points
        try:
            ep_modules = self._load_entrypoint_modules()
            discovered.update(ep_modules)
        except Exception as e:
            self.logger.debug(f"Entry point discovery failed: {e}")

        # Fallback: scan modules directory for classes not already provided by entry points
        module_dir = self.module_path

        if not module_dir.exists():
            if discovered:
                return discovered
            self.logger.warning(f"Modules directory not found: {module_dir}")
            return discovered

        # Use Path object for module discovery
        for module_info in pkgutil.iter_modules([str(module_dir)]):
            module_name = module_info.name
            # If already discovered via entry points, skip
            if module_name in discovered:
                continue

            try:
                module = importlib.import_module(f"beaversec.modules.{module_name}")
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if (issubclass(obj, BaseModule) and obj != BaseModule and not inspect.isabstract(obj)):
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
            module_class = discovered[module_name]
            try:
                module_instance = module_class()
            except Exception as e:
                self.logger.error(f"Failed to instantiate module {module_name}: {e}")
                return None
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
        result: Dict[str, Dict[str, Any]] = {}

        for name, module_class in discovered.items():
            try:
                # Create temporary instance to get info
                temp_instance = module_class()
                result[name] = temp_instance.get_info()
            except Exception as e:
                self.logger.error(f"Error getting info for {name}: {e}")

        return result
