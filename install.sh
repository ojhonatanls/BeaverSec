# Top-level install.sh now delegates to scripts/install.sh (if present)
#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/scripts/install.sh" ]; then
    echo "🔧 Executando scripts/install.sh..."
    bash "$SCRIPT_DIR/scripts/install.sh" "$@"
    exit $?
fi

# Fallback: simple environment check
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado"
    exit 1
fi

echo "⚠️ scripts/install.sh não encontrado. Crie scripts/install.sh para instalação avançada."
exit 0
