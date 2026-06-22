#!/usr/bin/env bash
set -euo pipefail

# scripts/install.sh - cria venv e instala o pacote (incluindo deps do pyproject.toml)
PY=${PY:-python3}
VENV_DIR=${VENV_DIR:-.venv}

echo "🦫 BeaverSec - criando ambiente virtual em $VENV_DIR"
$PY -m venv "$VENV_DIR"
# shellcheck disable=SC1090
source "$VENV_DIR/bin/activate"

echo "📦 Atualizando pip e instalando o pacote em modo editável"
pip install --upgrade pip
# instala dependências declaradas em pyproject.toml (via setuptools/pep517)
pip install -e . || true

# Caso ainda haja requirements.txt, instale como fallback
if [ -f "requirements.txt" ]; then
    echo "📦 Instalando requirements.txt (fallback)"
    pip install -r requirements.txt || true
fi

echo "✅ Ambiente pronto. Ative com: source $VENV_DIR/bin/activate"
echo "Para rodar testes: pytest -q"
