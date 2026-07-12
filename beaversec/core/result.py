# beaversec/core/result.py
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

@dataclass
class ModuleResult:
    """
    Standard result container for BeaverSec modules.
    """
    success: bool
    data: Optional[Dict[str, Any]] = field(default_factory=dict)
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)