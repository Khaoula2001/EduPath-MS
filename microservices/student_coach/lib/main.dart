import 'package:flutter/material.dart';
import 'screens/login_screen.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'EduPath Student Coach',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF8B80F8),
          primary: const Color(0xFF8B80F8),
          surface: const Color(0xFFF8F9FE),
        ),
        useMaterial3: true,
        scaffoldBackgroundColor: const Color(0xFFF8F9FE),
        textTheme: const TextTheme(
          displayLarge: TextStyle(color: Color(0xFF1A1C24), fontWeight: FontWeight.bold),
          bodyLarge: TextStyle(color: Color(0xFF1A1C24)),
          bodyMedium: TextStyle(color: Color(0xFF4A4D54)),
        ),
        bottomNavigationBarTheme: const BottomNavigationBarThemeData(
          backgroundColor: Colors.white,
          elevation: 10,
        ),
      ),
      home: const LoginScreen(),
    );
  }
}

