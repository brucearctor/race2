/// Animated arc RPM gauge using CustomPainter.
library;

import 'dart:math' as math;
import 'package:flutter/material.dart';

class RpmGauge extends StatefulWidget {
  final double rpm;
  final double maxRpm;

  const RpmGauge({super.key, required this.rpm, this.maxRpm = 7000});

  @override
  State<RpmGauge> createState() => _RpmGaugeState();
}

class _RpmGaugeState extends State<RpmGauge>
    with SingleTickerProviderStateMixin {
  late AnimationController _ctrl;
  late Animation<double> _anim;
  double _prev = 0;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(
        vsync: this, duration: const Duration(milliseconds: 300));
    _anim = Tween<double>(begin: 0, end: 0).animate(
        CurvedAnimation(parent: _ctrl, curve: Curves.easeOut));
  }

  @override
  void didUpdateWidget(RpmGauge old) {
    super.didUpdateWidget(old);
    if ((widget.rpm - _prev).abs() > 10) {
      _anim = Tween<double>(begin: _prev, end: widget.rpm).animate(
          CurvedAnimation(parent: _ctrl, curve: Curves.easeOut));
      _ctrl.forward(from: 0);
      _prev = widget.rpm;
    }
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _anim,
      builder: (_, __) => CustomPaint(
        painter: _GaugePainter(_anim.value, widget.maxRpm),
        child: SizedBox(
          width: double.infinity,
          height: 180,
          child: Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  widget.rpm.toStringAsFixed(0),
                  style: const TextStyle(
                    fontSize: 48,
                    fontWeight: FontWeight.w800,
                    color: Colors.white,
                    letterSpacing: -2,
                  ),
                ),
                const Text('RPM',
                    style: TextStyle(
                        fontSize: 11,
                        color: Color(0xFF5a5f7a),
                        letterSpacing: 2)),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _GaugePainter extends CustomPainter {
  final double rpm;
  final double maxRpm;
  _GaugePainter(this.rpm, this.maxRpm);

  @override
  void paint(Canvas canvas, Size size) {
    final cx = size.width / 2;
    final cy = size.height - 16;
    final r = math.min(cx, cy) - 12;
    const startAngle = math.pi;
    const sweepAngle = math.pi;
    final pct = (rpm / maxRpm).clamp(0.0, 1.0);

    // Track
    canvas.drawArc(
      Rect.fromCircle(center: Offset(cx, cy), radius: r),
      startAngle, sweepAngle, false,
      Paint()
        ..color = const Color(0xFF1e2235)
        ..style = PaintingStyle.stroke
        ..strokeWidth = 14
        ..strokeCap = StrokeCap.round,
    );

    // Coloured fill
    if (pct > 0) {
      const grad = SweepGradient(
        startAngle: startAngle,
        endAngle: startAngle + sweepAngle,
        colors: [Color(0xFF4ade80), Color(0xFFfbbf24), Color(0xFFf87171)],
        stops: [0.0, 0.6, 1.0],
      );
      final shader = grad.createShader(Rect.fromCircle(center: Offset(cx, cy), radius: r));

      canvas.drawArc(
        Rect.fromCircle(center: Offset(cx, cy), radius: r),
        startAngle, sweepAngle * pct, false,
        Paint()
          ..shader = shader
          ..style = PaintingStyle.stroke
          ..strokeWidth = 14
          ..strokeCap = StrokeCap.round,
      );
    }

    // Tick marks + labels
    final tickPaint = Paint()..strokeWidth = 2..strokeCap = StrokeCap.round;
    const textStyle = TextStyle(fontSize: 10, color: Color(0xFF5a5f7a));
    for (int i = 0; i <= 7; i++) {
      final a = startAngle + (i / 7) * sweepAngle;
      final inner = Offset(cx + (r - 18) * math.cos(a), cy + (r - 18) * math.sin(a));
      final outer = Offset(cx + (r - 8)  * math.cos(a), cy + (r - 8)  * math.sin(a));
      tickPaint.color = i * 1000 <= rpm
          ? const Color(0xFF5a5f7a)
          : const Color(0xFF2e3250);
      canvas.drawLine(inner, outer, tickPaint);

      final lx = cx + (r - 30) * math.cos(a);
      final ly = cy + (r - 30) * math.sin(a);
      final tp = TextPainter(
        text: TextSpan(text: '$i', style: textStyle),
        textDirection: TextDirection.ltr,
      )..layout();
      tp.paint(canvas, Offset(lx - tp.width / 2, ly - tp.height / 2));
    }
  }

  @override
  bool shouldRepaint(_GaugePainter old) => old.rpm != rpm;
}
