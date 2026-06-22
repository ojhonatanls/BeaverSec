"""
Módulo base para todos os scanners do BeaverSec.
"""
import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)


class ModuleInput(BaseModel):
    """Modelo base para entrada de módulos."""
    target: str
    threads: int = 10
    timeout: float = 5.0
    rate_limit: float = 0.1
    proxy: Optional[str] = None
    verbose: bool = False


class ModuleResult(BaseModel):
    """Modelo base para saída de módulos."""
    module: str
    target: str
    success: bool
    data: Dict[str, Any] = {}
    errors: List[str] = []
    duration: float = 0.0


class BaseModule(ABC):
    """Classe abstrata base para todos os módulos."""

    # Atributos de classe que devem ser sobrescritos pelas classes filhas
    name: str = "base"
    description: str = "Módulo base"

    def __init__(self) -> None:
        self._logger = logging.getLogger(f"beaversec.{self.name}")

    @abstractmethod
    def run(self, target: str, **kwargs) -> ModuleResult:
        """Executa o módulo contra o alvo."""
        pass

    def validate_input(self, target: str, **kwargs) -> ModuleInput:
        """Valida e sanitiza a entrada usando Pydantic."""
        try:
            return ModuleInput(target=target, **kwargs)
        except ValidationError as e:
            self._logger.error(f"Entrada inválida: {e}")
            raise ValueError(f"Entrada inválida: {e}")

    def _log_start(self, target: str) -> None:
        self._logger.info(f"Iniciando {self.name} em {target}")

    def _log_end(self, result: ModuleResult) -> None:
        status = "✅" if result.success else "❌"
        self._logger.info(
            f"{status} {self.name} finalizado em {result.duration:.2f}s"
        )
