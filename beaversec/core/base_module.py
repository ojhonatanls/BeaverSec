"""beaversec/core/base_module.py

Base abstract class for modules.
Provides standardized run() flow, logging and result saving.
"""
from __future__ import annotations

import json
import logging
import os
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional


class ModuleExecutionError(Exception):
    """Raised when a module fails in an unrecoverable way."""


class BaseModule(ABC):
    """Abstract base for BeaverSec modules.

    Subclasses must implement validate_target, execute and format_output.
    The concrete run() method orchestrates validation, execution, formatting
    and produces a standardized dictionary output.
    """

    def __init__(self, verbose: bool = False, logger: Optional[logging.Logger] = None, data_dir: str = "data") -> None:
        self.verbose = verbose
        self.logger = logger or logging.getLogger("BeaverSec")
        self.data_dir = data_dir
        try:
            os.makedirs(self.data_dir, exist_ok=True)
        except Exception:
            # Best-effort: if creation fails, continue without failing modules
            self.logger.debug("Não foi possível criar data_dir '%s'", self.data_dir)

    @abstractmethod
    def validate_target(self, target: str) -> None:
        """Validate and normalize the target.

        Should raise ValueError if the target is invalid.
        """

    @abstractmethod
    def execute(self, target: str, **kwargs) -> Any:
        """Run the core logic of the module and return raw result/data."""

    @abstractmethod
    def format_output(self, raw_result: Any) -> Dict[str, Any]:
        """Convert raw result into structured data serializable to JSON."""

    def log(self, message: str, level: int = logging.INFO) -> None:
        if self.logger:
            self.logger.log(level, message)
        elif self.verbose:
            print(message)

    def save_result(self, result: Dict[str, Any], output_file: Optional[str] = None) -> Optional[str]:
        """Save result to a file inside data_dir or specific output_file.

        Returns the path to the saved file or None if nothing was written.
        """
        if output_file is None:
            # default: save with timestamped filename
            ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
            output_file = os.path.join(self.data_dir, f"{result.get('module_name', 'module')}_{ts}.json")

        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2, default=str)
            self.log(f"Resultado salvo em: {output_file}")
            return output_file
        except Exception as e:
            self.log(f"Falha ao salvar resultado: {e}", level=logging.WARNING)
            return None

    def run(self, target: str, output_file: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """High-level runner used by CLI.

        This method normalizes the execution flow and returns a dict with keys:
        - module_name
        - target
        - status: "success" or "error"
        - data: module-specific structured data (dict)
        - timestamp
        - error: present only on failure
        """
        module_name = getattr(self, "__module_name__", self.__class__.__name__)
        timestamp = datetime.utcnow().isoformat() + "Z"

        try:
            self.validate_target(target)
        except Exception as ex:
            self.log(f"Validação falhou para {target}: {ex}", level=logging.ERROR)
            return {
                "module_name": module_name,
                "target": target,
                "status": "error",
                "data": None,
                "timestamp": timestamp,
                "error": str(ex),
            }

        try:
            raw = self.execute(target, **kwargs)
            data = self.format_output(raw)
            result = {
                "module_name": module_name,
                "target": target,
                "status": "success",
                "data": data,
                "timestamp": timestamp,
            }

            # Optionally save
            if output_file or kwargs.get("save", False):
                self.save_result(result, output_file)

            return result

        except ModuleExecutionError as me:
            self.log(f"Erro na execução do módulo: {me}", level=logging.ERROR)
            return {
                "module_name": module_name,
                "target": target,
                "status": "error",
                "data": None,
                "timestamp": timestamp,
                "error": str(me),
            }
        except Exception as e:
            self.log(f"Exceção inesperada: {e}", level=logging.ERROR)
            return {
                "module_name": module_name,
                "target": target,
                "status": "error",
                "data": None,
                "timestamp": timestamp,
                "error": str(e),
            }
