#!/bin/bash
# =====================================================
# BeaverSec - Atualizar do GitHub
# =====================================================

echo "🦫 Atualizando BeaverSec..."
echo ""

# Puxa as atualizações
git pull origin main

# Reconfigura
chmod +x main.py

echo ""
echo "✅ BeaverSec atualizado com sucesso!"
echo ""
echo "📋 Para ver as novidades:"
echo "   python3 main.py -l"