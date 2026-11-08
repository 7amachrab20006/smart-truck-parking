/// Commercial fleet unit conversion helpers.
class UnitConverter {
  UnitConverter._();

  static const double metersPerFoot = 0.3048;
  static const double feetPerMeter = 3.28084;

  static const double centimetersPerInch = 2.54;
  static const double inchesPerCentimeter = 0.393701;

  static const double kgPerPound = 0.45359237;
  static const double poundsPerKg = 2.20462;

  /// Converts feet to meters.
  static double feetToMeters(double feet) => feet * metersPerFoot;

  /// Converts meters to feet.
  static double metersToFeet(double meters) => meters * feetPerMeter;

  /// Converts inches to centimeters.
  static double inchesToCm(double inches) => inches * centimetersPerInch;

  /// Converts centimeters to inches.
  static double cmToInches(double cm) => cm * inchesPerCentimeter;

  /// Converts pounds (lbs) to kilograms (kg).
  static double poundsToKg(double lbs) => lbs * kgPerPound;

  /// Converts kilograms (kg) to pounds (lbs).
  static double kgToPounds(double kg) => kg * poundsPerKg;

  /// Formats feet and inches into a readable string (e.g. 13' 6").
  static String formatFeetAndInches(double totalFeet) {
    final feet = totalFeet.floor();
    final inches = ((totalFeet - feet) * 12).round();
    return '$feet\' $inches"';
  }

  /// Parses feet and inches inputs into total decimal feet.
  static double toDecimalFeet(int feet, int inches) {
    return feet + (inches / 12.0);
  }

  /// Formats weight with comma separators and unit (e.g. 80,000 lbs).
  static String formatWeightLbs(double pounds) {
    final intWeight = pounds.round();
    final buffer = StringBuffer();
    final digits = intWeight.toString();
    int count = 0;
    for (int i = digits.length - 1; i >= 0; i--) {
      buffer.write(digits[i]);
      count++;
      if (count % 3 == 0 && i != 0) {
        buffer.write(',');
      }
    }
    return '${buffer.toString().split('').reversed.join()} lbs';
  }
}
