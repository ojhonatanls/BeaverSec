# Contribuindo para o BeaverSec

Agradecemos seu interesse em contribuir para o BeaverSec.

## Adicionando um novo módulo

O BeaverSec utiliza um sistema de módulos estilo plugin. Novos módulos devem ser registrados como entry points do setuptools sob o grupo `beaversec.modules` para que possam ser descobertos pelo pacote instalado e pelo runner.

Passos para adicionar um novo módulo:

1. Crie um novo arquivo Python em `beaversec/modules/` implementando uma classe que herda de `beaversec.core.base.BaseModule`.

   Exemplo de esqueleto:

```python
from beaversec.core.base import BaseModule, ModuleResult
from beaversec.core.security import SecurityValidator

class MeuModulo(BaseModule):
    """Descrição curta do módulo.

    Documentação mais longa do módulo aqui.
    """

    name = "meu_modulo"
    description = "Descrição do que o módulo faz"
    version = "1.0.0"

    def validate_params(self, params: dict) -> bool:
        # Valida os parâmetros (retorna False ou levanta exceção em caso de inválido)
        return "target" in params

    def execute(self, params: dict) -> ModuleResult:
        # Implementa a lógica principal do módulo aqui
        target = SecurityValidator.validate_target(params.get("target", ""))
        # ... lógica do módulo ...
        return ModuleResult(success=True, data={"ok": True})
2. Registre o módulo no pyproject.toml sob o grupo de entry-points
    [project.entry-points."beaversec.modules"] usando o formato:

    meu_modulo = "beaversec.modules.meu_modulo:MeuModulo"

3. Instale e teste localmente:

    pipinstall−e.pipinstall−e. python3 -m beaversec list
    $ python3 -m beaversec run meu_modulo <alvo>

4. Adicione testes unitários em tests/ cobrindo a lógica de validação e execução.

5. Envie um Pull Request descrevendo o módulo e os testes.

## Compatibilidade com versões anteriores

Módulos antigos podem expor uma função run(target, **kwargs) ou método de classe. O
runner suporta tanto execute(params) quanto funções run() legadas para
compatibilidade com versões anteriores, mas novos módulos devem seguir o padrão da classe
BaseModule.

## Estilo de Código

- Siga as diretrizes do PEP8
- Use nomes significativos e adicione docstrings

## Testes

- Coloque testes unitários em tests/
- Testes de integração vão em tests/integration/

## Commits e PRs

- Use Commits Convencionais
- Inclua testes e atualize a documentação quando necessário
