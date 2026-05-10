"""Generate realistic sample OBD data for dashboard demo."""

import csv
import json
import math
import random
from datetime import datetime, timedelta
from pathlib import Path


def generate_sample_session(duration_s: int = 300, hz: float = 1.0) -> dict:
    """Generate a realistic 5-minute drive session."""
    random.seed(42)
    rows = []
    start = datetime(2026, 5, 10, 10, 30, 0)
    steps = int(duration_s * hz)

    # Simulate: cold start → warm-up → idle → acceleration → cruise → decel → idle
    def phase(t):
        if t < 30:   return "warmup"
        if t < 60:   return "idle"
        if t < 120:  return "accel"
        if t < 200:  return "cruise"
        if t < 240:  return "decel"
        return "idle"

    coolant = 45.0  # cold start
    ltft1 = 17.97
    ltft2 = 18.75

    for i in range(steps):
        t = i / hz
        p = phase(t)
        ts = start + timedelta(seconds=t)

        # RPM profile
        if p == "warmup": rpm = 1200 + random.gauss(0, 50)
        elif p == "idle":  rpm = 750  + random.gauss(0, 30)
        elif p == "accel": rpm = 750 + (t - 60) * 40 + random.gauss(0, 80)
        elif p == "cruise":rpm = 2500 + random.gauss(0, 100)
        elif p == "decel": rpm = 2500 - (t - 200) * 40 + random.gauss(0, 60)
        else:              rpm = 750  + random.gauss(0, 30)
        rpm = max(700, min(4500, rpm))

        # Speed
        if p in ("warmup", "idle"): speed = 0.0
        elif p == "accel":  speed = min(80, (t - 60) * 1.3 + random.gauss(0, 1))
        elif p == "cruise": speed = 80 + random.gauss(0, 2)
        elif p == "decel":  speed = max(0, 80 - (t - 200) * 2 + random.gauss(0, 1))
        else:               speed = 0.0

        # Coolant warms up
        coolant = min(89, coolant + 0.15 + random.gauss(0, 0.02))

        # Engine load
        if p == "accel":  load = 40 + (t - 60) * 0.3 + random.gauss(0, 3)
        elif p == "cruise":load = 25 + random.gauss(0, 4)
        elif p == "decel": load = max(5, 30 - (t - 200) * 0.5) + random.gauss(0, 2)
        elif p == "warmup":load = 15 + random.gauss(0, 2)
        else:              load = 8  + random.gauss(0, 1)
        load = max(0, min(100, load))

        # MAF correlates with load
        maf = (rpm / 1000) * (load / 100) * 3.5 + random.gauss(0, 0.1)

        # Throttle
        throttle = load * 0.6 + random.gauss(0, 1)
        throttle = max(0, min(100, throttle))

        # Short fuel trim oscillates around 0 in closed loop (after warmup)
        if p == "warmup" or coolant < 75:
            stft1 = 0.0; stft2 = 0.0
        else:
            stft1 = random.gauss(0, 3)
            stft2 = random.gauss(0, 3)

        # O2 B1S1 - upstream, switches fast in closed loop
        if coolant < 75:
            o2_b1s1 = 0.45
        else:
            # Simulate switching ~0.5 Hz
            o2_b1s1 = 0.1 + 0.8 * (0.5 + 0.5 * math.sin(t * 3.14 + random.gauss(0, 0.3)))

        # Timing advance increases with RPM
        timing = 8 + (rpm / 4500) * 20 + random.gauss(0, 1)

        rows.append({
            "timestamp": ts.isoformat(),
            "RPM": round(rpm, 1),
            "SPEED": round(speed, 1),
            "COOLANT_TEMP": round(coolant, 1),
            "ENGINE_LOAD": round(load, 1),
            "MAF": round(maf, 2),
            "THROTTLE_POS": round(throttle, 1),
            "SHORT_FUEL_TRIM_1": round(stft1, 2),
            "LONG_FUEL_TRIM_1": round(ltft1, 2),
            "SHORT_FUEL_TRIM_2": round(stft2, 2),
            "LONG_FUEL_TRIM_2": round(ltft2, 2),
            "O2_B1S1": round(o2_b1s1, 3),
            "TIMING_ADVANCE": round(timing, 1),
            "INTAKE_TEMP": round(35 + coolant * 0.1 + random.gauss(0, 0.5), 1),
        })

    return rows


def write_sample_csv(path: Path):
    rows = generate_sample_session()
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"Sample CSV written → {path}")


def write_sample_snapshot(path: Path):
    snap = {
        "timestamp": "2026-05-10T10:14:44",
        "dtcs": [],
        "sensors": {
            "RPM": "0.0 revolutions_per_minute",
            "SPEED": "0.0 kilometer_per_hour",
            "COOLANT_TEMP": "83 degree_Celsius",
            "INTAKE_TEMP": "51 degree_Celsius",
            "THROTTLE_POS": "0.0 percent",
            "ENGINE_LOAD": "0.0 percent",
            "TIMING_ADVANCE": "0.0 degree",
            "MAF": "0.0 gps",
            "SHORT_FUEL_TRIM_1": "0.0 percent",
            "LONG_FUEL_TRIM_1": "17.96875 percent",
            "SHORT_FUEL_TRIM_2": "0.0 percent",
            "LONG_FUEL_TRIM_2": "18.75 percent",
            "O2_B1S1": "0.455 volt",
            "O2_B1S2": "0.455 volt",
            "O2_B2S1": "0.455 volt",
            "O2_B2S2": "0.455 volt",
            "FUEL_STATUS": "Open loop due to insufficient engine temperature",
            "OBD_COMPLIANCE": "OBD-II as defined by the CARB",
            "DISTANCE_W_MIL": "0.0 kilometer",
            "AIR_STATUS": "From the outside atmosphere or off",
        },
    }
    path.write_text(json.dumps(snap, indent=2))
    print(f"Sample snapshot written → {path}")


if __name__ == "__main__":
    write_sample_csv(Path("sample_session.csv"))
    write_sample_snapshot(Path("sample_snapshot.json"))
