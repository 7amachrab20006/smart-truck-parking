/// Generic wrapper for API responses across all endpoints.
class ApiResponse<T> {
  final bool success;
  final String? message;
  final T? data;
  final int? statusCode;
  final dynamic error;

  const ApiResponse({
    required this.success,
    this.message,
    this.data,
    this.statusCode,
    this.error,
  });

  /// Factory constructor for successful operations.
  factory ApiResponse.success({
    T? data,
    String? message,
    int statusCode = 200,
  }) {
    return ApiResponse<T>(
      success: true,
      data: data,
      message: message,
      statusCode: statusCode,
    );
  }

  /// Factory constructor for failed operations.
  factory ApiResponse.error({
    required String message,
    int? statusCode,
    dynamic error,
  }) {
    return ApiResponse<T>(
      success: false,
      message: message,
      statusCode: statusCode,
      error: error,
    );
  }

  /// Helper getter to check status.
  bool get isSuccess => success;

  /// Helper getter to check failure.
  bool get isFailure => !success;

  @override
  String toString() =>
      'ApiResponse(success: $success, statusCode: $statusCode, message: $message, data: $data)';
}
