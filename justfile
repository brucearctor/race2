# Default recipe: list available tasks
default:
    @just --list

# Install dependencies
install:
    uv sync

# Run linter
lint:
    uv run ruff check .

# Auto-fix lint issues
fix:
    uv run ruff check --fix .
    uv run ruff format .

# Run tests
test:
    uv run pytest

# Read DTCs from vehicle
dtc:
    uv run race2 dtc

# Take a sensor snapshot
snapshot:
    uv run race2 snapshot

# Record 60 seconds of live data
record duration="60":
    uv run race2 record --duration {{duration}}
