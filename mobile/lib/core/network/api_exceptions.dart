/// Base class for all application API exceptions.
class ApiException implements Exception {
  final String message;
  final int? statusCode;
  final dynamic details;

  const ApiException({
    required this.message,
    this.statusCode,
    this.details,
  });

  @override
  String toString() => 'ApiException: [$statusCode] $message';
}

/// Thrown when user credentials or token are invalid or expired (HTTP 401).
class UnauthorizedException extends ApiException {
  const UnauthorizedException({
    super.message = 'Authentication required or session expired.',
    super.statusCode = 401,
    super.details,
  });
}

/// Thrown when requested resource does not exist (HTTP 404).
class NotFoundException extends ApiException {
  const NotFoundException({
    super.message = 'The requested resource was not found.',
    super.statusCode = 404,
    super.details,
  });
}

/// Thrown on server-side internal errors (HTTP 500+).
class ServerException extends ApiException {
  const ServerException({
    super.message = 'An internal server error occurred. Please try again later.',
    super.statusCode = 500,
    super.details,
  });
}

/// Thrown when network connection is absent or disrupted.
class NetworkException extends ApiException {
  const NetworkException({
    super.message = 'Unable to connect to the server. Please check your internet connection.',
    super.statusCode,
    super.details,
  });
}

/// Thrown when an HTTP request exceeds configured time limits.
class TimeoutException extends ApiException {
  const TimeoutException({
    super.message = 'The connection timed out. Please try again.',
    super.statusCode = 408,
    super.details,
  });
}

/// Thrown when input payload fails validation (HTTP 400 or 422).
class ValidationException extends ApiException {
  const ValidationException({
    super.message = 'Invalid data provided.',
    super.statusCode = 422,
    super.details,
  });
}
