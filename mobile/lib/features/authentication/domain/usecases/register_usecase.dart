import '../entities/user.dart';
import '../repositories/auth_repository.dart';

/// Use case to register a new commercial driver profile.
class RegisterUseCase {
  final AuthRepository _repository;

  RegisterUseCase(this._repository);

  Future<User> execute({
    required String email,
    required String password,
    required String firstName,
    required String lastName,
    String role = 'driver',
  }) {
    return _repository.register(
      email: email.trim(),
      password: password,
      firstName: firstName.trim(),
      lastName: lastName.trim(),
      role: role,
    );
  }
}
