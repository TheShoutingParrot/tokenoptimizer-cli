# Repository Guidelines

## Project Structure & Module Organization
- `tokenoptimizer/` is the main package. Key modules: `cli.py` (CLI entry), `client.py` (API calls), `config.py` (config and auth).
- `pyproject.toml` defines packaging, dependencies, and tooling.
- `install.sh` provides a quick install path.
- `tokenoptimizer.egg-info/` is build metadata; avoid editing by hand.
- Tests: there is no `tests/` directory yet; add one for new tests (e.g., `tests/test_cli.py`).

## Build, Test, and Development Commands
- `pip install -e ".[dev]"` set up a dev environment with test and lint tools.
- `pip install -e .` install the package in editable mode.
- `tokenoptimizer --help` sanity check the CLI locally.
- `pytest` run tests; `pytest --cov=tokenoptimizer` for coverage.
- `black tokenoptimizer/` format; `ruff check tokenoptimizer/` lint.

## Coding Style & Naming Conventions
- Python 3.8+; format with Black (line length 88) and lint with Ruff (configured in `pyproject.toml`).
- Prefer `snake_case` for functions and modules, `CapWords` for classes.
- Keep CLI options consistent with existing flags in `tokenoptimizer/cli.py`.

## Testing Guidelines
- Use pytest with `test_*.py` naming.
- Mock external HTTP calls (requests) to avoid hitting the live API.
- Add tests alongside changes that affect CLI behavior or config handling.

## Commit & Pull Request Guidelines
- No git history is present in this checkout, so no commit message convention is documented.
- When contributing, use concise, imperative subjects (e.g., "Add config caching") and include a short PR description plus any CLI output changes.

## Security & Configuration Tips
- Do not commit API keys. Use `TOKENOPTIMIZER_API_KEY` or `tokenoptimizer auth set`.
- Default config path: `~/.config/tokenoptimizer/config`.
