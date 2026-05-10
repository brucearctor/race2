# Getting Started

## Hardware Setup

### What You Need

- **OBDLink EX** adapter (comes with USB cable)
- A vehicle with an OBD-II port (all US cars 1996+, EU cars 2001+)
- Your Mac with a USB-A or USB-C port (use an adapter if needed)

### Physical Connection

```
[Car OBD-II Port] ←—— [OBDLink EX] ←—USB——→ [Your Mac]
  (under dash,              ↑
  driver's side)     powered by car,
                     NOT by USB
```

> **Important:** The OBDLink EX draws power from the car's OBD-II port.
> The USB cable only carries data. The car key must be in the **ON** position
> (or engine running) before the adapter will respond.

### Finding Your OBD-II Port

The OBD-II port is almost always located **under the dashboard on the driver's side**, often near the steering column. It's a trapezoidal 16-pin connector.

---

## macOS Driver

The OBDLink EX uses a standard USB-to-serial chip. On macOS 12+, the driver loads automatically. You can verify the device is recognized:

```bash
ls /dev/cu.usbserial-*
# Should show something like: /dev/cu.usbserial-223230327733
```

If nothing appears, download the driver from [obdlink.com/drivers](https://www.obdlink.com/drivers/).

---

## Software Setup

```bash
# 1. Clone the repo
git clone https://github.com/brucearctor/race2.git
cd race2

# 2. Enter the Nix dev shell
nix develop
# This installs: Python 3.12, uv, lefthook, ruff, just

# 3. Install Python deps
just install

# 4. Install git hooks
lefthook install
```

---

## First Connection

1. Plug the OBDLink EX into the car's OBD-II port
2. Run a USB cable from the OBDLink to your Mac
3. Turn the car key to the **ON** position (don't need to start the engine)
4. Verify the adapter is visible: `ls /dev/cu.usbserial-*`
5. Check for fault codes: `just dtc`

**Expected output:**
```
Connecting to /dev/cu.usbserial-XXXXXXXX @ 115200 baud...
Connected! Protocol: ISO 9141-2
✅ No fault codes found!
```

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| No `/dev/cu.usbserial-*` device | Driver not loaded | Install from obdlink.com/drivers |
| `ATE0 did not return OK` | Car not powered | Turn key to ON position |
| `Failed to read port` | Wrong baud rate | Use `--baud 115200` |
| All values show `N/A` | PID not supported | Run `just discover` to see what your car supports |
| Connection drops mid-session | USB power issue | Use a powered USB hub |
