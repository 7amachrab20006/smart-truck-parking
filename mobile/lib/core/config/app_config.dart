/// Application-wide configuration parameters and constants.
class AppConfig {
  AppConfig._();

  /// Name of the application displayed across user interfaces.
  static const String appName = 'Smart Truck & Parking Assistant';

  /// Semantic version string.
  static const String appVersion = '1.0.0';

  /// Internal build number.
  static const String buildNumber = '1';

  /// Default API base URL for network communication.
  static const String defaultBaseUrl = 'https://api.smarttruckparking.com/api/v1';

  /// Timeout duration when establishing network connections.
  static const Duration connectTimeout = Duration(seconds: 15);

  /// Timeout duration when receiving responses over network.
  static const Duration receiveTimeout = Duration(seconds: 15);

  /// Timeout duration when sending request payloads.
  static const Duration sendTimeout = Duration(seconds: 15);

  /// Maximum retry count for idempotent failed requests.
  static const int maxRetries = 3;

  /// Storage keys
  static const String tokenKey = 'auth_token';
  static const String refreshTokenKey = 'refresh_token';
  static const String userKey = 'auth_user';
  static const String onboardingCompletedKey = 'onboarding_completed';
  static const String activeVehicleIdKey = 'active_vehicle_id';
}
