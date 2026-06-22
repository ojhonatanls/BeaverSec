"""
Exportador para formato CSV.
"""
import csv
import logging
from pathlib import Path
from typing import List

from beaversec.core.base_module import ModuleResult

logger = logging.getLogger(__name__)


class CSVExporter:
    """Exporta resultados para formato CSV."""

    def export(self, results: List[ModuleResult], output_file: str) -> None:
        """Exporta uma lista de ModuleResult para um arquivo CSV."""
        if not results:
            logger.warning("Nenhum resultado para exportar")
            return

        # Garante que o diretório existe
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            # Define os cabeçalhos
            fieldnames = ['module', 'target', 'success', 'duration', 'data', 'errors']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for result in results:
                writer.writerow({
                    'module': result.module,
                    'target': result.target,
                    'success': result.success,
                    'duration': f"{result.duration:.2f}",
                    'data': str(result.data),
                    'errors': '; '.join(result.errors) if result.errors else ''
                })

        logger.info(f"Resultados exportados para {output_file}")
