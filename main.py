#!/usr/bin/env python3
"""
BeaverSec - B.E.A.V.E.R.
Binary Enumeration & Advanced Vulnerability Exploitation Recon

Ponto de entrada principal da ferramenta.
Uso: python main.py <módulo> <alvo> [opções]
"""
import sys
import argparse
import json
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
        "-o", "--output",
        help="Salva o resultado em um arquivo (formato JSON)"
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
        # CAPTURA O RESULTADO
        result = handler.run_module(args.module, args.target, verbose=args.verbose)
        
        # EXIBE O RESULTADO FORMATADO
        print("\n" + "="*50)
        print(f"📊 RESULTADO DO MÓDULO: {args.module.upper()}")
        print("="*50)
        
        if isinstance(result, dict):
            # Exibe campos principais
            if "host" in result:
                print(f"Host: {result['host']}")
            if "alive" in result:
                status = "✅ ATIVO" if result['alive'] else "❌ INATIVO"
                print(f"Status: {status}")
            if "rtt" in result and result['rtt'] is not None:
                print(f"Latência: {result['rtt']:.2f}ms")
            if "packet_loss" in result and result['packet_loss'] is not None:
                print(f"Perda de pacotes: {result['packet_loss']}%")
            if "error" in result:
                print(f"❌ Erro: {result['error']}")
            if "output" in result and args.verbose:
                print(f"\n📝 Saída completa:\n{result['output']}")
            # Mostra outras chaves
            for key, value in result.items():
                if key not in ["host", "alive", "rtt", "packet_loss", "error", "output"]:
                    print(f"{key}: {value}")
        else:
            print(result)
        
        # Salva em arquivo se solicitado
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            print(f"\n💾 Resultado salvo em: {args.output}")
        
        print("="*50 + "\n")
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
