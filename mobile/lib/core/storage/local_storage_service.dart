import 'package:shared_preferences/shared_preferences.dart';
import '../config/app_config.dart';

/// Local key-value storage backed by [SharedPreferences] for non-sensitive preferences.
class LocalStorageService {
  final SharedPreferences _prefs;

  LocalStorageService(this._prefs);

  /// Saves a boolean flag.
  Future<bool> setBool(String key, bool value) async {
    return await _prefs.setBool(key, value);
  }

  /// Retrieves a boolean flag.
  bool? getBool(String key) {
    return _prefs.getBool(key);
  }

  /// Saves a string value.
  Future<bool> setString(String key, String value) async {
    return await _prefs.setString(key, value);
  }

  /// Retrieves a string value.
  String? getString(String key) {
    return _prefs.getString(key);
  }

  /// Removes an entry by [key].
  Future<bool> remove(String key) async {
    return await _prefs.remove(key);
  }

  /// Marks onboarding walkthrough as completed.
  Future<bool> setOnboardingCompleted({bool completed = true}) async {
    return await _prefs.setBool(AppConfig.onboardingCompletedKey, completed);
  }

  /// Checks if the driver has completed onboarding walkthrough.
  bool isOnboardingCompleted() {
    return _prefs.getBool(AppConfig.onboardingCompletedKey) ?? false;
  }

  /// Stores active commercial vehicle ID.
  Future<bool> setActiveVehicleId(String? vehicleId) async {
    if (vehicleId == null) {
      return await _prefs.remove(AppConfig.activeVehicleIdKey);
    }
    return await _prefs.setString(AppConfig.activeVehicleIdKey, vehicleId);
  }

  /// Retrieves the active vehicle ID.
  String? getActiveVehicleId() {
    return _prefs.getString(AppConfig.activeVehicleIdKey);
  }

  /// Clears all preferences.
  Future<bool> clear() async {
    return await _prefs.clear();
  }
}
