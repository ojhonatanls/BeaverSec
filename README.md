# BeaverSec - Segurança Ofensiva Modular

**Ferramenta modular para pentest, reconhecimento e análise de segurança**

BeaverSec é uma ferramenta modular de segurança cibernética com arquitetura extensível.

## Módulos Disponíveis

- **ping_sweep** - Verifica hosts ativos via ICMP
- **port_scanner** - Escaneia portas TCP abertas
- **dns_enum** - Enumera registros DNS
- **ssl_scan** - Analisa certificados SSL/TLS
- **http_headers** - Analisa headers HTTP de segurança
- **subdomain_brute** - Descobre subdomínios por brute force
- **traceroute** - Rastreia a rota até o alvo

## Instalação

```bash
git clone https://github.com/ojhonatanls/BeaverSec.git
cd BeaverSec
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Licença

MIT © 2024

<p align="center">Feito com ✨ por <a href="https://github.com/ojhonatanls">Jhonatan</a></p>
