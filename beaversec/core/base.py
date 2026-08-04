"""Base module definition for BeaverSec."""

from abc import ABC, abstractmethod
from typing import Dict, Any
from beaversec.core.result import ModuleResult

class BaseModule(ABC):
    """Abstract base class for all BeaverSec modules."""

    name: str = ""
    description: str = ""
    version: str = "1.0.0"

    @abstractmethod
    def execute(self, params: Dict[str, Any]) -> ModuleResult:
        """Execute the module with given parameters."""
        pass

    def validate_params(self, params: Dict[str, Any]) -> bool:
        return "target" in params
