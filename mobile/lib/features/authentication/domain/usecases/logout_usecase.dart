import '../repositories/auth_repository.dart';

/// Use case to sign out the active driver and terminate the session.
class LogoutUseCase {
  final AuthRepository _repository;

  LogoutUseCase(this._repository);

  Future<void> execute() {
    return _repository.logout();
  }
}
