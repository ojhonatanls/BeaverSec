"""BeaverSec - Modular Offensive Security Framework."""

__version__ = "4.0.0"

from beaversec.core.base import BaseModule
from beaversec.core.exceptions import BeaverSecError, ModuleLoadError, ValidationError

__all__ = [
    "__version__",
    "BaseModule",
    "BeaverSecError",
    "ModuleLoadError",
    "ValidationError",
]