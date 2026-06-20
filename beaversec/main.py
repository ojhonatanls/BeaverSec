#!/usr/bin/env python3
"""Ponto de entrada principal do BeaverSec."""

import sys
import argparse
import importlib
from pathlib import Path

def list_modules():
    """Lista os módulos disponíveis."""
    print("📋 Módulos disponíveis:")
    print("  - ping_sweep    - Verifica hosts ativos via ICMP")
    print("  - port_scanner  - Escaneia portas TCP abertas")

def run_module(module_name: str, target: str, args: str = "", **kwargs):
    """Executa um módulo específico."""
    try:
        # Importa o módulo
        module = importlib.import_module(f"beaversec.modules.{module_name}")
        
        # Parse args se for JSON
        parsed_args = {}
        if args:
            try:
                import json
                parsed_args = json.loads(args)
            except:
                # key=value
                for item in args.split():
                    if "=" in item:
                        key, value = item.split("=", 1)
                        parsed_args[key] = value
        
        # Adiciona kwargs
        parsed_args.update(kwargs)
        
        # Executa
        result = module.run(target, **parsed_args)
        
        # Mostra resultado
        print("\n📊 RESULTADO:")
        if isinstance(result, dict):
            for key, value in result.items():
                print(f"  {key}: {value}")
        else:
            print(result)
            
    except ModuleNotFoundError:
        print(f"❌ Módulo '{module_name}' não encontrado")
        list_modules()
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro ao executar: {str(e)}")
        sys.exit(1)

def cli():
    """Interface de linha de comando principal."""
    parser = argparse.ArgumentParser(
        description="BeaverSec - Ferramenta de cibersegurança",
        epilog="Exemplo: beaversec run ping_sweep --target 8.8.8.8"
    )
    
    parser.add_argument(
        "-v", "--version",
        action="version",
        version="BeaverSec v0.2.0"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Comandos")
    
    # list
    subparsers.add_parser("list", help="Lista módulos")
    
    # run
    run_parser = subparsers.add_parser("run", help="Executa módulo")
    run_parser.add_argument("module", help="Nome do módulo")
    run_parser.add_argument("--target", required=True, help="Alvo (IP/domínio)")
    run_parser.add_argument("--args", default="", help="Argumentos (JSON ou key=value)")
    run_parser.add_argument("--verbose", action="store_true", help="Logs detalhados")
    run_parser.add_argument("--timeout", type=int, default=5, help="Timeout em segundos")
    
    args = parser.parse_args()
    
    if args.command == "list":
        list_modules()
    elif args.command == "run":
        run_module(args.module, args.target, args.args, 
                   verbose=args.verbose, timeout=args.timeout)
    else:
        parser.print_help()

if __name__ == "__main__":
    cli()
