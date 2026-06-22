#!/usr/bin/env python3
"""
main.py

Entrada principal robusta e completa:
- Lista módulos
- Executa módulo solicitado
- Salva saída JSON quando solicitado
- Uso de logger centralizado
- Tratamento de exceções para módulos ausentes / falhas
"""
import sys
import argparse
import json
import importlib
import pkgutil
from typing import Any
from beaversec.utils.logger import setup_logger, get_logger

__version__ = "0.1.0"

# Observação: ModuleHandler foi usado no original; caso exista, você pode usar
# a classe ModuleHandler em vez do import dinâmico abaixo. Aqui eu faço
# carregamento dinâmico de módulos em ./modules e beaversec/modules.

MODULE_SEARCH_PATHS = ["modules", "beaversec.modules"]

def _list_available_modules():
    """Lista todos os módulos disponíveis."""
    available = set()
    for base in MODULE_SEARCH_PATHS:
        try:
            pkg = importlib.import_module(base)
            if hasattr(pkg, "__path__"):
                for finder, name, ispkg in pkgutil.iter_modules(pkg.__path__):
                    available.add(name)
        except Exception:
            continue
    return available

def _import_module_by_name(name: str):
    """
    Tenta importar módulo por nome procurando em MODULE_SEARCH_PATHS.
    O módulo deve expor uma função run(target, **kwargs).
    """
    for base in MODULE_SEARCH_PATHS:
        mod_name = f"{base}.{name}"
        try:
            mod = importlib.import_module(mod_name)
            return mod
        except Exception as e:
            continue
    
    # último recurso: tentar import direto (se usuário passou caminho completo)
    try:
        return importlib.import_module(name)
    except Exception:
        raise ModuleNotFoundError(f"Módulo '{name}' não encontrado em {MODULE_SEARCH_PATHS}")

def print_result(result):
    """Imprime resultado formatado."""
    if isinstance(result, dict):
        print("\n📊 RESULTADO:")
        if 'error' in result:
            print(f"  ❌ {result['error']}")
        else:
            for key, value in result.items():
                if isinstance(value, dict):
                    print(f"  {key}:")
                    for k, v in value.items():
                        print(f"    {k}: {v}")
                elif isinstance(value, list):
                    print(f"  {key}: {len(value)} itens")
                    for item in value[:5]:
                        print(f"    - {item}")
                    if len(value) > 5:
                        print(f"    ... e mais {len(value)-5} itens")
                else:
                    print(f"  {key}: {value}")

def main() -> int:
    logger = setup_logger()
    log = get_logger()

    parser = argparse.ArgumentParser(
        prog="beaver",
        description="🦫 BeaverSec - Canivete suíço para cibersegurança",
        epilog=f"Exemplo: python main.py list\nExemplo: python main.py ssl_scan example.com -v\nVersão: {__version__}",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("module", nargs="?", default=None, help="Nome do módulo a ser executado (ex: ping_sweep)")
    parser.add_argument("target", nargs="?", default=None, help="Alvo: IP, domínio ou CIDR")
    parser.add_argument("-v", "--verbose", action="store_true", help="Ativa modo verboso")
    parser.add_argument("-l", "--list", action="store_true", help="Lista todos os módulos disponíveis e sai")
    parser.add_argument("-o", "--output", help="Salva o resultado em um arquivo (formato JSON)")
    parser.add_argument("--version", action="version", version=f"BeaverSec {__version__}")

    args = parser.parse_args()

    # Verifica se é comando list ou se "list" foi passado como módulo
    if args.list or args.module == "list":
        available = _list_available_modules()
        if available:
            print("\n📦 MÓDULOS DISPONÍVEIS:")
            for name in sorted(available):
                print(f"   - {name}")
            print(f"\nTotal: {len(available)} módulo(s)\n")
        else:
            print("\n⚠️ Nenhum módulo encontrado.\n")
        return 0

    # Se nenhum módulo foi fornecido, exibe ajuda
    if not args.module:
        parser.print_help()
        return 1

    # Se há módulo, target é obrigatório
    if not args.target:
        print("⚠️ Você deve fornecer um alvo (target) ao executar um módulo.")
        print(f"Exemplo: python main.py {args.module} 192.168.1.1")
        return 2

    try:
        mod = _import_module_by_name(args.module)
    except ModuleNotFoundError as e:
        print(f"[-] {str(e)}")
        available = _list_available_modules()
        print(f"\n📦 Módulos disponíveis: {', '.join(sorted(available))}")
        return 3
    except Exception as e:
        print(f"[-] Erro ao carregar módulo '{args.module}': {e}")
        return 4

    # Executa o módulo: espera-se função run(target, **kwargs)
    try:
        run_fn = getattr(mod, "run", None)
        if not callable(run_fn):
            print(f"[-] Módulo '{args.module}' não implementa 'run(target, **kwargs)'.")
            return 5

        kwargs = {"verbose": args.verbose}
        result = run_fn(args.target, **kwargs)

        # Use central output helper to print result consistently
        if result is not None:
            if isinstance(result, dict):
                print_result(result)
            else:
                # fallback: simple print
                print(result)

        # Salvar como JSON se solicitado
        if args.output:
            try:
                with open(args.output, "w", encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2, default=str)
                print(f"\n✅ Resultado salvo em: {args.output}")
            except Exception as e:
                print(f"[-] Falha ao salvar arquivo '{args.output}': {e}")

        return 0

    except Exception as e:
        log.exception("Erro executando módulo")
        print(f"[-] Erro executando módulo '{args.module}': {e}")
        return 10

if __name__ == "__main__":
    sys.exit(main())
