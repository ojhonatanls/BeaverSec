#!/bin/bash
# =====================================================
# BeaverSec - Instalação de Dependências
# =====================================================

echo "🦫 BeaverSec - Instalando dependências..."
echo ""

# Verifica Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado!"
    echo "   Instale com: sudo apt install python3"
    exit 1
fi

echo "✅ Python 3 encontrado: $(python3 --version)"

# Verifica pip
if ! command -v pip3 &> /dev/null; then
    echo "ℹ️  Pip3 não encontrado, instalando..."
    sudo apt update
    sudo apt install python3-pip -y
fi

# Instala dependências (se houver)
if [ -f "requirements.txt" ]; then
    echo "📦 Instalando dependências do requirements.txt..."
    pip3 install -r requirements.txt
else
    echo "ℹ️  Nenhum requirements.txt encontrado"
    echo "   BeaverSec usa apenas bibliotecas padrão do Python"
fi

# Configura o projeto
echo ""
echo "🔧 Configurando BeaverSec..."
chmod +x main.py

echo ""
echo "✅ Instalação concluída!"
echo ""
echo "📋 Comandos disponíveis:"
echo "   python3 main.py -l                    # Listar módulos"
echo "   python3 main.py ping_sweep 8.8.8.8    # Ping em IP"
echo "   ./main.py ping_sweep 192.168.1.0/24   # Modo executável"