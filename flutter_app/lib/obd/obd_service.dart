/// OBD service — polls PIDs in a loop and exposes a Stream<Map<String,double?>>.
library;

import 'dart:async';

import 'package:usb_serial/usb_serial.dart';

import 'elm327.dart';
import 'pids.dart';

enum OBDStatus { disconnected, connecting, connected, error }

class OBDService {
  final _elm = ELM327();
  final _dataCtrl = StreamController<Map<String, double?>>.broadcast();
  final _statusCtrl = StreamController<OBDStatus>.broadcast();

  Stream<Map<String, double?>> get dataStream => _dataCtrl.stream;
  Stream<OBDStatus> get statusStream => _statusCtrl.stream;

  Map<String, double?> _latest = {};
  Map<String, double?> get latest => Map.unmodifiable(_latest);

  Timer? _pollTimer;
  bool _running = false;

  // ── Start / stop ──────────────────────────────────────────────────────────

  Future<void> start() async {
    if (_running) return;
    _running = true;
    _emit(OBDStatus.connecting);

    // Watch for USB attach/detach
    UsbSerial.usbEventStream?.listen((event) {
      if (event.event == UsbEvent.ACTION_USB_ATTACHED) _reconnect();
      if (event.event == UsbEvent.ACTION_USB_DETACHED) _onDisconnect();
    });

    await _reconnect();
  }

  Future<void> stop() async {
    _running = false;
    _pollTimer?.cancel();
    await _elm.close();
    _emit(OBDStatus.disconnected);
  }

  // ── Internal ──────────────────────────────────────────────────────────────

  Future<void> _reconnect() async {
    _pollTimer?.cancel();
    _emit(OBDStatus.connecting);

    final ok = await _elm.connect();
    if (!ok) {
      _emit(OBDStatus.error);
      // Retry after 5 s
      await Future.delayed(const Duration(seconds: 5));
      if (_running) _reconnect();
      return;
    }

    _emit(OBDStatus.connected);
    _pollTimer = Timer.periodic(const Duration(seconds: 1), (_) => _poll());
  }

  void _onDisconnect() {
    _pollTimer?.cancel();
    _emit(OBDStatus.disconnected);
    if (_running) {
      Future.delayed(const Duration(seconds: 2), _reconnect);
    }
  }

  Future<void> _poll() async {
    final snap = <String, double?>{};
    for (final pid in kPIDs) {
      try {
        final bytes = await _elm.queryPID(pid.request);
        snap[pid.name] = bytes != null ? pid.parse(bytes) : null;
      } catch (_) {
        snap[pid.name] = null;
      }
    }
    _latest = snap;
    if (!_dataCtrl.isClosed) _dataCtrl.add(Map.from(snap));
  }

  void _emit(OBDStatus s) {
    if (!_statusCtrl.isClosed) _statusCtrl.add(s);
  }

  void dispose() {
    _pollTimer?.cancel();
    _dataCtrl.close();
    _statusCtrl.close();
  }
}
