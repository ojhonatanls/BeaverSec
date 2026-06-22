"""
Orquestrador principal do BeaverSec.
"""
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Type

from beaversec.core.base_module import BaseModule, ModuleResult
from beaversec.exporters.csv_exporter import CSVExporter
from beaversec.exporters.html_exporter import HTMLExporter
from beaversec.exporters.json_exporter import JSONExporter

logger = logging.getLogger(__name__)


class Beaver:
    """Classe principal que gerencia módulos e exportação."""

    def __init__(self, verbose: bool = False) -> None:
        self.modules: Dict[str, BaseModule] = {}
        self.results: List[ModuleResult] = []
        self.verbose = verbose
        self._setup_logging()

    def _setup_logging(self) -> None:
        level = logging.DEBUG if self.verbose else logging.INFO
        logging.basicConfig(
            level=level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        # Adiciona handler para arquivo com rotação
        from logging.handlers import RotatingFileHandler

        try:
            Path("logs").mkdir(exist_ok=True)
            fh = RotatingFileHandler(
                "logs/beaversec.log", maxBytes=10_485_760, backupCount=5
            )
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(
                logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
            )
            logging.getLogger().addHandler(fh)
        except Exception:
            pass  # Falha silenciosa se não conseguir criar logs

    def register_module(self, module: BaseModule) -> None:
        """Registra um módulo no orquestrador."""
        self.modules[module.name] = module
        logger.info(f"Módulo registrado: {module.name}")

    def run_module(self, name: str, target: str, **kwargs) -> ModuleResult:
        """Executa um módulo específico."""
        if name not in self.modules:
            raise ValueError(f"Módulo '{name}' não encontrado")

        module = self.modules[name]
        logger.info(f"Executando {name} em {target}")
        start = time.time()
        try:
            result = module.run(target, **kwargs)
            result.duration = time.time() - start
            self.results.append(result)
            return result
        except Exception as e:
            logger.error(f"Erro no módulo {name}: {e}", exc_info=True)
            result = ModuleResult(
                module=name,
                target=target,
                success=False,
                errors=[str(e)],
                duration=time.time() - start,
            )
            self.results.append(result)
            return result

    def export(self, format: str, output: str) -> None:
        """Exporta os resultados no formato especificado."""
        exporters = {
            "json": JSONExporter,
            "csv": CSVExporter,
            "html": HTMLExporter,
            "csv": CSVExporter,
        }
        if format not in exporters:
            raise ValueError(f"Formato '{format}' não suportado")

        exporter = exporters[format]()
        exporter.export(self.results, output)
        logger.info(f"Resultados exportados para {output}")
