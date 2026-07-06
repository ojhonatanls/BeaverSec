# Contributing to BeaverSec

Thank you for your interest in contributing to BeaverSec.

## Adding a new module

BeaverSec uses a plugin-style module system. New modules should be registered as
setuptools entry points under the `beaversec.modules` group so they can be
discovered by the installed package and by the runner.

Steps to add a new module:

1. Create a new Python file under `beaversec/modules/` implementing a class that
   inherits from `beaversec.core.base.BaseModule`.

   Example skeleton:

```python
from beaversec.core.base import BaseModule

class MyModule(BaseModule):
    """Short description of the module.

    Longer module documentation here.
    """

    name = "my_module"

    def validate_params(self, params: dict) -> bool:
        # Validate parameters (raise or return False on invalid)
        return True

    def execute(self, params: dict) -> dict:
        # Implement main module logic here
        return {"ok": True}
```

2. Register the module in `pyproject.toml` under the entry-point group
   `[project.entry-points."beaversec.modules"]` using the format:

   my_module = "beaversec.modules.my_module:MyModule"

3. Install and test locally:

    $ pip install -e . --user
    $ beaversec list
    $ beaversec run my_module <target>

4. Add unit tests under `tests/` covering validation and execution logic.

5. Submit a Pull Request describing the module and tests.

### Backwards compatibility
Older modules may expose a `run(target, **kwargs)` function or class method. The
runner supports both `execute(params)` and legacy `run()` functions for
backward compatibility, but new modules should follow the `BaseModule` class
pattern.

## Code Style

- Follow PEP8 guidelines
- Use meaningful names and add docstrings

## Tests

- Place unit tests in `tests/`
- Integration tests go in `tests/integration/`

## Commits and PRs

- Use Conventional Commits
- Include tests and update documentation when needed

