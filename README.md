BeaverSec - Segurança Ofensiva Modular (v4.0)
==============================================

Visão Geral

"BeaverSec é um framework de segurança ofensiva modular projetado para reconhecimento, enumeração e análise de vulnerabilidades. A v4.0 representa uma reformulação completa com foco em segurança, performance e arquitetura robusta."
Principais Características

    Arquitetura Modular: Sistema baseado em plugins com descoberta automática de módulos

"    Segurança em Primeiro Lugar: Sanitização de entradas, logging auditável e validação rigorosa"

"    Alta Performance: Processamento assíncrono, rate limiting e connection pooling"

"    Multiplataforma: Suporte nativo para Windows, Linux e macOS"

    Zero Dependências Externas: Utiliza apenas bibliotecas padrão do Python

    Logging Estruturado: Auditoria completa com logs em JSON e formato padrão

Módulos Disponíveis (16)
Módulo	Descrição
ping_sweep	Varredura ICMP e ARP para descoberta de hosts
port_scanner	Escaneamento TCP com detecção de serviços
syn_scan	SYN stealth scan para varredura sigilosa
udp_scan	Escaneamento UDP para serviços baseados em UDP
"dns_enum	Enumeração de registros DNS (A, AAAA, MX, NS, TXT, etc.)"
dns_zone_transfer	Teste de transferência de zona DNS
subdomain_brute	Força bruta de subdomínios com wordlist
ssl_scan	Análise de certificados SSL/TLS
ssl_cipher_scan	Enumeração de cifras SSL/TLS suportadas
http_headers	Análise de cabeçalhos HTTP de segurança
whois_lookup	Consulta WHOIS para domínios e IPs
shodan_enum	Enriquecimento de dados via Shodan API
vuln_scanner	Scanner de vulnerabilidades via NVD API
service_detection	Detecção de serviços via banner grabbing
os_detection	Fingerprinting de sistema operacional
snmp_enum	Enumeração SNMP com comunidades padrão

Início Rápido
1. Instalação

Linux/macOS:
text

./scripts/install.sh

Windows:
text

.\scripts\install.ps1

Com ferramentas de desenvolvimento:
text

./scripts/install.sh --dev

2. Configuração

Copie o arquivo de configuração de exemplo:
text

cp beaversec/config/templates/config.yaml.template ~/.beaversec/config.yaml

Edite ~/.beaversec/config.yaml para adicionar chaves de API e configurações de proxy.
3. Uso Básico

Listar módulos disponíveis:
text

beaversec list

Executar um módulo:
text

beaversec run <module_name> <target>

Exemplos:
text

"beaversec run port_scanner 192.168.1.1 -p 22,80,443"
beaversec run subdomain_brute example.com
beaversec run dns_enum example.com

Exportadores de Resultados
JSON
text

"beaversec run port_scanner 127.0.0.1 -p 22,80,443 -o resultado.json"

HTML
text

"beaversec run port_scanner 127.0.0.1 -p 22,80,443 -o resultado.html --format html"

CSV
text

"beaversec run port_scanner 127.0.0.1 -p 22,80,443 -o resultado.csv --format csv"

Configuração

BeaverSec suporta configuração via arquivo YAML. Crie um arquivo config.yaml em ~/.beaversec/:
text

# BeaverSec Configuration
threads: 10
timeout: 5.0
rate_limit: 100
verbose: false
log_level: INFO
max_results: 10000

# Proxy Configuration
proxy:
"  url: """""
"  username: """""
"  password: """""
  use_tor: false
"  tor_proxy: ""socks5://127.0.0.1:9050"""

# Security Settings
security:
  allow_private_networks: false
  max_targets: 1000
  allow_loopback: false

# API Keys (configure via environment variables for security)
"# SHODAN_API_KEY: """""
"# NVD_API_KEY: """""
"# SECURITYTRAILS_API_KEY: """""

"Nota: As opções da CLI sobrescrevem os valores do arquivo de configuração. Para maior segurança, configure as chaves de API como variáveis de ambiente:"
text

"export SHODAN_API_KEY=""sua_chave_aqui"""
"export NVD_API_KEY=""sua_chave_aqui"""
"export SECURITYTRAILS_API_KEY=""sua_chave_aqui"""

Novos Recursos na v4.0
🔒 Segurança Aprimorada

    Sanitização rigorosa de todas as entradas

    Logger auditável com rastreabilidade completa

    Gerenciamento seguro de credenciais com criptografia

    Validação de alvos com bloqueio de redes privadas

"    Eliminação total de eval(), exec() e subprocessos inseguros"

⚡ Performance e Robustez

    Connection pooling para scanners de rede

    Cache LRU para consultas DNS

    Rate limiting adaptativo por módulo

    Timeouts configuráveis com retry exponencial

    Processamento paralelo com controle de workers

🛠️ Arquitetura

    Sistema de módulos com descoberta automática

    Hierarquia de exceções personalizada

    Estrutura de validação centralizada

"    Reporters para múltiplos formatos (JSON, HTML, CSV)"

    Suporte nativo multiplataforma

📊 Logging e Auditoria

    Logs estruturados em JSON para integração com SIEM

    Rotação automática de logs

    Níveis de log configuráveis

    Auditoria completa de todas as operações

Notas do Desenvolvedor
Estrutura do Projeto
text

beaversec/
├── cli/          # Interface de linha de comando
"├── core/         # Núcleo do framework (segurança, validação, base)"
├── modules/      # Módulos de scanner (16 módulos)
"├── utils/        # Utilitários (logging, credenciais, rede, rate limiter)"
└── config/       # Configuração e templates

Desenvolvimento

Adicionar um novo módulo:

    Crie um arquivo em beaversec/modules/

    Herde da classe BaseModule

    Implemente os métodos execute() e validate_params()

    O módulo será descoberto automaticamente

Testes:
text

# Executar todos os testes
pytest

# Com cobertura
pytest --cov=beaversec

# Apenas testes unitários
pytest -m unit

# Apenas testes de segurança
pytest -m security

Padrões de Código:

    Siga PEP8

    Inclua docstrings completas

    Use type hints

    Mantenha 100% de cobertura de testes para módulos centrais

Licença

MIT © 2024 Jhonatan L. Santos

Contribuindo

    Fork o projeto

    Crie uma branch para sua feature (git checkout -b feature/AmazingFeature)

    Commit suas mudanças (git commit -m 'Add some AmazingFeature')

    Push para a branch (git push origin feature/AmazingFeature)

    Abra um Pull Request