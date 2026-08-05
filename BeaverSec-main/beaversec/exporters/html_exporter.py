"""Exportador HTML para BeaverSec."""
import json
from datetime import datetime


class HTMLExporter:
    """Exporta resultados para HTML formatado."""

    @staticmethod
    def export(data, output_file):
        """Exporta dados para um arquivo HTML."""
        html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BeaverSec - Relatório</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0e17;
            color: #e0e7f0;
            padding: 20px;
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            text-align: center;
            padding: 30px 0;
            border-bottom: 2px solid #1a2a3a;
            margin-bottom: 30px;
        }}
        .header h1 {{
            font-size: 2.5em;
            margin: 0;
            background: linear-gradient(135deg, #00d4ff, #7b2ffc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .header p {{
            color: #8a9bb5;
            margin: 5px 0 0;
        }}
        .module-card {{
            background: #111b26;
            border: 1px solid #1a2a3a;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }}
        .module-card h2 {{
            color: #00d4ff;
            margin: 0 0 10px;
            font-size: 1.5em;
        }}
        .module-card .target {{
            color: #8a9bb5;
            font-size: 0.9em;
            margin-bottom: 15px;
        }}
        .result-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 10px;
        }}
        .result-item {{
            background: #0d1622;
            border: 1px solid #1a2a3a;
            border-radius: 8px;
            padding: 12px 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .result-item .key {{
            color: #8a9bb5;
            font-weight: 500;
        }}
        .result-item .value {{
            color: #e0e7f0;
            font-weight: 600;
            padding: 2px 10px;
            border-radius: 4px;
        }}
        .value.open {{
            background: #00c85320;
            color: #00c853;
        }}
        .value.closed {{
            background: #ff174420;
            color: #ff1744;
        }}
        .value.filtered {{
            background: #ff910020;
            color: #ff9100;
        }}
        .footer {{
            text-align: center;
            padding: 20px 0;
            color: #4a5a6a;
            font-size: 0.8em;
            border-top: 1px solid #1a2a3a;
            margin-top: 30px;
        }}
        .error {{
            color: #ff1744;
            background: #ff174420;
            padding: 10px 16px;
            border-radius: 8px;
            border-left: 4px solid #ff1744;
        }}
        .success {{
            color: #00c853;
            background: #00c85320;
            padding: 10px 16px;
            border-radius: 8px;
            border-left: 4px solid #00c853;
        }}
        pre {{
            background: #0a0e17;
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
            border: 1px solid #1a2a3a;
            font-size: 0.85em;
            color: #8a9bb5;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🦫 BeaverSec</h1>
        <p>Relatório de Segurança Ofensiva - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
    </div>
    <div class="module-card">
        <h2>{module_name}</h2>
        <div class="target">🎯 Alvo: {target}</div>
        <div class="result-grid">
            {results}
        </div>
    </div>
    <div class="footer">
        BeaverSec v3.0 - Feito por <a href="https://github.com/ojhonatanls" style="color: #00d4ff; text-decoration: none;">Jhonatan</a>
    </div>
</body>
</html>"""

        # Processar os dados
        module_name = "port_scanner"
        target = "127.0.0.1"
        results_html = ""

        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, dict):
                    target = key
                    for port, status in value.items():
                        status_class = "open" if "open" in str(status).lower() else "closed" if "closed" in str(status).lower() else "filtered"
                        results_html += f"""
                        <div class="result-item">
                            <span class="key">Porta {port}</span>
                            <span class="value {status_class}">{status}</span>
                        </div>"""

        html_content = html_content.format(
            module_name=module_name,
            target=target,
            results=results_html
        )

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
