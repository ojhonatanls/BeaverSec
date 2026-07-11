"""Module registry for BeaverSec."""

from importlib.metadata import entry_points
from typing import Dict, Any, Optional
from beaversec.core.base import BaseModule, ModuleResult
from beaversec.core.exceptions import ModuleLoadError

class Registry:
    """Registry for loading and managing modules."""

    def __init__(self):
        self._modules: Dict[str, BaseModule] = {}

    def list_modules(self) -> Dict[str, Dict[str, str]]:
        """Return a dict of available modules with their metadata."""
        eps = entry_points(group="beaversec.modules")
        result = {}
        for ep in eps:
            try:
                module_class = ep.load()
                # Try to instantiate to get metadata
                instance = module_class()
                result[ep.name] = {
                    "description": getattr(instance, "description", "No description"),
                    "version": getattr(instance, "version", "1.0.0"),
                }
            except Exception:
                result[ep.name] = {"description": "Error loading module", "version": "unknown"}
        return result

    def get_module(self, name: str) -> BaseModule:
        """Load and return a module by name."""
        if name in self._modules:
            return self._modules[name]

        eps = entry_points(group="beaversec.modules")
        for ep in eps:
            if ep.name == name:
                try:
                    module_class = ep.load()
                    instance = module_class()
                    self._modules[name] = instance
                    return instance
                except Exception as e:
                    raise ModuleLoadError(f"Failed to load module '{name}': {e}")

        raise ModuleLoadError(f"Module '{name}' not found")

    def run_module(self, name: str, params: Dict[str, Any]) -> ModuleResult:
        """Execute a module by name with given parameters."""
        module = self.get_module(name)
        return module.execute(params)