/// Main dashboard screen.
library;

import 'package:flutter/material.dart';

import '../obd/obd_service.dart';
import 'fuel_trim_bar.dart';
import 'metric_card.dart';
import 'rpm_gauge.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  final _obd = OBDService();
  OBDStatus _status = OBDStatus.disconnected;
  Map<String, double?> _data = {};

  @override
  void initState() {
    super.initState();
    _obd.statusStream.listen((s) => setState(() => _status = s));
    _obd.dataStream.listen((d) => setState(() => _data = d));
    _obd.start();
  }

  @override
  void dispose() {
    _obd.dispose();
    super.dispose();
  }

  // ── Helpers ──────────────────────────────────────────────────────────────
  String _fmt(String key, {int decimals = 0}) {
    final v = _data[key];
    return v == null ? '—' : v.toStringAsFixed(decimals);
  }

  CardState _coolantState() {
    final v = _data['COOLANT_TEMP'];
    if (v == null) return CardState.normal;
    if (v > 110) return CardState.alert;
    if (v > 100) return CardState.warn;
    return CardState.normal;
  }

  // ── Status chip ───────────────────────────────────────────────────────────
  Widget _statusChip() {
    final (label, color) = switch (_status) {
      OBDStatus.connected    => ('Live', const Color(0xFF4ade80)),
      OBDStatus.connecting   => ('Connecting…', const Color(0xFFfbbf24)),
      OBDStatus.error        => ('No device', const Color(0xFFf87171)),
      OBDStatus.disconnected => ('Disconnected', const Color(0xFF5a5f7a)),
    };
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 8, height: 8,
          decoration: BoxDecoration(
            color: color,
            shape: BoxShape.circle,
            boxShadow: [BoxShadow(color: color.withValues(alpha: 0.6), blurRadius: 6)],
          ),
        ),
        const SizedBox(width: 6),
        Text(label,
            style: TextStyle(fontSize: 12, color: color, fontWeight: FontWeight.w600)),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    final rpm = _data['RPM'] ?? 0.0;

    return Scaffold(
      backgroundColor: const Color(0xFF0a0b0f),
      appBar: AppBar(
        backgroundColor: const Color(0xFF12141c),
        elevation: 0,
        title: const Text('🏎️ race2',
            style: TextStyle(fontWeight: FontWeight.w800, fontSize: 18)),
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 16),
            child: Center(child: _statusChip()),
          ),
        ],
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.only(bottom: 24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // RPM Gauge
              Padding(
                padding: const EdgeInsets.fromLTRB(16, 16, 16, 0),
                child: RpmGauge(rpm: rpm),
              ),

              // Core metrics grid
              Padding(
                padding: const EdgeInsets.all(12),
                child: GridView.count(
                  crossAxisCount: 2,
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  mainAxisSpacing: 10,
                  crossAxisSpacing: 10,
                  childAspectRatio: 1.5,
                  children: [
                    MetricCard(label: 'SPEED', value: _fmt('SPEED'), unit: 'km/h'),
                    MetricCard(
                      label: 'ENGINE LOAD',
                      value: _fmt('ENGINE_LOAD', decimals: 1),
                      unit: '%',
                      state: (_data['ENGINE_LOAD'] ?? 0) > 85
                          ? CardState.alert
                          : (_data['ENGINE_LOAD'] ?? 0) > 70
                              ? CardState.warn
                              : CardState.normal,
                    ),
                    MetricCard(
                      label: 'COOLANT',
                      value: _fmt('COOLANT_TEMP'),
                      unit: '°C',
                      state: _coolantState(),
                    ),
                    MetricCard(
                        label: 'INTAKE', value: _fmt('INTAKE_TEMP'), unit: '°C'),
                    MetricCard(
                        label: 'MAF', value: _fmt('MAF', decimals: 2), unit: 'g/s'),
                    MetricCard(
                        label: 'TIMING',
                        value: _fmt('TIMING_ADVANCE', decimals: 1),
                        unit: '°'),
                  ],
                ),
              ),

              // Fuel trims section
              _sectionTitle('FUEL TRIMS'),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                child: Column(children: [
                  FuelTrimBar(label: 'STFT B1', value: _data['SHORT_FUEL_TRIM_1']),
                  FuelTrimBar(label: 'LTFT B1', value: _data['LONG_FUEL_TRIM_1']),
                  FuelTrimBar(label: 'STFT B2', value: _data['SHORT_FUEL_TRIM_2']),
                  FuelTrimBar(label: 'LTFT B2', value: _data['LONG_FUEL_TRIM_2']),
                ]),
              ),

              // O2 sensors
              _sectionTitle('O2 SENSORS'),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 12),
                child: Row(children: [
                  Expanded(
                    child: MetricCard(
                      label: 'B1 S1 UPSTREAM',
                      value: _fmt('O2_B1S1', decimals: 3),
                      unit: 'V',
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: MetricCard(
                      label: 'B2 S1 UPSTREAM',
                      value: _fmt('O2_B2S1', decimals: 3),
                      unit: 'V',
                    ),
                  ),
                ]),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _sectionTitle(String text) => Padding(
        padding: const EdgeInsets.fromLTRB(16, 20, 16, 8),
        child: Text(text,
            style: const TextStyle(
                fontSize: 10,
                color: Color(0xFF5a5f7a),
                letterSpacing: 2,
                fontWeight: FontWeight.w700)),
      );
}
