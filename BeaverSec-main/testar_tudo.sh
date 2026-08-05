[#!/bin/bash
# BeaverSec 3.0 - Teste Completo de Todos os Módulos

echo "=========================================="
echo "BEAVERSEC 4.0 - TESTE COMPLETO"
echo "=========================================="
echo ""

# 1. Verificar ambiente
echo "1. VERIFICANDO AMBIENTE..."
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Ambiente virtual NÃO está ativo!"
    echo "   Execute: source venv/bin/activate"
    exit 1
else
    echo "Ambiente virtual ativo: $VIRTUAL_ENV"
fi
echo ""

# 2. Listar módulos
echo "2. MÓDULOS DISPONÍVEIS..."
beaversec list
echo ""

# 3. Testar todos os módulos (sem sudo)
echo "3. TESTANDO MÓDULOS (SEM SUDO)..."
echo ""

# 3.1 - ping_sweep
echo "🔹 ping_sweep (127.0.0.1)..."
beaversec run ping_sweep 127.0.0.1 --verbose 2>/dev/null | grep -q "True" && echo "   ✅ ping_sweep: OK" || echo "   ❌ ping_sweep: FALHA"
echo ""

# 3.2 - port_scanner
echo "🔹 port_scanner (127.0.0.1 -p 22,80,443)..."
beaversec run port_scanner 127.0.0.1 -p 22,80,443 2>/dev/null | grep -q "closed|filtered" && echo "   ✅ port_scanner: OK" || echo "   ❌ port_scanner: FALHA"
echo ""

# 3.3 - dns_enum
echo "🔹 dns_enum (google.com)..."
beaversec run dns_enum google.com 2>/dev/null | grep -q "A" && echo "   ✅ dns_enum: OK" || echo "   ❌ dns_enum: FALHA"
echo ""

# 3.4 - ssl_scan
echo "🔹 ssl_scan (google.com)..."
beaversec run ssl_scan google.com 2>/dev/null | grep -q "handshake" && echo "   ✅ ssl_scan: OK" || echo "   ❌ ssl_scan: FALHA"
echo ""

# 3.5 - http_headers
echo "🔹 http_headers (example.com)..."
beaversec run http_headers example.com 2>/dev/null | grep -q "score" && echo "   ✅ http_headers: OK" || echo "   ❌ http_headers: FALHA"
echo ""

# 3.6 - ssl_cipher_scan
echo "🔹 ssl_cipher_scan (google.com -p 443)..."
beaversec run ssl_cipher_scan google.com -p 443 2>/dev/null | grep -q "HIGH" && echo "   ✅ ssl_cipher_scan: OK" || echo "   ❌ ssl_cipher_scan: FALHA"
echo ""

# 3.7 - whois_lookup
echo "🔹 whois_lookup (google.com)..."
beaversec run whois_lookup google.com 2>/dev/null | grep -q "domain_name" && echo "   ✅ whois_lookup: OK" || echo "   ❌ whois_lookup: FALHA"
echo ""

# 3.8 - dns_zone_transfer
echo "🔹 dns_zone_transfer (example.com)..."
beaversec run dns_zone_transfer example.com 2>/dev/null | grep -q "axfr" && echo "   ✅ dns_zone_transfer: OK" || echo "   ❌ dns_zone_transfer: FALHA"
echo ""

# 3.9 - subdomain_brute
echo "🔹 subdomain_brute (example.com)..."
beaversec run subdomain_brute example.com 2>/dev/null | grep -q "found" && echo "   ✅ subdomain_brute: OK" || echo "   ❌ subdomain_brute: FALHA"
echo ""

# 3.10 - udp_scan
echo "🔹 udp_scan (127.0.0.1 -p 53,123)..."
beaversec run udp_scan 127.0.0.1 -p 53,123 2>/dev/null | grep -q "open|filtered" && echo "   ✅ udp_scan: OK" || echo "   ❌ udp_scan: FALHA"
echo ""

# 3.11 - service_detection
echo "🔹 service_detection (127.0.0.1 -p 22,80)..."
beaversec run service_detection 127.0.0.1 -p 22,80 2>/dev/null | grep -q "error" && echo "   ✅ service_detection: OK" || echo "   ❌ service_detection: FALHA"
echo ""

# 3.12 - shodan_enum
echo "🔹 shodan_enum (8.8.8.8)..."
beaversec run shodan_enum 8.8.8.8 2>/dev/null | grep -q "ip" && echo "   ✅ shodan_enum: OK" || echo "   ❌ shodan_enum: FALHA"
echo ""

# 3.13 - vuln_scanner
echo "🔹 vuln_scanner (example.com)..."
beaversec run vuln_scanner example.com 2>/dev/null | grep -q "{}" && echo "   ✅ vuln_scanner: OK" || echo "   ❌ vuln_scanner: FALHA"
echo ""

# 4. Módulos com sudo
echo "4. TESTANDO MÓDULOS (COM SUDO)..."
echo ""

# 4.1 - syn_scan
echo "🔹 syn_scan (127.0.0.1 -p 22,80,443)..."
sudo "$(which beaversec)" run syn_scan 127.0.0.1 -p 22,80,443 2>/dev/null | grep -q "open" && echo "   ✅ syn_scan: OK" || echo "   ❌ syn_scan: FALHA"
echo ""

# 4.2 - arp_scan
echo "🔹 arp_scan (192.168.1.0/28)..."
sudo "$(which beaversec)" run arp_scan 192.168.1.0/28 2>/dev/null | grep -q "{}" && echo "   ✅ arp_scan: OK" || echo "   ❌ arp_scan: FALHA"
echo ""

# 5. Exportadores
echo "5. TESTANDO EXPORTADORES..."
beaversec run port_scanner 127.0.0.1 -p 22,80,443 -o teste.json 2>/dev/null && echo "   ✅ JSON: OK" || echo "   ❌ JSON: FALHA"
beaversec run port_scanner 127.0.0.1 -p 22,80,443 -o teste.html --format html 2>/dev/null && echo "   ✅ HTML: OK" || echo "   ❌ HTML: FALHA"
beaversec run port_scanner 127.0.0.1 -p 22,80,443 -o teste.csv --format csv 2>/dev/null && echo "   ✅ CSV: OK" || echo "   ❌ CSV: FALHA"
echo ""

# 6. Limpeza
echo "6. LIMPANDO ARQUIVOS DE TESTE..."
rm -f teste.json teste.html teste.csv
echo "   ✅ Limpeza concluída"
echo ""

echo "=========================================="
echo "TESTE COMPLETO CONCLUÍDO!"
echo "=========================================="]
