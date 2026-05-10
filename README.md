# race2 🏎️

OBD-II vehicle data logger via **OBDLink EX** on macOS.

Reads live sensor data, diagnostic trouble codes (DTCs), freeze frame data, and records time-series telemetry to CSV.

## Requirements

- [Nix](https://nixos.org/download) with flakes enabled
- OBDLink EX connected via USB to Mac, and plugged into your car's OBD-II port

## Setup

```bash
# Enter dev shell (installs all tools)
nix develop

# Install Python deps
just install

# Install git hooks (Lefthook)
lefthook install
```

## Usage

```bash
# Check for fault codes
just dtc
# or: uv run race2 dtc

# Full sensor snapshot (saved to JSON)
just snapshot
# or: uv run race2 snapshot

# Record 60s of live telemetry (saved to CSV)
just record
# or: uv run race2 record --duration 60

# Custom port / baud
uv run race2 --port /dev/cu.usbserial-XXXX --baud 115200 snapshot
```

## Output

| Command    | Output file                        |
|------------|------------------------------------|
| `snapshot` | `obd_snapshot_YYYYMMDD_HHMMSS.json`|
| `record`   | `obd_live_YYYYMMDD_HHMMSS.csv`     |

## Development

```bash
just lint    # ruff check
just fix     # ruff autofix + format
just test    # pytest
```

CI runs automatically on push/PR via GitHub Actions.
