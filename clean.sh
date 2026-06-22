#!/bin/bash
# BeaverSec Cleaner - Limpa caches e arquivos temporários

echo "🧹 Limpando caches e lixos do projeto BeaverSec..."

# Remove caches do Python
rm -rf __pycache__/ .pytest_cache/ .mypy_cache/ .ruff_cache/
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
find . -type f -name "*.pyo" -delete 2>/dev/null

# Remove arquivos temporários do VSCode
rm -rf .vscode/.ropeproject/ .vscode/*.code-workspace

# Remove logs e relatórios antigos
rm -rf logs/ *.log *.html *.json report.html 2>/dev/null

# Remove venv (opcional - só se quiser recriar do zero)
# rm -rf venv/

# Remove arquivos temporários do sistema
rm -rf *.tmp *.bak *.swp *.swo 2>/dev/null

echo "✅ Limpeza concluída! Projeto está limpo."

echo ""
echo "📦 Para recriar o ambiente virtual:"
echo "python3 -m venv venv"
echo "source venv/bin/activate"
echo "pip install -r requirements.txt"
