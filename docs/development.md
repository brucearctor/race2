# Development Guide

## Environment

All tooling is managed via Nix. Enter the dev shell before doing anything:

```bash
nix develop
```

This provides: `python3.12`, `uv`, `lefthook`, `ruff`, `just`

---

## Dependency Management (uv)

```bash
# Install all deps (including dev)
uv sync

# Add a new runtime dependency
uv add <package>

# Add a dev-only dependency
uv add --dev <package>

# Update all deps
uv lock --upgrade
```

---

## Common Tasks (just)

```bash
just          # list all tasks
just install  # uv sync
just lint     # ruff check
just fix      # ruff check --fix + ruff format
just test     # pytest with coverage
just dtc      # read fault codes from car
just snapshot # sensor snapshot → JSON
just record   # 60s live recording → CSV
```

---

## Git Hooks (Lefthook)

Hooks are defined in `lefthook.yml` and installed automatically when you enter the Nix shell.

| Hook | Trigger | What runs |
|---|---|---|
| `pre-commit` | `git commit` | `ruff check` + `ruff format --check` on staged `.py` files |
| `pre-push` | `git push` | Full `pytest` suite |

Reinstall manually:
```bash
lefthook install
```

Skip hooks in an emergency (avoid this):
```bash
git commit --no-verify  # not recommended
```

---

## Testing

Tests live in `tests/` and use mocked OBD connections — no hardware needed to run them.

```bash
# Run all tests
uv run pytest

# With verbose output
uv run pytest -v

# Specific file
uv run pytest tests/test_obd_client.py

# Coverage report
uv run pytest --cov=race2 --cov-report=html
open htmlcov/index.html
```

---

## CI (GitHub Actions)

The CI pipeline runs on every push and PR:

1. **Lint** — `ruff check .`
2. **Format check** — `ruff format --check .`
3. **Tests** — `pytest` with coverage upload to Codecov

The pipeline runs inside the Nix dev shell using `DeterminateSystems/nix-installer-action` with `magic-nix-cache-action` for fast Nix store caching.

---

## Project Structure

```
race2/
├── flake.nix                   # Nix dev shell definition
├── pyproject.toml              # Python project, deps, ruff, pytest config
├── lefthook.yml                # Git hooks
├── justfile                    # Task runner
├── race2/
│   ├── __init__.py
│   ├── obd_client.py           # OBD connection + query helpers
│   └── cli.py                  # Click CLI (dtc, snapshot, record, discover)
├── tests/
│   └── test_obd_client.py      # Unit tests (mocked hardware)
├── docs/
│   ├── getting-started.md
│   ├── sensors.md
│   ├── interpreting-data.md
│   └── development.md
└── .github/
    └── workflows/
        └── ci.yml
```
