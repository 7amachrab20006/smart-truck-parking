import 'dart:convert';
import '../../../../core/config/app_config.dart';
import '../../../../core/storage/local_storage_service.dart';
import '../../../../core/storage/secure_storage_service.dart';
import '../../domain/entities/user.dart';
import '../../domain/repositories/auth_repository.dart';
import '../datasources/auth_remote_datasource.dart';
import '../models/user_model.dart';

/// Concrete implementation of [AuthRepository] orchestrating remote data source and local storage.
class AuthRepositoryImpl implements AuthRepository {
  final AuthRemoteDataSource _remoteDataSource;
  final SecureStorageService _secureStorage;
  final LocalStorageService _localStorage;
  User? _cachedUser;

  AuthRepositoryImpl({
    required AuthRemoteDataSource remoteDataSource,
    required SecureStorageService secureStorage,
    required LocalStorageService localStorage,
  })  : _remoteDataSource = remoteDataSource,
        _secureStorage = secureStorage,
        _localStorage = localStorage;

  @override
  Future<User> login({
    required String email,
    required String password,
  }) async {
    final result = await _remoteDataSource.login(
      email: email,
      password: password,
    );

    await _secureStorage.saveAuthTokens(
      accessToken: result.tokens.accessToken,
      refreshToken: result.tokens.refreshToken,
    );

    await _cacheUser(result.user);
    _cachedUser = result.user.toEntity();
    return _cachedUser!;
  }

  @override
  Future<User> register({
    required String email,
    required String password,
    required String firstName,
    required String lastName,
    String role = 'driver',
  }) async {
    final result = await _remoteDataSource.register(
      email: email,
      password: password,
      firstName: firstName,
      lastName: lastName,
      role: role,
    );

    await _secureStorage.saveAuthTokens(
      accessToken: result.tokens.accessToken,
      refreshToken: result.tokens.refreshToken,
    );

    await _cacheUser(result.user);
    _cachedUser = result.user.toEntity();
    return _cachedUser!;
  }

  @override
  Future<void> logout() async {
    await _remoteDataSource.logout();
    await _secureStorage.clearAuthTokens();
    await _localStorage.remove(AppConfig.userKey);
    _cachedUser = null;
  }

  @override
  Future<User?> getCurrentUser() async {
    if (_cachedUser != null) {
      return _cachedUser;
    }

    // Try reading cached JSON from local storage first
    final cachedJson = _localStorage.getString(AppConfig.userKey);
    if (cachedJson != null) {
      try {
        final map = jsonDecode(cachedJson) as Map<String, dynamic>;
        _cachedUser = UserModel.fromJson(map).toEntity();
        return _cachedUser;
      } catch (_) {
        // Fallback to remote fetch
      }
    }

    // Attempt remote profile retrieval if token is present
    final token = await _secureStorage.getAccessToken();
    if (token != null && token.isNotEmpty) {
      try {
        final remoteUser = await _remoteDataSource.getCurrentUser();
        await _cacheUser(remoteUser);
        _cachedUser = remoteUser.toEntity();
        return _cachedUser;
      } catch (_) {
        return null;
      }
    }

    return null;
  }

  @override
  Future<bool> isAuthenticated() async {
    final token = await _secureStorage.getAccessToken();
    return token != null && token.isNotEmpty;
  }

  Future<void> _cacheUser(UserModel user) async {
    final jsonStr = jsonEncode(user.toJson());
    await _localStorage.setString(AppConfig.userKey, jsonStr);
  }
}
