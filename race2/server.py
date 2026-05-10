"""
race2 live streaming server.

FastAPI + SSE: reads OBD in a background thread, broadcasts JSON
events to every connected browser client at ~1 Hz.

Usage:
    uv run race2 live              # real OBD hardware
    uv run race2 live --demo       # simulated data, no car needed
"""

from __future__ import annotations

import asyncio
import json
import logging
import math
import random
import threading
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from sse_starlette.sse import EventSourceResponse

log = logging.getLogger("race2.server")

# ── Shared state ──────────────────────────────────────────────────────────────

_latest: dict = {}
_subscribers: list[asyncio.Queue] = []
_lock = threading.Lock()

COMMANDS_WANTED = [
    "RPM", "SPEED", "COOLANT_TEMP", "ENGINE_LOAD", "MAF",
    "THROTTLE_POS", "SHORT_FUEL_TRIM_1", "LONG_FUEL_TRIM_1",
    "SHORT_FUEL_TRIM_2", "LONG_FUEL_TRIM_2",
    "O2_B1S1", "O2_B2S1", "TIMING_ADVANCE", "INTAKE_TEMP",
]


def _broadcast(data: dict) -> None:
    """Push latest data to every SSE subscriber queue (thread-safe)."""
    global _latest
    with _lock:
        _latest = data
        dead = []
        for q in _subscribers:
            try:
                q.put_nowait(data)
            except asyncio.QueueFull:
                dead.append(q)
        for q in dead:
            _subscribers.remove(q)


# ── OBD reader thread ─────────────────────────────────────────────────────────

def _obd_thread(port: str, baud: int, stop: threading.Event) -> None:
    import obd
    conn = None
    while not stop.is_set():
        try:
            if conn is None or not conn.is_connected():
                log.info("Connecting to OBD at %s @ %d…", port, baud)
                conn = obd.OBD(portstr=port, baudrate=baud, fast=False, timeout=10)
                if not conn.is_connected():
                    log.warning("OBD not connected, retrying in 5s")
                    time.sleep(5)
                    continue
                log.info("OBD connected — protocol: %s", conn.protocol_name())

            snapshot: dict = {"_ts": time.time(), "_connected": True}
            for name in COMMANDS_WANTED:
                cmd = getattr(obd.commands, name, None)
                if cmd is None:
                    continue
                try:
                    resp = conn.query(cmd)
                    snapshot[name] = float(str(resp.value).split()[0]) if not resp.is_null() else None
                except Exception:
                    snapshot[name] = None
            _broadcast(snapshot)

        except Exception as exc:
            log.error("OBD error: %s", exc)
            conn = None
            _broadcast({"_connected": False, "_ts": time.time()})
            time.sleep(5)

        time.sleep(1)

    if conn:
        conn.close()


# ── Demo data thread ──────────────────────────────────────────────────────────

def _demo_thread(stop: threading.Event) -> None:
    t = 0.0
    coolant = 45.0
    while not stop.is_set():
        phase = "idle" if t < 30 else ("accel" if t < 90 else ("cruise" if t < 180 else "decel"))
        rpm = {"idle": 750, "accel": 750 + (t-30)*30, "cruise": 2500, "decel": max(750, 2500-(t-180)*20)}[phase]
        rpm = max(700, min(4000, rpm + random.gauss(0, 30)))
        speed = {"idle": 0, "accel": min(80,(t-30)*1.2), "cruise": 80, "decel": max(0,80-(t-180)*2)}[phase]
        coolant = min(90, coolant + 0.2 + random.gauss(0, 0.05))
        load = max(5, min(100, rpm/40 + random.gauss(0, 2)))
        o2 = 0.45 if coolant < 75 else round(0.1 + 0.8*(0.5 + 0.5*math.sin(t*3.14)), 3)
        _broadcast({
            "_ts": time.time(), "_connected": True, "_demo": True,
            "RPM": round(rpm, 1),
            "SPEED": round(speed, 1),
            "COOLANT_TEMP": round(coolant, 1),
            "ENGINE_LOAD": round(load, 1),
            "MAF": round((rpm/1000)*(load/100)*3.2 + random.gauss(0,0.05), 2),
            "THROTTLE_POS": round(load*0.6 + random.gauss(0,0.5), 1),
            "SHORT_FUEL_TRIM_1": round(random.gauss(0, 2) if coolant > 75 else 0, 2),
            "LONG_FUEL_TRIM_1": 17.97,
            "SHORT_FUEL_TRIM_2": round(random.gauss(0, 2) if coolant > 75 else 0, 2),
            "LONG_FUEL_TRIM_2": 18.75,
            "O2_B1S1": o2,
            "O2_B2S1": round(o2 + random.gauss(0, 0.02), 3),
            "TIMING_ADVANCE": round(8 + (rpm/4000)*20, 1),
            "INTAKE_TEMP": round(35 + coolant*0.1 + random.gauss(0, 0.3), 1),
        })
        t = (t + 1) % 240
        time.sleep(1)


# ── FastAPI app ───────────────────────────────────────────────────────────────

_stop_event = threading.Event()
_STATIC = Path(__file__).parent / "static"


def create_app(port: str, baud: int, demo: bool) -> FastAPI:

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        _stop_event.clear()
        target = _demo_thread if demo else lambda s: _obd_thread(port, baud, s)
        t = threading.Thread(target=target, args=(_stop_event,), daemon=True)
        t.start()
        log.info("race2 live server started (demo=%s)", demo)
        yield
        _stop_event.set()
        t.join(timeout=5)

    app = FastAPI(title="race2 live", lifespan=lifespan)
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

    @app.get("/", response_class=HTMLResponse)
    async def index():
        html = (_STATIC / "live.html").read_text()
        return HTMLResponse(html)

    @app.get("/stream")
    async def stream(request: Request):
        q: asyncio.Queue = asyncio.Queue(maxsize=10)
        with _lock:
            _subscribers.append(q)
            if _latest:
                await q.put(_latest)

        async def generator():
            try:
                while True:
                    if await request.is_disconnected():
                        break
                    try:
                        data = await asyncio.wait_for(q.get(), timeout=2.0)
                        yield {"data": json.dumps(data)}
                    except asyncio.TimeoutError:
                        yield {"comment": "ping"}  # keep-alive
            finally:
                with _lock:
                    if q in _subscribers:
                        _subscribers.remove(q)

        return EventSourceResponse(generator())

    @app.get("/snapshot")
    async def snapshot():
        with _lock:
            return _latest

    return app


def serve(port_str: str, baud: int, demo: bool, host: str, http_port: int) -> None:
    import socket
    app = create_app(port_str, baud, demo)
    # Print all network IPs so user knows what to type on the phone
    ips = []
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None):
            ip = info[4][0]
            if ip.startswith(("192.", "10.", "172.")):
                ips.append(ip)
    except Exception:
        pass

    print("\n🏎️  race2 live server")
    print(f"   Local:   http://localhost:{http_port}")
    for ip in set(ips):
        print(f"   Network: http://{ip}:{http_port}  ← open this on your Pixel")
    print(f"\n   {'[DEMO MODE]' if demo else '[REAL OBD]'}  Streaming at ~1 Hz\n")
    uvicorn.run(app, host=host, port=http_port, log_level="warning")
