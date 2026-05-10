"""CLI entry point for race2."""

from __future__ import annotations

import csv
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import click
import obd
from rich.console import Console
from rich.table import Table

from race2.obd_client import (
    DEFAULT_BAUD,
    DEFAULT_PORT,
    SENSOR_COMMANDS,
    connect,
    read_dtcs,
    read_snapshot,
)
from race2 import server as _server

console = Console()


@click.group()
@click.option("--port", default=DEFAULT_PORT, show_default=True, help="Serial port of OBD adapter.")
@click.option("--baud", default=DEFAULT_BAUD, show_default=True, help="Baud rate.")
@click.pass_context
def main(ctx: click.Context, port: str, baud: int) -> None:
    """🏎️  race2 — OBD-II vehicle data logger."""
    ctx.ensure_object(dict)
    ctx.obj["port"] = port
    ctx.obj["baud"] = baud


@main.command()
@click.pass_context
def dtc(ctx: click.Context) -> None:
    """Read and display diagnostic trouble codes (DTCs)."""
    conn = connect(ctx.obj["port"], ctx.obj["baud"])
    codes = read_dtcs(conn)
    conn.close()

    if not codes:
        console.print("[bold green]✅ No fault codes found![/]")
        return

    table = Table(title="Diagnostic Trouble Codes", show_header=True)
    table.add_column("Code", style="bold red")
    table.add_column("Description")
    for code, desc in codes:
        table.add_row(code, desc)
    console.print(table)


@main.command()
@click.option("--out", "-o", default=None, help="Optional JSON output file.")
@click.pass_context
def snapshot(ctx: click.Context, out: str | None) -> None:
    """Take a one-shot snapshot of all sensor values."""
    conn = connect(ctx.obj["port"], ctx.obj["baud"])
    dtcs = read_dtcs(conn)
    data = read_snapshot(conn)
    conn.close()

    # Pretty-print table
    table = Table(title="Sensor Snapshot", show_header=True)
    table.add_column("Sensor", style="cyan")
    table.add_column("Value", style="yellow")
    for k, v in data.items():
        table.add_row(k, v or "[dim]N/A[/dim]")
    console.print(table)

    if dtcs:
        console.print(f"\n[bold red]⚠️  Active DTCs:[/] {[c for c, _ in dtcs]}")

    # Save JSON
    out_path = Path(out) if out else Path(f"obd_snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    payload = {"timestamp": datetime.now().isoformat(), "dtcs": [str(d) for d in dtcs], "sensors": data}
    out_path.write_text(json.dumps(payload, indent=2))
    console.print(f"\n[dim]Saved → {out_path}[/dim]")


@main.command()
@click.option("--interval", "-i", default=1.0, show_default=True, help="Sampling interval (seconds).")
@click.option("--duration", "-d", default=60, show_default=True, help="Recording duration (seconds).")
@click.option("--out", "-o", default=None, help="Output CSV file path.")
@click.pass_context
def record(ctx: click.Context, interval: float, duration: int, out: str | None) -> None:
    """Stream live sensor data to a CSV file."""
    conn = connect(ctx.obj["port"], ctx.obj["baud"])

    live_cmds = [
        obd.commands.RPM,
        obd.commands.SPEED,
        obd.commands.COOLANT_TEMP,
        obd.commands.THROTTLE_POS,
        obd.commands.ENGINE_LOAD,
        obd.commands.FUEL_LEVEL,
    ]
    supported = [c for c in live_cmds if conn.supports(c)]

    out_path = Path(out) if out else Path(f"obd_live_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    console.print(f"[bold]Recording {duration}s → {out_path}[/]  (Ctrl+C to stop early)")

    with out_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp"] + [c.name for c in supported])

        start = time.monotonic()
        try:
            while time.monotonic() - start < duration:
                row = [datetime.now().isoformat()]
                parts = []
                for cmd in supported:
                    resp = conn.query(cmd)
                    val = str(resp.value) if not resp.is_null() else ""
                    row.append(val)
                    parts.append(f"{cmd.name}={val}")
                writer.writerow(row)
                f.flush()
                console.print(f"  {' | '.join(parts)}")
                time.sleep(interval)
        except KeyboardInterrupt:
            console.print("\n[yellow]Stopped early.[/]")

    conn.close()
    console.print(f"\n[bold green]Done![/] Saved → {out_path}")


@main.command()
@click.option("--out", "-o", default=None, help="Optional JSON output file.")
@click.pass_context
def discover(ctx: click.Context, out: str | None) -> None:
    """Query every PID the ECU reports as supported — finds hidden data."""
    conn = connect(ctx.obj["port"], ctx.obj["baud"])

    supported = sorted(conn.supported_commands, key=lambda c: c.name)
    console.print(f"\n[bold cyan]ECU supports {len(supported)} PIDs[/]\n")

    table = Table(title="All Supported Sensors", show_header=True)
    table.add_column("PID", style="dim")
    table.add_column("Name", style="cyan")
    table.add_column("Value", style="yellow")
    table.add_column("Description")

    data: dict[str, str | None] = {}
    for cmd in supported:
        # Skip meta/control commands (mode != 1 and mode != 9)
        if not hasattr(cmd, "mode") or cmd.mode not in (1, 9):
            continue
        try:
            resp = conn.query(cmd)
            val = str(resp.value) if not resp.is_null() else None
        except Exception:  # noqa: BLE001
            val = None
        data[cmd.name] = val
        pid_hex = f"{cmd.mode:02X}{cmd.pid:02X}" if hasattr(cmd, "pid") else "—"
        table.add_row(
            pid_hex,
            cmd.name,
            val or "[dim]N/A[/dim]",
            cmd.desc if hasattr(cmd, "desc") else "",
        )

    console.print(table)

    out_path = Path(out) if out else Path(f"obd_discover_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    payload = {"timestamp": datetime.now().isoformat(), "pid_count": len(supported), "sensors": data}
    out_path.write_text(json.dumps(payload, indent=2))
    console.print(f"\n[dim]Saved → {out_path}[/dim]")

    conn.close()


@main.command()
@click.option("--demo", is_flag=True, help="Stream simulated data — no car needed.")
@click.option("--host", default="0.0.0.0", show_default=True, help="Bind address.")
@click.option("--http-port", default=8000, show_default=True, help="HTTP port.")
@click.pass_context
def live(ctx: click.Context, demo: bool, host: str, http_port: int) -> None:
    """Start live SSE server → open in any browser on your network (or Pixel phone)."""
    _server.serve(
        port_str=ctx.obj["port"],
        baud=ctx.obj["baud"],
        demo=demo,
        host=host,
        http_port=http_port,
    )
