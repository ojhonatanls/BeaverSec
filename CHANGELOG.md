# Changelog

## v4.0.0 — Release

Short summary of changes included in this release (post-audit):

- Refactor: module discovery unified around setuptools entry points (`beaversec.modules`). All existing modules are now registered as entry points in pyproject.toml.
- Refactor: ModuleManager now prefers entry points and wraps legacy callable `run()` functions with adapters — fallback to directory scanning preserved for development installs.
- Fix: banner_grabber module import fixed and adapted to use the project's configuration loader.
- Feature: Configuration loader unified to XDG path (~/.config/beaversec/config.yaml) and ensures secure directory/file permissions.
- CI: GitHub Actions workflow expanded with a distro matrix (integration job) and unit test matrix for Python versions; integration tests added under tests/integration/.
- Docs: README updated with one-command installation flow, XDG config instructions, and entry-point guidance; CONTRIBUTING.md updated with a module authoring guide.
- Tooling: beaversec_runner.py updated to load modules via entry points; pyproject.toml entry-points section added/expanded.

Notes:
- Backwards compatibility: the runner and ModuleManager handle both new `BaseModule` classes and legacy `run()` callables.
- The package version in pyproject.toml is 4.0.0.

