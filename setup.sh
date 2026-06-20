#!/bin/bash
# =====================================================
# BeaverSec - Script de Configuração Rápida
# =====================================================

echo "🦫 Configurando BeaverSec..."

# 1. Dá permissão de execução
chmod +x main.py
echo "✅ main.py agora é executável"

# 2. Cria alias permanente
if ! grep -q "alias beaver=" ~/.bashrc; then
    echo "alias beaver='python3 $(pwd)/main.py'" >> ~/.bashrc
    echo "✅ Alias 'beaver' adicionado ao .bashrc"
else
    echo "ℹ️  Alias 'beaver' já existe"
fi

# 3. Instala globalmente (opcional)
read -p "❓ Deseja instalar globalmente? (s/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    sudo ln -sf $(pwd)/main.py /usr/local/bin/beaver
    echo "✅ BeaverSec instalado globalmente!"
fi

echo ""
echo "🎉 Configuração concluída!"
echo ""
echo "📋 Agora você pode usar:"
echo "   beaver -l                    # Listar módulos"
echo "   beaver ping_sweep 8.8.8.8    # Ping em IP"
echo "   beaver ping_sweep 192.168.1.0/24 -v  # Varredura detalhada"
echo ""
echo "🔄 Reinicie o terminal ou execute: source ~/.bashrc"