# PID Bitmap Analysis

> Generated from live `discover` output — 2026-05-10
> Protocol: ISO 9141-2 · Coverage: **22/62 standard PIDs (35%)**

## Does Starting the Engine Unlock More PIDs?

**No.** The supported PID bitmap is declared by the ECU firmware and is fixed regardless of engine state. What *does* change when the engine runs:

| Sensor | Key-ON | Engine Running |
|--------|--------|----------------|
| RPM | `0.0 rpm` | `~750 rpm` at idle |
| MAF | `0.0 g/s` | Real airflow value |
| ENGINE_LOAD | `0.0 %` | Real load % |
| TIMING_ADVANCE | `0.0 °` | Actual advance |
| O2 sensors | `0.455 V` (inactive) | Switching 0.1–0.9 V rapidly |
| FUEL_STATUS | Open loop (cold) | Closed loop (using O2) |
| FUEL_TRIM (short) | `0.0 %` | Active corrections ±10% |
| FUEL_TRIM (long) | `+18%` (learned) | Same — but STFT now visible |

The bitmap tells you what **can** be read. Engine state determines whether those readings are **meaningful**.

---

## Your Car vs. a Modern CAN Bus Vehicle

ISO 9141-2 (your protocol) is a mid-1990s standard. A 2015+ CAN bus vehicle typically exposes 60–80+ PIDs.

```
Your car (ISO 9141-2):  ████████░░░░░░░░░░░░  22/62  (35%)
Typical CAN bus car:    ████████████████████  60+/62 (95%+)
```

This is **normal for this era** — not a fault.

---

## Supported PIDs (22)

| Hex | Name | Category | Useful For |
|-----|------|----------|------------|
| `01` | STATUS | Diagnostics | MIL on/off, DTC count |
| `03` | FUEL_STATUS | Fuel | Open vs. closed loop state |
| `04` | ENGINE_LOAD | Engine | % of max torque — great for logging |
| `05` | COOLANT_TEMP | Temperature | Warm-up tracking, overheating |
| `06` | SHORT_FUEL_TRIM_1 | Fuel | Real-time lean/rich correction, Bank 1 |
| `07` | LONG_FUEL_TRIM_1 | Fuel | ⚠️ +17.97% — learned lean correction, Bank 1 |
| `08` | SHORT_FUEL_TRIM_2 | Fuel | Real-time lean/rich correction, Bank 2 |
| `09` | LONG_FUEL_TRIM_2 | Fuel | ⚠️ +18.75% — learned lean correction, Bank 2 |
| `0C` | RPM | Engine | Core metric — idle, rev range |
| `0D` | SPEED | Vehicle | Speed in km/h |
| `0E` | TIMING_ADVANCE | Engine | Ignition timing degrees |
| `0F` | INTAKE_TEMP | Temperature | Intake air temp |
| `10` | MAF | Air | Mass airflow; use to estimate fuel economy |
| `11` | THROTTLE_POS | Air | Throttle % — maps to driver input |
| `12` | AIR_STATUS | Fuel | Secondary air injection |
| `13` | O2_SENSORS | Diagnostics | Which O2 sensors are present |
| `14` | O2_B1S1 | Oxygen | Bank 1 upstream — primary fuel feedback |
| `15` | O2_B1S2 | Oxygen | Bank 1 downstream — catalyst monitor |
| `18` | O2_B2S1 | Oxygen | Bank 2 upstream |
| `19` | O2_B2S2 | Oxygen | Bank 2 downstream |
| `1C` | OBD_COMPLIANCE | Diagnostics | OBD-II CARB standard |
| `21` | DISTANCE_W_MIL | Diagnostics | km driven with check engine on — currently 0 |

---

## Not Supported (Notable Gaps)

| Hex | Name | Why It Matters |
|-----|------|----------------|
| `02` | FREEZE_DTC | Snapshot of sensor values when a fault triggered |
| `0A` | FUEL_PRESSURE | Direct fuel rail pressure reading |
| `0B` | INTAKE_PRESSURE (MAP) | Manifold absolute pressure — useful for NA vs. boost |
| `1F` | RUN_TIME | Seconds since engine start |
| `2C` | COMMANDED_EGR | EGR valve position |
| `2F` | FUEL_LEVEL | Tank level |
| `31` | DISTANCE_SINCE_DTC_CLEAR | Odometer since last code clear |
| `33` | BAROMETRIC_PRESSURE | Ambient pressure / altitude |
| `3C`–`3F` | CATALYST_TEMP (all 4) | Catalytic converter temperatures |

> **Most impactful gap:** No `CATALYST_TEMP` — can't monitor cat health directly.
> **Workaround:** downstream O2 (`O2_B1S2`, `O2_B2S2`) voltage behavior is a proxy for cat efficiency.

---

## Bitmap Visualization

```
PIDS_A  Bit: 1  2  3  4  5  6  7  8  9  A  B  C  D  E  F 10 11 12 13 14 15 16 17 18 19 1A 1B 1C 1D 1E 1F 20
             █  ░  █  █  █  █  █  █  █  ░  ░  █  █  █  █  █  █  █  █  █  █  ░  ░  █  █  ░  ░  █  ░  ░  ░  █

PIDS_B  Bit: 21 22 23 24 25 26 27 28 29 2A 2B 2C 2D 2E 2F 30 31 32 33 34 35 36 37 38 39 3A 3B 3C 3D 3E 3F 40
              █  ░  ░  ░  ░  ░  ░  ░  ░  ░  ░  ░  ░  ░  ░  ░  ░  ░  ░  ░  ░  ░  ░  ░  ░  ░  ░  ░  ░  ░  ░  ░
```

`█` = supported · `░` = not supported

PIDS_B is nearly empty — this ECU exposes almost nothing in the 0x21–0x40 range beyond `DISTANCE_W_MIL`. This is characteristic of late-1990s ISO 9141-2 implementations.

---

*Re-run `just discover` with engine running to capture live values for all 22 supported PIDs.*
