# Vehicle Data Reference

> Captured: 2026-05-10 · Protocol: **ISO 9141-2** · ECU-reported PIDs: **54**
> Conditions: Key-ON, engine not running

This document describes every data point accessible from this vehicle via OBD-II.
PIDs marked ❌ were reported by the ECU's support bitmap but returned no value under key-ON conditions — start the engine and re-run `just discover` to populate them.

---

## Engine

| PID | Name | Key-ON Value | Unit | Notes |
|-----|------|-------------|------|-------|
| `010C` | RPM | 0.0 | rpm | Will show ~750 at idle |
| `0104` | ENGINE_LOAD | 0.0 | % | 0–100%; calculated from MAF vs. max airflow |
| `010E` | TIMING_ADVANCE | 0.0 | degrees | Ignition advance relative to TDC |
| `0110` | MAF | 0.0 | g/s | Mass Air Flow; use to estimate fuel consumption |

## Temperature

| PID | Name | Key-ON Value | Unit | Notes |
|-----|------|-------------|------|-------|
| `0105` | COOLANT_TEMP | **83** | °C | Normal operating range: 80–100°C |
| `010F` | INTAKE_TEMP | **51** | °C | Ambient + heat soak at time of capture |

## Speed & Distance

| PID | Name | Key-ON Value | Unit | Notes |
|-----|------|-------------|------|-------|
| `010D` | SPEED | 0.0 | km/h | Vehicle speed sensor |
| `0121` | DISTANCE_W_MIL | 0.0 | km | Distance driven with check engine light on — **clean** |

## Fuel System

| PID | Name | Key-ON Value | Unit | Notes |
|-----|------|-------------|------|-------|
| `0103` | FUEL_STATUS | Open loop (cold) | — | Will switch to `Closed loop, using O2 sensor` once warm |
| `0106` | SHORT_FUEL_TRIM_1 | 0.0 | % | Bank 1 real-time correction; normal ±10% |
| `0107` | LONG_FUEL_TRIM_1 | **+17.97** | % | ⚠️ Bank 1 learned correction — elevated, see analysis |
| `0108` | SHORT_FUEL_TRIM_2 | 0.0 | % | Bank 2 real-time correction |
| `0109` | LONG_FUEL_TRIM_2 | **+18.75** | % | ⚠️ Bank 2 learned correction — elevated, see analysis |
| `0112` | AIR_STATUS | Off / atmosphere | — | Secondary air injection status |

## Throttle & Airflow

| PID | Name | Key-ON Value | Unit | Notes |
|-----|------|-------------|------|-------|
| `0111` | THROTTLE_POS | 0.0 | % | 0 = closed, 100 = wide open throttle |

## Oxygen Sensors

4 O2 sensors confirmed present (2 banks × 2 sensors each — upstream + downstream).

| PID | Name | Key-ON Value | Unit | Notes |
|-----|------|-------------|------|-------|
| `0114` | O2_B1S1 | 0.455 | V | Bank 1, upstream (pre-cat). At idle: should switch 0.1–0.9V rapidly |
| `0115` | O2_B1S2 | 0.455 | V | Bank 1, downstream (post-cat). Should be steady ~0.6–0.7V |
| `0118` | O2_B2S1 | 0.455 | V | Bank 2, upstream |
| `0119` | O2_B2S2 | 0.455 | V | Bank 2, downstream |
| `0113` | O2_SENSORS | See below | — | Sensor presence bitmap |

> All O2 readings of **0.455V** at key-ON are normal — sensors are cold/inactive.
> Values only become meaningful with engine running in closed-loop.

**O2 sensor map from `O2_SENSORS`:**
```
Bank 1: sensors 3 & 4 present  (positions S3=upstream, S4=downstream)
Bank 2: sensors 3 & 4 present
```

## Diagnostics & Compliance

| PID | Name | Value | Notes |
|-----|------|-------|-------|
| `0101` | STATUS | No DTCs | MIL off, no stored faults |
| `011C` | OBD_COMPLIANCE | OBD-II (CARB) | Meets California standards |

---

## Not Accessible on This Vehicle

These common PIDs were queried but are **not supported** by this ECU:

| PID | Name | Notes |
|-----|------|-------|
| `012F` | FUEL_LEVEL | Not exposed via ISO 9141-2 on this ECU |
| `0133` | BAROMETRIC_PRESSURE | Not supported |
| `011F` | RUN_TIME | Not supported |
| `0131` | DISTANCE_SINCE_DTC_CLEAR | Not supported |
| `0902` | VIN | Not supported over ISO 9141-2 |
| `010B` | INTAKE_PRESSURE (MAP) | Not in support bitmap |
| `0115` | FUEL_RAIL_PRESSURE | Not in support bitmap |

---

## ⚠️ Fuel Trim Analysis

Both banks show **elevated long-term fuel trim (~+18%)**, meaning the ECU has learned to continuously add ~18% more fuel than the base map expects. This is a consistent, cross-bank finding.

**What it rules out:**
- Single injector failure (both banks affected equally)
- Bank-specific O2 sensor fault

**Most likely causes (in order of probability):**

1. **Dirty or failing MAF sensor** — most common cause of symmetric high LTFT
   - Fix: clean with MAF cleaner spray; cost ~$10
2. **Vacuum/intake leak** — unmetered air entering after the MAF
   - Fix: inspect intake manifold gaskets, PCV hoses, brake booster line
3. **Weak fuel pressure** — pump or regulator not delivering enough fuel
   - Fix: fuel pressure test
4. **Clogged fuel injectors** — less likely given symmetry across banks

**How to diagnose with race2:**
```bash
# Start engine, let fully warm up, then:
just record --duration 300

# Look for STFT oscillating while LTFT stays elevated
# If STFT = 0 and LTFT = +18%, ECU has "given up" correcting — suggests MAF
# If STFT is also high and jumping, suggests a dynamic leak
```

---

## Raw Support Bitmaps

```
PIDS_A (01-20): 10111111100111111111100110010001
PIDS_B (21-40): 10000000000000000000000000000000
PIDS_9A        : (all zeros — mode 09 / VIN not supported)
```

---

*Generated by `race2` — re-run `just discover` with engine running for full live values.*
