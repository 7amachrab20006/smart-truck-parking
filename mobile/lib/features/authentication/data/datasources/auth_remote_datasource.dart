import '../../../../core/constants/api_endpoints.dart';
import '../../../../core/network/api_client.dart';
import '../models/auth_tokens.dart';
import '../models/user_model.dart';

/// Abstract contract for remote authentication API operations.
abstract class AuthRemoteDataSource {
  Future<({UserModel user, AuthTokens tokens})> login({
    required String email,
    required String password,
  });

  Future<({UserModel user, AuthTokens tokens})> register({
    required String email,
    required String password,
    required String firstName,
    required String lastName,
    String role = 'driver',
  });

  Future<void> logout();

  Future<UserModel> getCurrentUser();
}

/// Implementation of [AuthRemoteDataSource] making network calls through [ApiClient].
class AuthRemoteDataSourceImpl implements AuthRemoteDataSource {
  final ApiClient _apiClient;

  AuthRemoteDataSourceImpl({required ApiClient apiClient})
      : _apiClient = apiClient;

  @override
  Future<({UserModel user, AuthTokens tokens})> login({
    required String email,
    required String password,
  }) async {
    final response = await _apiClient.post(
      ApiEndpoints.login,
      data: {
        'email': email,
        'password': password,
      },
    );

    final data = response.data as Map<String, dynamic>;
    final userData = data['user'] as Map<String, dynamic>? ?? data['data']?['user'] ?? data;
    final tokensData = data['tokens'] as Map<String, dynamic>? ??
        data['data']?['tokens'] ??
        {
          'accessToken': data['accessToken'] ?? data['token'] ?? 'mock_token_${DateTime.now().millisecondsSinceEpoch}',
          'refreshToken': data['refreshToken'] ?? 'mock_refresh_token',
        };

    final user = UserModel.fromJson(userData);
    final tokens = AuthTokens.fromJson(tokensData);

    return (user: user, tokens: tokens);
  }

  @override
  Future<({UserModel user, AuthTokens tokens})> register({
    required String email,
    required String password,
    required String firstName,
    required String lastName,
    String role = 'driver',
  }) async {
    final response = await _apiClient.post(
      ApiEndpoints.register,
      data: {
        'email': email,
        'password': password,
        'firstName': firstName,
        'lastName': lastName,
        'role': role,
      },
    );

    final data = response.data as Map<String, dynamic>;
    final userData = data['user'] as Map<String, dynamic>? ?? data['data']?['user'] ?? data;
    final tokensData = data['tokens'] as Map<String, dynamic>? ??
        data['data']?['tokens'] ??
        {
          'accessToken': data['accessToken'] ?? data['token'] ?? 'mock_token_${DateTime.now().millisecondsSinceEpoch}',
          'refreshToken': data['refreshToken'] ?? 'mock_refresh_token',
        };

    final user = UserModel.fromJson(userData);
    final tokens = AuthTokens.fromJson(tokensData);

    return (user: user, tokens: tokens);
  }

  @override
  Future<void> logout() async {
    try {
      await _apiClient.post(ApiEndpoints.logout);
    } catch (_) {
      // Allow logout to proceed locally even if remote request fails
    }
  }

  @override
  Future<UserModel> getCurrentUser() async {
    final response = await _apiClient.get(ApiEndpoints.me);
    final data = response.data as Map<String, dynamic>;
    final userData = data['user'] as Map<String, dynamic>? ?? data['data'] ?? data;
    return UserModel.fromJson(userData);
  }
}
