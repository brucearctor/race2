/// ELM327 AT command layer — handles init sequence and raw PID exchange.
library;

import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';

import 'package:usb_serial/usb_serial.dart';

class ELM327 {
  UsbPort? _port;
  final _rxBuf = StringBuffer();
  final StreamController<String> _lineCtrl = StreamController.broadcast();

  Stream<String> get lines => _lineCtrl.stream;

  // ── Connect ────────────────────────────────────────────────────────────────
  Future<bool> connect() async {
    final devices = await UsbSerial.listDevices();
    if (devices.isEmpty) return false;

    // Pick first recognised device (FTDI / CP210x / CH340)
    _port = await devices.first.create();
    if (_port == null) return false;

    final ok = await _port!.open();
    if (!ok) return false;

    await _port!.setDTR(true);
    await _port!.setRTS(true);
    await _port!.setPortParameters(
      115200,
      UsbPort.DATABITS_8,
      UsbPort.STOPBITS_1,
      UsbPort.PARITY_NONE,
    );

    // Wire incoming bytes into line buffer
    _port!.inputStream?.listen(_onBytes);

    return await _init();
  }

  void _onBytes(Uint8List data) {
    _rxBuf.write(latin1.decode(data));
    final raw = _rxBuf.toString();
    final lines = raw.split('\r');
    for (var i = 0; i < lines.length - 1; i++) {
      final line = lines[i].trim();
      if (line.isNotEmpty) _lineCtrl.add(line);
    }
    _rxBuf.clear();
    _rxBuf.write(lines.last); // incomplete line
  }

  // ── Init sequence ─────────────────────────────────────────────────────────
  Future<bool> _init() async {
    // Reset and configure
    for (final cmd in ['ATZ', 'ATE0', 'ATL0', 'ATS0', 'ATH0', 'ATSP0']) {
      final resp = await send(cmd, timeoutMs: cmd == 'ATZ' ? 2000 : 500);
      if (cmd == 'ATZ' && !resp.contains('ELM')) return false;
      if (cmd != 'ATZ' && !resp.contains('OK')) return false;
    }
    return true;
  }

  // ── Send / receive ────────────────────────────────────────────────────────
  Future<String> send(String cmd, {int timeoutMs = 1000}) async {
    final bytes = Uint8List.fromList(latin1.encode('$cmd\r'));
    await _port!.write(bytes);

    final buf = StringBuffer();
    try {
      await for (final line in lines.timeout(
        Duration(milliseconds: timeoutMs),
        onTimeout: (sink) => sink.close(),
      )) {
        if (line == '>') break; // prompt = response complete
        buf.writeln(line);
      }
    } catch (_) {}
    return buf.toString().trim();
  }

  // ── Query a raw OBD PID ──────────────────────────────────────────────────
  /// Returns data bytes (after echo stripped), or null on NODATA / timeout.
  Future<List<int>?> queryPID(String request) async {
    final resp = await send(request);
    if (resp.isEmpty || resp.contains('NODATA') || resp.contains('ERROR')) {
      return null;
    }
    // Response looks like "41 0C 0F A0" — strip mode+pid bytes, parse hex
    final hex = resp.replaceAll(RegExp(r'[^0-9A-Fa-f\s]'), '').trim().split(RegExp(r'\s+'));
    if (hex.length < 3) return null;
    // hex[0] = response mode (41), hex[1] = pid echo → data starts at hex[2]
    return hex.skip(2).map((h) => int.parse(h, radix: 16)).toList();
  }

  Future<void> close() async {
    await _port?.close();
    await _lineCtrl.close();
  }
}
