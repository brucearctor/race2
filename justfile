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

# Discover all PIDs the ECU actually supports
discover:
    uv run race2 discover

# Launch analysis dashboard
dashboard:
    uv run streamlit run race2/dashboard.py

# Generate demo data for dashboard testing
demo-data:
    uv run python3 -c "from race2.sample_data import write_sample_csv, write_sample_snapshot; from pathlib import Path; write_sample_csv(Path('sample_session.csv')); write_sample_snapshot(Path('sample_snapshot.json'))"
