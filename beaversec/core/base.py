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

    # Legacy compatibility for modules that still use run()
    def run(self, **kwargs) -> ModuleResult:
        """Legacy run method for backward compatibility."""
        return self.execute(kwargs)
    """
Base module definitions for BeaverSec modules.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ModuleResult(BaseModel):
    """Resultado padrão retornado por um módulo."""
    module: str = Field(..., description="Nome do módulo")
    target: str = Field(..., description="Alvo escaneado")
    success: bool = Field(default=True, description="Indica se a execução foi bem-sucedida")
    data: Dict[str, Any] = Field(default_factory=dict, description="Dados do resultado")
    error: Optional[str] = Field(default=None, description="Mensagem de erro se houver")


class BaseModule(ABC):
    """Classe base para todos os módulos do BeaverSec."""
    
    name: str = ""
    description: str = ""
    
    @abstractmethod
    async def run(self, **kwargs) -> ModuleResult:
        """Executa o módulo com os argumentos fornecidos."""
        pass