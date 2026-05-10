/// OBD-II PID definitions and hex response parsers.
library;

class OBDFrame {
  final String name;
  final double? value;
  final String unit;

  const OBDFrame({required this.name, this.value, required this.unit});

  @override
  String toString() => '$name: ${value?.toStringAsFixed(1) ?? "—"} $unit';
}

class PIDDef {
  final int mode;
  final int pid;
  final String name;
  final String unit;
  final double Function(List<int> bytes) parse;

  const PIDDef({
    required this.mode,
    required this.pid,
    required this.name,
    required this.unit,
    required this.parse,
  });

  String get request => '${mode.toRadixString(16).padLeft(2, '0').toUpperCase()}'
      '${pid.toRadixString(16).padLeft(2, '0').toUpperCase()}';
}

/// All PIDs we want to query. Parser receives only the data bytes (after mode+pid echo).
final List<PIDDef> kPIDs = [
  PIDDef(
    mode: 0x01, pid: 0x0C, name: 'RPM', unit: 'rpm',
    parse: (b) => ((b[0] * 256 + b[1]) / 4.0),
  ),
  PIDDef(
    mode: 0x01, pid: 0x0D, name: 'SPEED', unit: 'km/h',
    parse: (b) => b[0].toDouble(),
  ),
  PIDDef(
    mode: 0x01, pid: 0x05, name: 'COOLANT_TEMP', unit: '°C',
    parse: (b) => (b[0] - 40).toDouble(),
  ),
  PIDDef(
    mode: 0x01, pid: 0x0F, name: 'INTAKE_TEMP', unit: '°C',
    parse: (b) => (b[0] - 40).toDouble(),
  ),
  PIDDef(
    mode: 0x01, pid: 0x04, name: 'ENGINE_LOAD', unit: '%',
    parse: (b) => b[0] * 100.0 / 255.0,
  ),
  PIDDef(
    mode: 0x01, pid: 0x11, name: 'THROTTLE_POS', unit: '%',
    parse: (b) => b[0] * 100.0 / 255.0,
  ),
  PIDDef(
    mode: 0x01, pid: 0x10, name: 'MAF', unit: 'g/s',
    parse: (b) => (b[0] * 256 + b[1]) / 100.0,
  ),
  PIDDef(
    mode: 0x01, pid: 0x0E, name: 'TIMING_ADVANCE', unit: '°',
    parse: (b) => (b[0] / 2.0) - 64.0,
  ),
  PIDDef(
    mode: 0x01, pid: 0x06, name: 'SHORT_FUEL_TRIM_1', unit: '%',
    parse: (b) => (b[0] - 128) * 100.0 / 128.0,
  ),
  PIDDef(
    mode: 0x01, pid: 0x07, name: 'LONG_FUEL_TRIM_1', unit: '%',
    parse: (b) => (b[0] - 128) * 100.0 / 128.0,
  ),
  PIDDef(
    mode: 0x01, pid: 0x08, name: 'SHORT_FUEL_TRIM_2', unit: '%',
    parse: (b) => (b[0] - 128) * 100.0 / 128.0,
  ),
  PIDDef(
    mode: 0x01, pid: 0x09, name: 'LONG_FUEL_TRIM_2', unit: '%',
    parse: (b) => (b[0] - 128) * 100.0 / 128.0,
  ),
  PIDDef(
    mode: 0x01, pid: 0x14, name: 'O2_B1S1', unit: 'V',
    parse: (b) => b[0] / 200.0,
  ),
  PIDDef(
    mode: 0x01, pid: 0x18, name: 'O2_B2S1', unit: 'V',
    parse: (b) => b[0] / 200.0,
  ),
];
