"""Exportador de relatórios HTML."""

import datetime
from typing import Dict, Any

def export_html(data: Dict[str, Any], output_file: str) -> None:
    """Exporta resultado para HTML."""
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>BeaverSec - Relatório</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 1000px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
            h2 { color: #34495e; margin-top: 30px; }
            .module { background: #ecf0f1; padding: 15px; border-radius: 5px; margin: 10px 0; }
            .success { color: #27ae60; }
            .error { color: #e74c3c; }
            table { width: 100%; border-collapse: collapse; margin: 15px 0; }
            th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background: #3498db; color: white; }
            .footer { margin-top: 40px; text-align: center; color: #7f8c8d; font-size: 12px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🦫 BeaverSec - Relatório</h1>
            <p><strong>Módulo:</strong> {{ data.module }}</p>
            <p><strong>Alvo:</strong> {{ data.target }}</p>
            <p><strong>Data:</strong> {{ data.timestamp }}</p>
            
            <h2>📊 Resultados</h2>
            <div class="module">
                {% for key, value in data.result.items() %}
                    {% if key != 'error' %}
                        <p><strong>{{ key }}:</strong> {{ value }}</p>
                    {% endif %}
                {% endfor %}
            </div>
            
            {% if data.result.error %}
                <div class="error">
                    <strong>❌ Erro:</strong> {{ data.result.error }}
                </div>
            {% endif %}
            
            <div class="footer">
                <p>Gerado por BeaverSec v0.2.0</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    from jinja2 import Template
    template = Template(html_template)
    html_output = template.render(data=data)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_output)
    
    print(f"📄 Relatório HTML salvo em: {output_file}")