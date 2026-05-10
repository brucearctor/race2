"""OBD connection and query helpers."""

from __future__ import annotations

import obd
from rich.console import Console

console = Console()

DEFAULT_PORT = "/dev/cu.usbserial-223230327733"
DEFAULT_BAUD = 38400

SENSOR_COMMANDS = [
    obd.commands.RPM,
    obd.commands.SPEED,
    obd.commands.COOLANT_TEMP,
    obd.commands.INTAKE_TEMP,
    obd.commands.THROTTLE_POS,
    obd.commands.ENGINE_LOAD,
    obd.commands.FUEL_LEVEL,
    obd.commands.BAROMETRIC_PRESSURE,
    obd.commands.TIMING_ADVANCE,
    obd.commands.MAF,
    obd.commands.SHORT_FUEL_TRIM_1,
    obd.commands.LONG_FUEL_TRIM_1,
    obd.commands.O2_B1S1,
    obd.commands.RUN_TIME,
    obd.commands.DISTANCE_SINCE_DTC_CLEAR,
    obd.commands.FUEL_STATUS,
    obd.commands.OBD_COMPLIANCE,
    obd.commands.VIN,
]


def connect(port: str = DEFAULT_PORT, baud: int = DEFAULT_BAUD) -> obd.OBD:
    """Connect to the OBD adapter and return the connection."""
    console.print(f"[bold cyan]Connecting to[/] {port} @ {baud} baud...")
    connection = obd.OBD(portstr=port, baudrate=baud, fast=False, timeout=30)
    if not connection.is_connected():
        console.print(
            "[bold red]ERROR:[/] Could not connect.\n"
            "  • Is OBDLink EX plugged into the OBD port?\n"
            "  • Is the engine on (or key-on)?\n"
            "  • Is the USB connected to your Mac?"
        )
        raise ConnectionError("OBD adapter not found or not responding.")
    console.print(f"[bold green]Connected![/] Protocol: {connection.protocol_name()}")
    return connection


def read_dtcs(connection: obd.OBD) -> list[tuple[str, str]]:
    """Query stored diagnostic trouble codes."""
    response = connection.query(obd.commands.GET_DTC)
    return response.value or []


def read_snapshot(connection: obd.OBD) -> dict[str, str | None]:
    """Read all sensor values in a single pass and return as a dict."""
    data: dict[str, str | None] = {}
    for cmd in SENSOR_COMMANDS:
        try:
            resp = connection.query(cmd)
            data[cmd.name] = str(resp.value) if not resp.is_null() else None
        except Exception:  # noqa: BLE001
            data[cmd.name] = None
    return data
