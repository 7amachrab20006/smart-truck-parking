import '../entities/user.dart';

/// Abstract contract for authentication data operations.
abstract class AuthRepository {
  /// Authenticates a driver with email and password credentials.
  Future<User> login({
    required String email,
    required String password,
  });

  /// Registers a new commercial driver profile.
  Future<User> register({
    required String email,
    required String password,
    required String firstName,
    required String lastName,
    String role = 'driver',
  });

  /// Terminates the current session and purges credentials.
  Future<void> logout();

  /// Retrieves the currently cached or fetched driver profile.
  Future<User?> getCurrentUser();

  /// Checks whether a valid session token currently exists.
  Future<bool> isAuthenticated();
}
