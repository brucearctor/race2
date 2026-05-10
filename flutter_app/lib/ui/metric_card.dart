/// Metric card widget — shows a single sensor value with label, value, unit.
library;

import 'package:flutter/material.dart';

class MetricCard extends StatelessWidget {
  final String label;
  final String value;
  final String unit;
  final CardState state;

  const MetricCard({
    super.key,
    required this.label,
    required this.value,
    required this.unit,
    this.state = CardState.normal,
  });

  @override
  Widget build(BuildContext context) {
    final borderColor = switch (state) {
      CardState.warn  => const Color(0xFFfbbf24),
      CardState.alert => const Color(0xFFf87171),
      CardState.normal => const Color(0xFF1e2235),
    };
    final valueColor = switch (state) {
      CardState.warn  => const Color(0xFFfbbf24),
      CardState.alert => const Color(0xFFf87171),
      CardState.normal => Colors.white,
    };

    return AnimatedContainer(
      duration: const Duration(milliseconds: 300),
      decoration: BoxDecoration(
        color: const Color(0xFF12141c),
        border: Border.all(color: borderColor, width: 1.5),
        borderRadius: BorderRadius.circular(14),
      ),
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label,
              style: const TextStyle(
                  fontSize: 10,
                  color: Color(0xFF5a5f7a),
                  letterSpacing: 1.2,
                  fontWeight: FontWeight.w600)),
          const SizedBox(height: 4),
          Text(value,
              style: TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.w800,
                  color: valueColor,
                  fontFeatures: const [FontFeature.tabularFigures()])),
          Text(unit,
              style: const TextStyle(
                  fontSize: 11, color: Color(0xFF5a5f7a))),
        ],
      ),
    );
  }
}

enum CardState { normal, warn, alert }
