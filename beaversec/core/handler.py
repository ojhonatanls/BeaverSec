"""
ModuleHandler - Gerencia dinamicamente todos os módulos do BeaverSec
"""
import importlib
import pkgutil
import sys
from typing import Dict, List, Optional, Any
from beaversec import modules as module_pkg
from beaversec.utils.logger import setup_logger

class ModuleHandler:
    """
    Responsável por carregar, listar e executar módulos dinamicamente.
    """
    
    def __init__(self):
        self.logger = setup_logger()
        self.modules: Dict[str, Any] = {}
        self._load_modules()
        self.logger.info(f"{len(self.modules)} módulo(s) carregado(s) com sucesso.")

    def _load_modules(self) -> None:
        """
        Varre a pasta 'modules' e importa dinamicamente todos os arquivos .py
        que possuam uma função 'run(target, verbose=False)'.
        """
        module_paths = list(module_pkg.__path__)
        
        for finder, modname, ispkg in pkgutil.iter_modules(module_paths):
            try:
                full_name = f"{module_pkg.__name__}.{modname}"
                module = importlib.import_module(full_name)
                
                if hasattr(module, 'run') and callable(module.run):
                    self.modules[modname] = module
                    self.logger.debug(f"Módulo carregado: {modname}")
                else:
                    self.logger.warning(f"Módulo '{modname}' ignorado: não possui função 'run()'")
                    
            except Exception as e:
                self.logger.error(f"Erro ao carregar módulo '{modname}': {e}")
                continue

    def list_modules(self) -> List[str]:
        """Retorna lista com os nomes de todos os módulos carregados."""
        return sorted(self.modules.keys())

    def get_module(self, module_name: str) -> Optional[Any]:
        """Retorna o módulo pelo nome, ou None se não existir."""
        return self.modules.get(module_name)

    def run_module(self, module_name: str, target: str, verbose: bool = False) -> Dict[str, Any]:
        """
        Executa um módulo específico e RETORNA o resultado.
        Levanta ModuleNotFoundError se o módulo não existir.
        """
        module = self.get_module(module_name)
        if not module:
            raise ModuleNotFoundError(f"Módulo '{module_name}' não encontrado.")
        
        self.logger.info(f"Executando '{module_name}' contra '{target}'...")
        try:
            # CAPTURA o retorno do módulo
            result = module.run(target, verbose=verbose)
            return result
        except KeyboardInterrupt:
            self.logger.warning("Execução interrompida pelo usuário.")
            raise
        except Exception as e:
            self.logger.error(f"Erro durante execução do módulo '{module_name}': {e}")
            return {"error": str(e)}
