# Interpreting Your Data

## Fuel Trims — The Most Telling Metric

Fuel trims are the ECU's real-time corrections to the air/fuel mixture. They're one of the best indicators of engine health.

### Short-Term Fuel Trim (STFT)

- **What it is:** Instant, second-by-second correction
- **Normal range:** ±10%
- **Positive value:** ECU adding fuel (running lean)
- **Negative value:** ECU removing fuel (running rich)

### Long-Term Fuel Trim (LTFT)

- **What it is:** Averaged correction the ECU has learned over time
- **Normal range:** ±10%
- **Important:** This persists even after the engine is off

### Your Reading: LTFT = +17.97%

> ⚠️ **This is elevated.** The ECU is consistently adding ~18% more fuel than expected, meaning the engine is running lean.

**Common causes of high positive LTFT:**

| Cause | How to Diagnose |
|---|---|
| Vacuum leak | Listen for hissing at idle; spray carb cleaner near intake manifold gaskets |
| Dirty/failing MAF sensor | Clean with MAF cleaner spray; STFT should drop |
| Weak fuel injectors | Compare LTFT at idle vs. high RPM |
| Clogged fuel filter | Check fuel pressure |
| O2 sensor degrading | Compare O2 voltage oscillation speed |

**Rule of thumb:**
- LTFT elevated only at **idle** → likely vacuum leak
- LTFT elevated at **all RPMs** → likely MAF or fuel delivery issue

---

## O2 Sensor

| Reading | Meaning |
|---|---|
| Rapidly switching 0.1V–0.9V | Healthy sensor, closed-loop operation |
| Stuck low (~0.1–0.2V) | Running lean or dead sensor |
| Stuck high (~0.8–0.9V) | Running rich or dead sensor |
| Slow switching | Sensor degrading (lazy O2) |

**Your reading: 0.455V** — This was captured with the engine not running (key-on only), so it's not meaningful yet. Capture with engine running for a real reading.

---

## Coolant Temperature

| Range | Meaning |
|---|---|
| < 70°C | Engine still warming up |
| 80–100°C | Normal operating temperature |
| > 110°C | Overheating — investigate immediately |

**Your reading: 84°C** — Normal. Engine was warm from recent use.

---

## Fuel Status

| Status | Meaning |
|---|---|
| `Open loop due to insufficient engine temperature` | Engine warming up; ECU ignoring O2 sensor |
| `Closed loop, using O2 sensor` | Normal operation; ECU using O2 feedback |
| `Open loop due to detected system fault` | ⚠️ Problem — check DTCs |

---

## Engine Load

Percentage of maximum possible torque. Useful for:
- Tracking how hard you're working the engine
- Identifying inefficiencies (high load at low speed)
- Correlating with fuel consumption estimates

---

## MAF (Mass Airflow)

Measured in grams per second. Correlates with engine load and can be used to estimate fuel consumption:

```
Fuel flow (L/hr) ≈ MAF × 3600 / (14.7 × 750)
```

A value of 0.0 g/s at idle indicates the engine was not running during the snapshot.

---

## Protocol: ISO 9141-2

Your car uses the **ISO 9141-2** protocol (also called K-Line). This is common in:
- Late 1990s – mid 2000s European and Asian vehicles
- Some domestic vehicles from the same era

ISO 9141-2 is slower than modern CAN bus protocols and supports fewer PIDs than newer vehicles. Use `just discover` to see exactly what your car exposes.
