"""Module registry for BeaverSec with caching."""
from importlib.metadata import entry_points
from typing import Dict, Any
from functools import lru_cache

from beaversec.core.base import BaseModule
from beaversec.core.exceptions import ModuleLoadError

@lru_cache(maxsize=1)
def _cached_list_modules() -> Dict[str, Dict[str, str]]:
    eps = entry_points(group="beaversec.modules")
    result = {}
    for ep in eps:
        try:
            module_class = ep.load()
            instance = module_class()
            result[ep.name] = {
                "description": getattr(instance, "description", "No description"),
                "version": getattr(instance, "version", "1.0.0"),
            }
        except Exception:
            result[ep.name] = {"description": "Error loading module", "version": "unknown"}
    return result

@lru_cache(maxsize=64)
def _cached_get_module(name: str):
    eps = entry_points(group="beaversec.modules")
    for ep in eps:
        if ep.name == name:
            module_class = ep.load()
            instance = module_class()
            return instance
    raise ModuleLoadError(f"Module '{name}' not found")

class Registry:
    """Registry for loading and managing modules."""
    def __init__(self):
        self._modules: Dict[str, BaseModule] = {}

    def list_modules(self) -> Dict[str, Dict[str, str]]:
        return _cached_list_modules()

    def get_module(self, name: str) -> BaseModule:
        if name in self._modules:
            return self._modules[name]
        try:
            instance = _cached_get_module(name)
            self._modules[name] = instance
            return instance
        except ModuleLoadError:
            raise
        except Exception as e:
            raise ModuleLoadError(f"Failed to load module '{name}': {e}")

    def run_module(self, name: str, params: Dict[str, Any]):
        module = self.get_module(name)
        return module.execute(params)
