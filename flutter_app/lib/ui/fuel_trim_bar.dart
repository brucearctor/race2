/// Fuel trim bar — bidirectional bar centred at 0%, coloured by severity.
library;

import 'package:flutter/material.dart';

class FuelTrimBar extends StatelessWidget {
  final String label;
  final double? value;

  const FuelTrimBar({super.key, required this.label, this.value});

  @override
  Widget build(BuildContext context) {
    final v = value ?? 0.0;
    final warn = v.abs() > 10;
    final color = warn ? const Color(0xFFfbbf24) : const Color(0xFF4ade80);
    final pct = (v.abs() / 25.0).clamp(0.0, 1.0); // ±25% = full half

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          SizedBox(
            width: 72,
            child: Text(label,
                style: const TextStyle(
                    fontSize: 11, color: Color(0xFF5a5f7a))),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: ClipRRect(
              borderRadius: BorderRadius.circular(4),
              child: SizedBox(
                height: 8,
                child: CustomPaint(
                  painter: _TrimPainter(pct, v >= 0, color),
                ),
              ),
            ),
          ),
          const SizedBox(width: 8),
          SizedBox(
            width: 56,
            child: Text(
              value == null
                  ? '—'
                  : '${v >= 0 ? '+' : ''}${v.toStringAsFixed(1)}%',
              textAlign: TextAlign.right,
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w600,
                color: color,
                fontFeatures: const [FontFeature.tabularFigures()],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _TrimPainter extends CustomPainter {
  final double pct;
  final bool positive;
  final Color color;
  _TrimPainter(this.pct, this.positive, this.color);

  @override
  void paint(Canvas canvas, Size size) {
    // Track
    canvas.drawRect(Rect.fromLTWH(0, 0, size.width, size.height),
        Paint()..color = const Color(0xFF1e2235));

    // Centre line
    canvas.drawRect(
        Rect.fromLTWH(size.width / 2 - 0.5, 0, 1, size.height),
        Paint()..color = const Color(0xFF2e3250));

    // Fill
    final half = size.width / 2;
    final fillW = pct * half;
    final left = positive ? half : half - fillW;
    canvas.drawRRect(
      RRect.fromRectAndRadius(
          Rect.fromLTWH(left, 0, fillW, size.height),
          const Radius.circular(4)),
      Paint()..color = color,
    );
  }

  @override
  bool shouldRepaint(_TrimPainter old) =>
      old.pct != pct || old.positive != positive || old.color != color;
}
