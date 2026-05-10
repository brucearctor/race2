import 'package:flutter_test/flutter_test.dart';
import 'package:race2_app/main.dart';

void main() {
  testWidgets('App renders dashboard', (WidgetTester tester) async {
    await tester.pumpWidget(const Race2App());
    expect(find.text('🏎️ race2'), findsOneWidget);
  });
}
