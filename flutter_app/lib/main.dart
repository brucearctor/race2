import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import 'ui/dashboard.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  // Lock to portrait — can be removed if landscape wanted
  SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
    DeviceOrientation.portraitDown,
  ]);
  SystemChrome.setSystemUIOverlayStyle(const SystemUiOverlayStyle(
    statusBarColor: Colors.transparent,
    statusBarIconBrightness: Brightness.light,
  ));
  runApp(const Race2App());
}

class Race2App extends StatelessWidget {
  const Race2App({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'race2',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF6c72f5),
          brightness: Brightness.dark,
        ),
        useMaterial3: true,
        scaffoldBackgroundColor: const Color(0xFF0a0b0f),
        appBarTheme: const AppBarTheme(
          backgroundColor: Color(0xFF12141c),
          foregroundColor: Colors.white,
          surfaceTintColor: Colors.transparent,
        ),
        fontFamily: 'Roboto',
      ),
      home: const DashboardScreen(),
    );
  }
}
