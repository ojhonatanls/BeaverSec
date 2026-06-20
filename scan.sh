#!/bin/bash
# =====================================================
# BeaverSec - Script de Varredura Rápida
# =====================================================

echo "🦫 BeaverSec - Scanner Rápido"
echo "================================"
echo ""

# Função para mostrar uso
show_usage() {
    echo "Uso: ./scan.sh <IP>"
    echo "  ./scan.sh 8.8.8.8"
    echo "  ./scan.sh 192.168.1.0/24"
    echo "  ./scan.sh 8.8.8.8 -v    (modo detalhado)"
}

# Verifica se passou argumento
if [ $# -eq 0 ]; then
    echo "❌ Erro: Nenhum alvo especificado!"
    show_usage
    exit 1
fi

# Executa o comando
echo "🔍 Escaneando: $1"
echo ""

# Verifica se o módulo ping_sweep existe
if [ -f "beaversec/modules/ping_sweep.py" ]; then
    python3 main.py ping_sweep "$@"
else
    echo "❌ Erro: Módulo ping_sweep não encontrado!"
    echo "💡 Execute 'python3 main.py -l' para listar módulos disponíveis"
    exit 1
fi