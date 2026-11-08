import 'package:flutter/material.dart';

/// Centralized color palette for the Smart Truck & Parking Assistant.
/// Adheres to Material Design 3 and truck safety status color conventions.
class AppColors {
  AppColors._();

  // --- Brand Colors ---
  /// Dark Navy primary brand color.
  static const Color primary = Color(0xFF0A1628);

  /// Slightly lighter navy for cards, elevated surfaces, and headers.
  static const Color primaryLight = Color(0xFF1B2B44);

  /// Deep brand dark for container accents.
  static const Color primaryDark = Color(0xFF060D18);

  /// Secondary brand color (Pure White).
  static const Color secondary = Color(0xFFFFFFFF);

  /// Accent color (Electric Blue).
  static const Color accent = Color(0xFF2196F3);

  // --- Status & Commercial Trucking Colors ---
  /// Green: Allowed routes, vacant parking, operational status.
  static const Color success = Color(0xFF4CAF50);
  static const Color allowed = Color(0xFF4CAF50);

  /// Red: Prohibited weight/height routes, full parking, critical alerts.
  static const Color error = Color(0xFFF44336);
  static const Color prohibited = Color(0xFFF44336);

  /// Orange: Conditional restrictions, hazmat requirements, low clearance warnings.
  static const Color warning = Color(0xFFFF9800);
  static const Color conditional = Color(0xFFFF9800);

  /// Blue: Informational notes, reserved bays, general guidance.
  static const Color info = Color(0xFF2196F3);
  static const Color reserved = Color(0xFF2196F3);

  /// Gray: Unknown or unverified restriction zones, offline services.
  static const Color unknown = Color(0xFF9E9E9E);
  static const Color unverified = Color(0xFF9E9E9E);

  // --- Backgrounds & Surfaces ---
  /// Clean, neutral off-white background.
  static const Color background = Color(0xFFF5F7FA);

  /// Light surface color for cards and modals.
  static const Color surface = Color(0xFFFFFFFF);

  /// Dark background for dark theme.
  static const Color darkBackground = Color(0xFF060D18);

  /// Dark surface for dark theme cards.
  static const Color darkSurface = Color(0xFF111E33);

  /// Card border / subtle divider.
  static const Color border = Color(0xFFE2E8F0);
  static const Color borderDark = Color(0xFF243653);

  // --- Typography Colors ---
  /// Primary high-contrast text color.
  static const Color textPrimary = Color(0xFF0A1628);

  /// Secondary subdued text color.
  static const Color textSecondary = Color(0xFF64748B);

  /// Hint or placeholder text color.
  static const Color textMuted = Color(0xFF94A3B8);

  /// Inverted text for dark navy backgrounds.
  static const Color textLight = Color(0xFFFFFFFF);

  /// Inverted secondary text for dark navy backgrounds.
  static const Color textLightMuted = Color(0xFFCBD5E1);

  // --- Functional Accents ---
  static const Color inputFill = Color(0xFFF8FAFC);
  static const Color inputFillDark = Color(0xFF16253D);
  static const Color divider = Color(0xFFE2E8F0);
  static const Color dividerDark = Color(0xFF1E2F4A);
  static const Color shimmerBase = Color(0xFFE2E8F0);
  static const Color shimmerHighlight = Color(0xFFF8FAFC);
}
