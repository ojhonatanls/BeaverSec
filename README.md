# BeaverSec - Segurança Ofensiva Modular (v3.0)

## Visão geral

Estrutura de digitalização modular com módulos baseados em BaseModule.

Novos módulos em 3.0: syn_scan, udp_scan, arp_scan, os_detection, service_detection, vuln_scanner, ssl_cipher_scan, dns_zone_transfer, shodan_enum, snmp_enum.

Async I/O com aiohttp, limitação de taxa de token-bucket, proxy e suporte a Tor.

## Módulos disponíveis (16)

- ping_sweep - Varredura ICMP e ARP
- port_scanner - Escaneamento TCP
- syn_scan - SYN stealth scan
- udp_scan - Escaneamento UDP
- dns_enum - Enumeração de registros DNS
- dns_zone_transfer - Teste de transferência de zona DNS
- subdomain_brute - Força bruta de subdomínios
- ssl_scan - Análise de certificados SSL/TLS
- ssl_cipher_scan - Enumeração de cifras SSL/TLS
- http_headers - Análise de cabeçalhos HTTP de segurança
- whois_lookup - Consulta WHOIS
- shodan_enum - Enriquecimento via Shodan API
- vuln_scanner - Scanner de vulnerabilidades via NVD API
- service_detection - Detecção de serviços via banner grabbing
- os_detection - Fingerprinting de sistema operacional
- snmp_enum - Enumeração SNMP

## Início rápido

Instalar dependências:

    pip install -r requirements.txt

Editar config.yaml para adicionar chaves de API (Shodan, SecurityTrails, NVD) e configurações de proxy opcionais.

Exemplo de uso:

    beaversec list
    beaversec run port_scanner 192.0.2.1 -p 22,80,443
    beaversec run subdomain_brute example.com

## Exportadores

JSON:

    beaversec run port_scanner 127.0.0.1 -p 22,80,443 -o resultado.json

HTML:

    beaversec run port_scanner 127.0.0.1 -p 22,80,443 -o resultado.html --format html

CSV:

    beaversec run port_scanner 127.0.0.1 -p 22,80,443 -o resultado.csv --format csv

## Configuração

BeaverSec suporta configuração via arquivo YAML. Crie um arquivo config.yaml na raiz do projeto:

```yaml
# config.yaml
threads: 10
timeout: 5.0
rate_limit: 100
verbose: false

proxy:
  url: ""
  username: ""
  password: ""

use_tor: false
tor_proxy: "socks5://127.0.0.1:9050"

shodan:
  api_key: "YOUR_SHODAN_API_KEY"

nvd:
  api_key: "YOUR_NVD_API_KEY"

securitytrails:
  api_key: "YOUR_SECURITYTRAILS_API_KEY"
```

As opções da CLI sobrescrevem os valores do arquivo de configuração.

## Novos recursos na v3.0

- Limitação de taxa usando token-bucket em todos os módulos.
- Suporte a proxy e Tor para módulos baseados em HTTP.
- Enumeração de cifras e varredura SSL aprimorada com heurística de vulnerabilidade básica.
- Integrações com Shodan e SecurityTrails para enriquecimento de dados.
- Módulos assíncronos para melhor desempenho.

## Notas do desenvolvedor

- Os módulos são registrados automaticamente em `beaversec/modules/__init__.py`.
- A CLI permanece compatível com versões anteriores; módulos mais antigos que expõem `execute()` ainda são suportados.
- Testes estão esqueletizados sob `tests/` — adicionar asserções e mocks conforme necessário.
- Siga PEP8 e inclua docstrings.
- Execute testes com `pytest`.

## Licença

MIT © 2024

---

Feito por [Jhonatan](https://github.com/ojhonatanls)
