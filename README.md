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

## 🚀 Instalação

```bash
git clone https://github.com/ojhonatanls/BeaverSec.git
cd BeaverSec
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 💻 Como usar

```bash
# Listar módulos disponíveis
python main.py -l

# Executar ping sweep
python main.py ping_sweep 8.8.8.8

# Executar com verbose
python main.py ping_sweep 8.8.8.8 -v

# Salvar resultado em JSON
python main.py ping_sweep 8.8.8.8 -o resultado.json
```

## 📊 Exemplo de saída

```bash
python main.py ping_sweep 8.8.8.8
```

```
==================================================
📊 RESULTADO DO MÓDULO: PING_SWEEP
==================================================
Host: 8.8.8.8
Status: ✅ ATIVO
Latência: 24.10ms
==================================================
```

## 📝 Licença

MIT © 2024

---

<p align="center">Feito com 🦫 por <a href="https://github.com/ojhonatanls">Jhonatan</a></p>
