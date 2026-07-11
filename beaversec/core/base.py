"""Base module definition for BeaverSec."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

@dataclass
class ModuleResult:
    """Standard result container for module execution."""
    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class BaseModule(ABC):
    """Abstract base class for all BeaverSec modules."""

    name: str = ""
    description: str = ""
    version: str = "1.0.0"

    @abstractmethod
    def execute(self, params: Dict[str, Any]) -> ModuleResult:
        """Execute the module with given parameters.

        Args:
            params: Dictionary containing module parameters (target, port, etc.)

        Returns:
            ModuleResult object with execution results.
        """
        pass

    def validate_params(self, params: Dict[str, Any]) -> bool:
        """Validate input parameters. Override for custom validation."""
        return "target" in params