import 'app_config.dart';

/// Available application runtime environments.
enum AppEnvironment {
  /// Development environment for local and staging tests.
  dev,

  /// Staging environment for pre-production verification.
  staging,

  /// Production environment for live drivers and fleets.
  prod,
}

/// Dynamic environment configuration manager.
class EnvConfig {
  EnvConfig._();

  static AppEnvironment _environment = AppEnvironment.dev;
  static String _baseUrl = AppConfig.defaultBaseUrl;

  /// Current active runtime environment.
  static AppEnvironment get environment => _environment;

  /// Current active base URL for API communication.
  static String get apiBaseUrl => _baseUrl;

  /// Whether current environment is development.
  static bool get isDev => _environment == AppEnvironment.dev;

  /// Whether current environment is staging.
  static bool get isStaging => _environment == AppEnvironment.staging;

  /// Whether current environment is production.
  static bool get isProd => _environment == AppEnvironment.prod;

  /// Initialize environment configuration before app startup.
  static void initialize({
    AppEnvironment environment = AppEnvironment.dev,
    String? baseUrl,
  }) {
    _environment = environment;
    if (baseUrl != null && baseUrl.isNotEmpty) {
      _baseUrl = baseUrl;
    } else {
      switch (environment) {
        case AppEnvironment.dev:
          _baseUrl = 'https://dev-api.smarttruckparking.com/api/v1';
          break;
        case AppEnvironment.staging:
          _baseUrl = 'https://staging-api.smarttruckparking.com/api/v1';
          break;
        case AppEnvironment.prod:
          _baseUrl = 'https://api.smarttruckparking.com/api/v1';
          break;
      }
    }
  }
}
