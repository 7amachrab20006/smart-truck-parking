import '../constants/app_strings.dart';

/// Form validation utility helpers.
class Validators {
  Validators._();

  static final RegExp _emailRegex = RegExp(
    r'^[a-zA-Z0-9.!#$%&’*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$',
  );

  static final RegExp _phoneRegex = RegExp(
    r'^\+?[0-9]{7,15}$',
  );

  /// Validates standard user email addresses.
  static String? validateEmail(String? value) {
    if (value == null || value.trim().isEmpty) {
      return AppStrings.emailRequired;
    }
    if (!_emailRegex.hasMatch(value.trim())) {
      return AppStrings.emailInvalid;
    }
    return null;
  }

  /// Validates password security (minimum 8 characters).
  static String? validatePassword(String? value) {
    if (value == null || value.isEmpty) {
      return AppStrings.passwordRequired;
    }
    if (value.length < 8) {
      return AppStrings.passwordTooShort;
    }
    return null;
  }

  /// Validates confirmation password against origin password.
  static String? validateConfirmPassword(String? value, String? originalPassword) {
    if (value == null || value.isEmpty) {
      return AppStrings.fieldRequired;
    }
    if (value != originalPassword) {
      return AppStrings.passwordsDoNotMatch;
    }
    return null;
  }

  /// Validates that a required text field is not empty.
  static String? validateRequired(String? value, [String? fieldName]) {
    if (value == null || value.trim().isEmpty) {
      return fieldName != null ? '$fieldName is required' : AppStrings.fieldRequired;
    }
    return null;
  }

  /// Validates phone number format.
  static String? validatePhone(String? value) {
    if (value == null || value.trim().isEmpty) {
      return null; // Phone is optional in some contexts
    }
    final sanitized = value.replaceAll(RegExp(r'[\s()-]'), '');
    if (!_phoneRegex.hasMatch(sanitized)) {
      return 'Please enter a valid phone number';
    }
    return null;
  }

  /// Validates commercial vehicle dimensions (positive decimal number).
  static String? validateDimension(String? value, [String? dimensionName]) {
    final name = dimensionName ?? 'Dimension';
    if (value == null || value.trim().isEmpty) {
      return '$name is required';
    }
    final parsed = double.tryParse(value.trim());
    if (parsed == null || parsed <= 0) {
      return 'Enter a valid positive number for $name';
    }
    return null;
  }

  /// Validates axle count (positive integer, typical range 2 to 10).
  static String? validateAxleCount(String? value) {
    if (value == null || value.trim().isEmpty) {
      return 'Axle count is required';
    }
    final parsed = int.tryParse(value.trim());
    if (parsed == null || parsed < 2 || parsed > 15) {
      return 'Enter a realistic axle count (2 to 15)';
    }
    return null;
  }

  /// Validates gross vehicle weight rating in pounds.
  static String? validateWeight(String? value) {
    if (value == null || value.trim().isEmpty) {
      return 'Weight is required';
    }
    final parsed = double.tryParse(value.trim());
    if (parsed == null || parsed <= 0) {
      return 'Enter a valid gross vehicle weight';
    }
    if (parsed > 160000) {
      return 'Weight exceeds max commercial rating (160,000 lbs)';
    }
    return null;
  }
}
