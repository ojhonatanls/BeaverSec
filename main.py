#!/usr/bin/env python3
"""
BeaverSec - B.E.A.V.E.R.
Binary Enumeration & Advanced Vulnerability Exploitation Recon

Ponto de entrada principal da ferramenta.
Uso: python main.py <módulo> <alvo> [opções]
"""
import sys
import argparse
from beaversec.core.handler import ModuleHandler
from beaversec.utils.logger import setup_logger

__version__ = "0.1.0"

def main() -> int:
    logger = setup_logger()
    
    parser = argparse.ArgumentParser(
        prog="beaver",
        description="🦫 BeaverSec - Canivete suíço para cibersegurança",
        epilog=f"Exemplo: python main.py ping_sweep 192.168.1.0/24 -v\nVersão: {__version__}",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "module",
        help="Nome do módulo a ser executado (ex: ping_sweep)"
    )
    
    parser.add_argument(
        "target",
        help="Alvo: IP (8.8.8.8), domínio (example.com) ou CIDR (192.168.1.0/24)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Ativa modo verboso (mostra detalhes da execução)"
    )
    
    parser.add_argument(
        "-l", "--list",
        action="store_true",
        help="Lista todos os módulos disponíveis e sai"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"BeaverSec {__version__}"
    )
    
    args = parser.parse_args()
    
    if args.list:
        handler = ModuleHandler()
        modules = handler.list_modules()
        
        if modules:
            print("\n📦 MÓDULOS DISPONÍVEIS:")
            for name in modules:
                print(f"   - {name}")
            print(f"\nTotal: {len(modules)} módulo(s)\n")
        else:
            print("\n⚠️ Nenhum módulo encontrado.\n")
        return 0
    
    try:
        handler = ModuleHandler()
        handler.run_module(args.module, args.target, verbose=args.verbose)
        return 0
        
    except ModuleNotFoundError as e:
        logger.error(str(e))
        print("\n💡 Dica: Use '-l' para listar os módulos disponíveis.\n")
        return 1
        
    except KeyboardInterrupt:
        logger.warning("Execução interrompida pelo usuário (Ctrl+C).")
        return 130
        
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())