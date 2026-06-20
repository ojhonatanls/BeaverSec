# 🦫 BeaverSec

**BeaverSec - Modular Swiss Army Knife for Cybersecurity**

BeaverSec é uma ferramenta modular de segurança cibernética projetada para ser extensível e fácil de usar. Com uma arquitetura baseada em módulos, você pode adicionar novas funcionalidades rapidamente e executar tarefas de reconhecimento e análise de rede.

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Tests](https://img.shields.io/badge/tests-3%2F3%20passing-brightgreen)

---

## 📦 Módulos Disponíveis

| Módulo | Descrição | Exemplo de Uso |
|--------|-----------|----------------|
| **dns_enum** | Enumeração de registros DNS (A, MX, NS, TXT, CNAME, SOA) | `python main.py dns_enum google.com` |
| **subdomain_brute** | Descoberta de subdomínios por brute force | `python main.py subdomain_brute google.com` |
| **http_headers** | Análise de headers HTTP de segurança (HSTS, CSP, etc.) | `python main.py http_headers https://google.com` |
| **ssl_scan** | Verificação de certificados SSL/TLS e expiração | `python main.py ssl_scan google.com` |
| **banner_grabber** | Captura de banners e detecção de versões vulneráveis | `python main.py banner_grabber 192.168.1.1` |
| **whois_lookup** | Consulta WHOIS de domínios | `python main.py whois_lookup google.com` |
| **traceroute** | Rastreamento de rotas de rede | `python main.py traceroute google.com` |
| **ping_sweep** | Varredura de hosts em uma rede | `python main.py ping_sweep 192.168.1.0/24` |
| **port_scanner** | Scanner de portas TCP | `python main.py port_scanner 192.168.1.1` |

---

## 🚀 Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/ojhonatanls/beaversec.git
cd beaversec
```

### 2. Crie um ambiente virtual (recomendado)

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Execute a ferramenta

```bash
python main.py --help
```

---

## 🎯 Exemplos de Uso

### Enumeração DNS
```bash
python main.py dns_enum google.com
```
**Saída:**
```
[+] DNS Enumeration for google.com
  A: 142.250.217.46
  MX: 10 smtp.google.com
  NS: ns1.google.com, ns2.google.com
  TXT: v=spf1 include:_spf.google.com ~all
```

### Análise de Headers HTTP
```bash
python main.py http_headers https://github.com
```
**Saída:**
```
[+] HTTP Headers for https://github.com (Status: 200)
  Strict-Transport-Security: ✅ Present -> max-age=31536000
  Content-Security-Policy: ✅ Present -> default-src 'none'
  X-Frame-Options: ✅ Present -> deny
  X-Content-Type-Options: ✅ Present -> nosniff
```

### Scan SSL/TLS
```bash
python main.py ssl_scan google.com
```
**Saída:**
```
[+] SSL/TLS Info for google.com:443
  Subject: CN=google.com
  Issuer: CN=GTS CA 1C3
  Valid From: 2025-01-15 08:00:00
  Valid To: 2025-04-09 07:59:59
  ✅ Válido por mais 85 dias.
  Cipher: ('TLS_AES_256_GCM_SHA384', 'TLSv1.3', 256)
```

### Captura de Banners
```bash
python main.py banner_grabber 192.168.1.1
```
**Saída:**
```
[+] Grabbing banners from 192.168.1.1...
  Port 22:
    Banner: SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.6
    ⚠️  Possíveis vulnerabilidades: OpenSSH 8.9 -> CVE-2023-38408 (RCE)
  Port 80:
    Banner: nginx/1.18.0
```

---

## 🛠️ Criando Novos Módulos

BeaverSec foi projetado para ser facilmente extensível. Para criar um novo módulo:

1. **Crie um arquivo** em `modules/meu_modulo.py`
2. **Implemente a função `run()`**:

```python
def run(target, **kwargs):
    """
    Descrição do seu módulo.
    Exemplo: python main.py meu_modulo alvo.com
    """
    print(f"[+] Executando meu_modulo em {target}")
    # Sua lógica aqui
    return resultado
```

3. **Pronto!** O módulo será automaticamente carregado pelo `ModuleHandler`.

---

## ⚙️ Configuração

O BeaverSec usa um arquivo `config.yaml` para configurações centralizadas:

```yaml
settings:
  timeout: 3.0
  max_threads: 50
  default_ports: [21, 22, 23, 25, 80, 443, 3306, 3389]

modules:
  ssl_scan:
    warn_expiry_days: 30
  banner_grabber:
    grab_timeout: 5.0
```

---

## 🧪 Testes

Execute os testes automatizados para verificar se tudo está funcionando:

```bash
pytest tests/ -v
```

**Saída esperada:**
```
tests/test_modules.py::test_dns_enum PASSED     [ 33%]
tests/test_modules.py::test_http_headers PASSED [ 66%]
tests/test_modules.py::test_whois PASSED        [100%]
```

---

## 📂 Estrutura do Projeto

```
beaversec/
├── config.yaml              # Configurações centralizadas
├── requirements.txt         # Dependências do projeto
├── main.py                  # Ponto de entrada
├── core/
│   └── module_handler.py    # Gerenciador de módulos
├── modules/                 # Módulos de segurança
│   ├── dns_enum.py
│   ├── subdomain_brute.py
│   ├── http_headers.py
│   ├── ssl_scan.py
│   ├── banner_grabber.py
│   ├── whois_lookup.py
│   ├── traceroute.py
│   ├── ping_sweep.py
│   └── port_scanner.py
├── tests/                   # Testes automatizados
│   └── test_modules.py
└── utils/                   # Utilitários
    └── config_loader.py     # Carregador de configurações
```

---

## 🤝 Contribuição

Contribuições são bem-vindas! Siga os passos:

1. Faça um **Fork** do projeto
2. Crie uma **branch** para sua feature: `git checkout -b feature/nova-funcionalidade`
3. **Commit** suas mudanças: `git commit -m "feat: adiciona nova funcionalidade"`
4. **Push** para a branch: `git push origin feature/nova-funcionalidade`
5. Abra um **Pull Request**

---

## 📄 Licença

Este projeto está licenciado sob a **MIT License** - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## 👨‍💻 Autor

**Jhonatan Lucas Santos** - [GitHub](https://github.com/ojhonatanls)

Projeto desenvolvido no 1º semestre de Tecnologia em Sistemas para Internet (TSI) na UTFPR.

---

## ⭐ Agradecimentos

Se este projeto foi útil para você, considere dar uma ⭐ no GitHub!