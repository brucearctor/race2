# race2 🏎️

> OBD-II vehicle data logger for macOS via **OBDLink EX**

[![CI](https://github.com/brucearctor/race2/actions/workflows/ci.yml/badge.svg)](https://github.com/brucearctor/race2/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![uv](https://img.shields.io/badge/deps-uv-purple.svg)](https://github.com/astral-sh/uv)
[![Nix](https://img.shields.io/badge/env-nix-5277C3.svg)](https://nixos.org/)

Read live sensor data, diagnostic trouble codes (DTCs), and record time-series telemetry from any OBD-II compliant vehicle directly from your Mac.

---

## Requirements

| Requirement | Notes |
|---|---|
| [Nix](https://nixos.org/download) with flakes enabled | Manages all tooling |
| OBDLink EX adapter | Plugged into car's OBD-II port via USB |
| Vehicle key in **ON** position (or engine running) | Powers the OBD port |

> The OBDLink EX is powered by the car's OBD port — not by USB. The USB cable is data only.

---

## Setup

```bash
# Clone
git clone https://github.com/brucearctor/race2.git
cd race2

# Enter Nix dev shell (installs Python, uv, lefthook, ruff, just)
nix develop

# Install Python dependencies
just install

# Install git hooks
lefthook install
```

---

## Quick Start

```bash
# 1. Check for fault codes
just dtc

# 2. Snapshot all sensors → saves JSON
just snapshot

# 3. Record 60s of live telemetry → saves CSV
just record
```

---

## CLI Reference

All commands support `--port` and `--baud` overrides:

```bash
uv run race2 --port /dev/cu.usbserial-XXXX --baud 115200 <command>
```

### `dtc` — Diagnostic Trouble Codes

```bash
uv run race2 dtc
```

Reads stored fault codes (check engine light codes) from the ECU. Prints a table of codes and descriptions, or confirms no faults are present.

### `snapshot` — Sensor Snapshot

```bash
uv run race2 snapshot [--out my_snapshot.json]
```

Queries all supported sensors in a single pass. Saves results to a timestamped JSON file.

**Output:** `obd_snapshot_YYYYMMDD_HHMMSS.json`

### `record` — Live Telemetry Recording

```bash
uv run race2 record [--duration 60] [--interval 1.0] [--out my_log.csv]
```

Streams live sensor readings to a CSV file. Default: 60 seconds at 1 Hz.

**Output:** `obd_live_YYYYMMDD_HHMMSS.csv`

---

## Output Formats

### Snapshot JSON

```json
{
  "timestamp": "2026-05-10T10:11:26",
  "dtcs": [],
  "sensors": {
    "RPM": "750.0 revolutions_per_minute",
    "COOLANT_TEMP": "84 degree_Celsius",
    "LONG_FUEL_TRIM_1": "17.97 percent",
    ...
  }
}
```

### Live CSV

```
timestamp,RPM,SPEED,COOLANT_TEMP,THROTTLE_POS,ENGINE_LOAD
2026-05-10T10:11:26,750.0 rpm,0.0 kph,85 °C,0.0 %,12.5 %
...
```

---

## Development

```bash
just lint     # ruff check
just fix      # ruff autofix + format
just test     # pytest with coverage
```

CI runs on every push and PR via GitHub Actions (Nix-based).

---

## Documentation

| Doc | Description |
|---|---|
| [Getting Started](docs/getting-started.md) | Hardware setup, drivers, first connection |
| [Sensors Reference](docs/sensors.md) | All supported PIDs and what they measure |
| [Interpreting Data](docs/interpreting-data.md) | How to read fuel trims, O2 sensors, temps |
| [Development](docs/development.md) | Nix, uv, Lefthook, CI setup |
