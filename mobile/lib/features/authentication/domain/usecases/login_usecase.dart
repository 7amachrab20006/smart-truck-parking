import '../entities/user.dart';
import '../repositories/auth_repository.dart';

/// Use case to authenticate a commercial driver.
class LoginUseCase {
  final AuthRepository _repository;

  LoginUseCase(this._repository);

  Future<User> execute({
    required String email,
    required String password,
  }) {
    return _repository.login(
      email: email.trim(),
      password: password,
    );
  }
}
