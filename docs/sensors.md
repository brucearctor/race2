# Sensors Reference

## How PIDs Work

OBD-II uses **Parameter IDs (PIDs)** — numeric codes the diagnostic tool sends to the ECU to request specific sensor values. Not all PIDs are supported by every vehicle. Use `just discover` to see what your car actually exposes.

---

## Supported PIDs

### Engine

| PID Name | Unit | Description |
|---|---|---|
| `RPM` | rpm | Engine revolutions per minute |
| `ENGINE_LOAD` | % | Calculated engine load (0–100%) |
| `TIMING_ADVANCE` | degrees | Ignition timing advance relative to TDC |
| `RUN_TIME` | seconds | Time since engine start |

### Temperature

| PID Name | Unit | Description |
|---|---|---|
| `COOLANT_TEMP` | °C | Engine coolant temperature. Normal: 80–100°C |
| `INTAKE_TEMP` | °C | Intake air temperature |
| `AMBIENT_AIR_TEMP` | °C | Outside air temperature (if supported) |
| `OIL_TEMP` | °C | Engine oil temperature (if supported) |

### Fuel System

| PID Name | Unit | Description |
|---|---|---|
| `FUEL_STATUS` | — | Open/closed loop status |
| `SHORT_FUEL_TRIM_1` | % | Bank 1 short-term fuel trim. Normal: ±10% |
| `LONG_FUEL_TRIM_1` | % | Bank 1 long-term fuel trim. Normal: ±10% |
| `SHORT_FUEL_TRIM_2` | % | Bank 2 short-term (V engines) |
| `LONG_FUEL_TRIM_2` | % | Bank 2 long-term (V engines) |
| `FUEL_LEVEL` | % | Fuel tank level |
| `FUEL_RAIL_PRESSURE` | kPa | Fuel rail pressure |

### Air / Intake

| PID Name | Unit | Description |
|---|---|---|
| `MAF` | g/s | Mass air flow rate |
| `THROTTLE_POS` | % | Throttle plate position (0=closed, 100=WOT) |
| `BAROMETRIC_PRESSURE` | kPa | Ambient barometric pressure |
| `INTAKE_PRESSURE` | kPa | Intake manifold absolute pressure (MAP) |

### Oxygen Sensors

| PID Name | Unit | Description |
|---|---|---|
| `O2_B1S1` | V | O2 sensor, bank 1, sensor 1 (upstream) |
| `O2_B1S2` | V | O2 sensor, bank 1, sensor 2 (downstream) |
| `O2_B2S1` | V | O2 sensor, bank 2, sensor 1 (V engines) |
| `O2_B2S2` | V | O2 sensor, bank 2, sensor 2 (V engines) |

### Speed & Distance

| PID Name | Unit | Description |
|---|---|---|
| `SPEED` | km/h | Vehicle speed |
| `DISTANCE_SINCE_DTC_CLEAR` | km | Distance traveled since codes were cleared |
| `DISTANCE_W_MIL` | km | Distance traveled with MIL (check engine) on |

### Diagnostics

| PID Name | Unit | Description |
|---|---|---|
| `GET_DTC` | — | Stored diagnostic trouble codes |
| `FREEZE_DTC` | — | DTC that triggered freeze frame |
| `OBD_COMPLIANCE` | — | OBD standard the vehicle conforms to |
| `VIN` | — | Vehicle Identification Number |

---

## Protocol Notes

### ISO 9141-2 (your car)
- Older K-Line protocol, common in late 1990s – mid 2000s vehicles
- Slower communication than CAN bus
- Supports fewer PIDs — `FUEL_LEVEL`, `VIN`, `RUN_TIME` often not exposed
- Use `just discover` to enumerate what your specific ECU reports

### CAN Bus (ISO 15765-4)
- Modern protocol, all US vehicles 2008+
- Faster, supports more PIDs
- VIN, fuel level, and extended sensors typically available

---

## Discover Your Car's PIDs

```bash
just discover
# or:
uv run race2 discover
```

This queries the ECU's PID support bitmaps and reports every sensor your car actually exposes, then reads them all.
