"""Tests for race2 OBD client helpers."""

from unittest.mock import MagicMock, patch

import obd

from race2.obd_client import read_dtcs, read_snapshot


def _make_mock_connection(supported_values: dict) -> MagicMock:
    conn = MagicMock()
    conn.is_connected.return_value = True
    conn.protocol_name.return_value = "ISO 15765-4 (CAN 11/500)"

    def query_side_effect(cmd):
        resp = MagicMock()
        if cmd.name in supported_values:
            resp.is_null.return_value = False
            resp.value = supported_values[cmd.name]
        else:
            resp.is_null.return_value = True
            resp.value = None
        return resp

    conn.query.side_effect = query_side_effect
    return conn


def test_read_dtcs_no_codes():
    conn = MagicMock()
    resp = MagicMock()
    resp.value = []
    conn.query.return_value = resp
    assert read_dtcs(conn) == []


def test_read_dtcs_with_codes():
    conn = MagicMock()
    resp = MagicMock()
    resp.value = [("P0300", "Random/Multiple Cylinder Misfire Detected")]
    conn.query.return_value = resp
    codes = read_dtcs(conn)
    assert len(codes) == 1
    assert codes[0][0] == "P0300"


def test_read_snapshot_returns_supported_values():
    conn = _make_mock_connection({"RPM": "2500 rpm", "SPEED": "60 kph"})
    data = read_snapshot(conn)
    assert data["RPM"] == "2500 rpm"
    assert data["SPEED"] == "60 kph"


def test_read_snapshot_null_values_are_none():
    conn = _make_mock_connection({})
    data = read_snapshot(conn)
    # All unsupported sensors should be None
    assert all(v is None for v in data.values())
