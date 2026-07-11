BeaverSec - Segurança Ofensiva Modular
======================================

O que é o BeaverSec
-------------------

BeaverSec é um framework modular de segurança ofensiva projetado para reconhecimento,
enumeração e análise de vulnerabilidades. Construído com Python 3.8+, ele fornece uma
arquitetura baseada em plugins para realizar avaliações de segurança.

Características principais:

- Arquitetura modular de plugins usando entry points do setuptools
- Validação e sanitização segura de entrada
- Logs estruturados com trilha de auditoria
- Processamento síncrono otimizado (sem async)
- Design nativo para Linux (sem código específico para Windows/macOS)
- Dependências mínimas usando extensões da biblioteca padrão Python

Dependências
------------

Os seguintes pacotes são necessários:

- click >= 8.1       - Interface de linha de comando
- pydantic >= 1.10   - Validação de dados
- aiohttp >= 3.8     - Cliente HTTP assíncrono
- pyyaml >= 6.0      - Parsing de configuração YAML
- dnspython >= 2.3   - Consultas DNS
- shodan >= 1.27     - Integração com a API Shodan
- pysnmp >= 4.4      - Suporte ao protocolo SNMP
- scapy >= 2.4       - Manipulação de pacotes de rede
- cryptography >= 41.0 - Operações criptográficas
- pytest >= 7.0      - Framework de testes
- python-whois >= 0.7 - Consultas WHOIS (instalação opcional)

Como instalar
-------------

Instalação com um único comando (recomendado):

    $ curl -sSL https://raw.githubusercontent.com/ojhonatanls/BeaverSec/main/scripts/install.sh | bash

Ou clone e execute o instalador (alternativa):

    $ git clone https://github.com/ojhonatanls/BeaverSec.git
    $ cd BeaverSec
    $ ./install.sh

Notas:
- O instalador agora cria um ambiente virtual (venv) para isolar as dependências.
- Ele verifica a versão do Python (3.8+), instala as dependências e configura
  o BeaverSec em modo editável.
- O instalador tenta garantir que o comando `beaversec` esteja disponível no PATH.
- Para módulos que exigem root (arp_scan, syn_scan), use `sudo python3 -m beaversec`.

Verifique a instalação:

    $ python3 -m beaversec --help

Início Rápido
-------------

Listar módulos disponíveis:

    $ python3 -m beaversec list

Executar um módulo contra um alvo:

    $ python3 -m beaversec run ping_sweep 192.168.1.1
    $ python3 -m beaversec run port_scanner 192.168.1.1 -p 80
    $ python3 -m beaversec run dns_enum example.com

Salvar resultados em arquivo:

    $ python3 -m beaversec run port_scanner 192.168.1.1 -p 80 -o results.json

Runner
------

O projeto inclui um script runner `beaversec_runner.py` que pode ser usado como
alternativa ao entry point `beaversec`. O runner foi adaptado para carregar
módulos via entry points do setuptools (grupo `beaversec.modules`). Prefira o
comando `python3 -m beaversec` quando disponível, pois oferece uma interface
mais completa com Click.

Configuração
------------

Arquivo de configuração (XDG): ~/.config/beaversec/config.yaml

Crie este arquivo para personalizar o comportamento do BeaverSec:

    # Chaves de API
    shodan:
      api_key: "SUA_SHODAN_API_KEY"
    
    nvd:
      api_key: "SUA_NVD_API_KEY"
    
    securitytrails:
      api_key: ""

    # Comportamento
    rate_limit: 200
    http_timeout: 30

    # Proxy
    proxy:
      url: ""
      username: ""
      password: ""

    # Segurança
    use_tor: false
    tor_proxy: "socks5://127.0.0.1:9050"

    # Furtividade
    stealth:
      enable_mac_spoof: false
      random_delay_range: [0.0, 0.5]
      packet_fragmentation: false

    # Exportadores
    exporters:
      json: true
      html: true
      csv: true
      pdf: false

    # Timeouts
    arp_timeout: 2

Módulos Disponíveis
-------------------

- ping_sweep        - Descoberta de hosts via ICMP
- arp_scan          - Descoberta de hosts na rede local via ARP (requer root)
- port_scanner      - Escaneamento de portas TCP com detecção de serviço
- syn_scan          - Escaneamento SYN furtivo (requer root)
- udp_scan          - Escaneamento de portas UDP
- dns_enum          - Enumeração de registros DNS
- dns_zone_transfer - Teste de transferência de zona DNS
- subdomain_brute   - Força bruta de subdomínios
- ssl_scan          - Análise de certificados SSL/TLS
- ssl_cipher_scan   - Enumeração de ciphers SSL/TLS
- http_headers      - Análise de cabeçalhos de segurança HTTP
- whois_lookup      - Consulta WHOIS de domínios/IPs
- shodan_enum       - Enriquecimento de dados via API Shodan
- vuln_scanner      - Escaneamento de vulnerabilidades
- service_detection - Identificação de serviços via banner grabbing
- os_detection      - Identificação de sistema operacional via TTL
- snmp_enum         - Enumeração SNMP
- banner_grabber    - Captura de banners em portas específicas

Contribuindo
------------

Guia para adicionar novos módulos:

1. Crie um novo arquivo Python em `beaversec/modules/` implementando uma classe
   que herda de `beaversec.core.base.BaseModule`.

2. Implemente `validate_params(self, params)` e `execute(self, params)` na
   classe. O método `execute` deve retornar um objeto `ModuleResult`.

3. Registre o módulo no `pyproject.toml` sob o grupo de entry-points
   `[project.entry-points."beaversec.modules"]`:

   ping_sweep = "beaversec.modules.ping_sweep:PingSweepModule"

4. Teste instalando o pacote em modo editável e executando o CLI:

    $ pip install -e .
    $ python3 -m beaversec list
    $ python3 -m beaversec run <modulo> <alvo>

5. Abra um PR com suas alterações.

Testes
------

Execute os testes unitários:

    $ pytest -q

Testes de integração estão localizados em `tests/integration/` e são executados
pela matriz de integração do CI.

Solução de Problemas
---------------------

1. **Erro "externally-managed-environment"**:
   O Python do sistema está protegido. Use o ambiente virtual:
   `python3 -m venv venv && source venv/bin/activate`

2. **"beaversec: command not found"**:
   Ative o ambiente virtual: `source venv/bin/activate`
   Ou use: `python3 -m beaversec`

3. **"ModuleNotFoundError: No module named 'beaversec'"**:
   Certifique-se de que o ambiente virtual está ativado e reinstale:
   `pip install -e .`

4. **"Permission denied" no arp_scan ou syn_scan**:
   Execute com sudo: `sudo python3 -m beaversec run <modulo> <alvo>`

5. **"Invalid target: 192.168.1.0/24" no arp_scan**:
   O arp_scan aceita apenas IP individual, não CIDR.
   Correto: `sudo python3 -m beaversec run arp_scan 192.168.1.1`

6. **Módulo não aparece no `beaversec list`**:
   Verifique se o módulo está registrado no `pyproject.toml` e reinstale:
   `pip install -e .`

Se `beaversec` não estiver no PATH após a instalação, inicie um novo shell ou
execute `source ~/.profile` ou `source venv/bin/activate`.

Licença
-------

MIT License 2024

Mantido por Jhonatan L. Santos (https://github.com/ojhonatanls)
