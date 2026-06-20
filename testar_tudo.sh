#!/bin/bash
echo "🦫 BeaverSec - Teste completo"
echo "================================"
echo

echo "📡 DNS Enumeration"
python -c "from beaversec.modules import dns_enum; dns_enum.run('google.com')"
echo

echo "🔎 Subdomain Brute Force"
python -c "from beaversec.modules import subdomain_brute; subdomain_brute.run('google.com')"
echo

echo "🌐 HTTP Headers"
python -c "from beaversec.modules import http_headers; http_headers.run('https://google.com')"
echo

echo "🔒 SSL Scan"
python -c "from beaversec.modules import ssl_scan; ssl_scan.run('google.com')"
echo

echo "📋 WHOIS Lookup"
python -c "from beaversec.modules import whois_lookup; whois_lookup.run('google.com')"
echo

echo "🔄 Traceroute"
python -c "from beaversec.modules import traceroute; traceroute.run('google.com')"
echo

echo "✅ Todos os testes concluídos!"
