<p align="center">
  <img src="assets/BeaverSec2.png" alt="BeaverSec Banner" width="100%">
</p>

# 🦫 BeaverSec - Segurança Ofensiva Modular

**Ferramenta modular para pentest, reconhecimento e análise de segurança**

BeaverSec é uma ferramenta modular de segurança cibernética com arquitetura extensível.

## 📋 Módulos Disponíveis

- 🖥️ **ping_sweep** - Verifica hosts ativos via ICMP
- 🔌 **port_scanner** - Escaneia portas TCP abertas
- 🌐 **dns_enum** - Enumera registros DNS
- 🔒 **ssl_scan** - Analisa certificados SSL/TLS
- 📋 **http_headers** - Analisa headers HTTP de segurança
- 🔍 **subdomain_brute** - Descobre subdomínios por brute force
- 🗺️ **traceroute** - Rastreia a rota até o alvo
- 🕵️ **whois_lookup** - Consulta WHOIS de domínios

## 🚀 Instalação

```bash
git clone https://github.com/ojhonatanls/BeaverSec.git
cd BeaverSec
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

## 💻 Como usar

### Listar módulos disponíveis
```bash
beaversec list
```

### Executar um módulo
```bash
# Ping sweep
beaversec run ping_sweep --target 8.8.8.8

# Port scanner
beaversec run port_scanner --target 127.0.0.1

# DNS enumeration
beaversec run dns_enum --target example.com

# Subdomain brute force
beaversec run subdomain_brute --target example.com

# WHOIS lookup
beaversec run whois_lookup --target example.com
```

### Salvar resultado em JSON
```bash
beaversec run port_scanner --target 127.0.0.1 --output-file resultado.json --format json
```

### Salvar resultado em CSV
```bash
beaversec run port_scanner --target 127.0.0.1 --output-file resultado.csv --format csv
```

### Salvar resultado em HTML
```bash
beaversec run port_scanner --target 127.0.0.1 --output-file resultado.html --format html
```

### Modo verbose
```bash
beaversec run ping_sweep --target 8.8.8.8 --verbose
```

### Timeout customizado
```bash
beaversec run dns_enum --target example.com --timeout 10
```

## 📊 Exemplo de saída

```bash
beaversec run ping_sweep --target 8.8.8.8
```

```json
{
  "module": "ping_sweep",
  "target": "8.8.8.8",
  "success": true,
  "timestamp": "2024-06-22T10:30:45Z",
  "duration": 1.234,
  "data": {
    "host": "8.8.8.8",
    "status": "ATIVO",
    "latency_ms": 24.10
  }
}
```

## ⚙️ Configuração

BeaverSec suporta configuração via arquivo YAML. Crie um arquivo `config.yaml` na raiz do projeto:

```yaml
# config.yaml
threads: 10
timeout: 5.0
rate_limit: 100
verbose: false
```

As opções da CLI sobrescrevem os valores do arquivo de configuração.

## 📝 Licença

MIT © 2024

---

<p align="center">Feito com 🦫 por <a href="https://github.com/ojhonatanls">Jhonatan</a></p>