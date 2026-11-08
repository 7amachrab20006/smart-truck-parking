import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../config/app_config.dart';

/// Secure key-value storage service backed by [FlutterSecureStorage].
/// Used exclusively for confidential data such as JWT tokens and driver credentials.
class SecureStorageService {
  final FlutterSecureStorage _storage;

  SecureStorageService({FlutterSecureStorage? storage})
      : _storage = storage ??
            const FlutterSecureStorage(
              aOptions: AndroidOptions(encryptedSharedPreferences: true),
              iOptions: IOSOptions(accessibility: KeychainAccessibility.first_unlock),
            );

  /// Persists a string [value] for [key].
  Future<void> write(String key, String value) async {
    await _storage.write(key: key, value: value);
  }

  /// Reads string value associated with [key].
  Future<String?> read(String key) async {
    return await _storage.read(key: key);
  }

  /// Deletes key-value pair for [key].
  Future<void> delete(String key) async {
    await _storage.delete(key: key);
  }

  /// Clears all stored key-value pairs.
  Future<void> deleteAll() async {
    await _storage.deleteAll();
  }

  /// Persist authentication access and refresh tokens.
  Future<void> saveAuthTokens({
    required String accessToken,
    required String refreshToken,
  }) async {
    await _storage.write(key: AppConfig.tokenKey, value: accessToken);
    await _storage.write(key: AppConfig.refreshTokenKey, value: refreshToken);
  }

  /// Retrieve the current access token.
  Future<String?> getAccessToken() async {
    return await _storage.read(key: AppConfig.tokenKey);
  }

  /// Retrieve the current refresh token.
  Future<String?> getRefreshToken() async {
    return await _storage.read(key: AppConfig.refreshTokenKey);
  }

  /// Erase all stored authentication tokens upon logout or session expiry.
  Future<void> clearAuthTokens() async {
    await _storage.delete(key: AppConfig.tokenKey);
    await _storage.delete(key: AppConfig.refreshTokenKey);
  }
}
