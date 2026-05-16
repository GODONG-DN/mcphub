# Contributing

Thanks for wanting to improve MCPHub.

## Setup

```bash
git clone https://github.com/GODONG-DN/mcphub.git
cd mcphub
pip install -e ".[dev]"
```

## Running tests

```bash
pytest -v
```

## Adding a new MCP server to the registry

1. Add an entry to `registry.json` (and `src/mcphub/registry.py` `REGISTRY` list)
2. Required fields: `name`, `description`, `repo`, `type`, `package`, `command`, `args`
3. Optional: `env`, `tags`, `subdir`
4. Run `pytest` to make sure nothing's broken

## Code style

- Use `ruff` for linting: `ruff check src tests`
- Line length: 100 chars
- No docstrings on simple things, docstrings on tricky things
- Keep it readable — don't over-engineer

## Pull requests

- One feature/fix per PR
- Add tests if you're adding logic
- Make sure tests pass before opening

## Releasing

1. Update `__version__` in `src/mcphub/__init__.py`
2. Update `version` in `pyproject.toml`
3. Create a GitHub release — CI will publish to PyPI
