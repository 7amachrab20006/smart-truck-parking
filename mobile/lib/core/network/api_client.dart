import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../config/app_config.dart';
import '../config/env_config.dart';
import '../constants/api_endpoints.dart';
import '../storage/secure_storage_service.dart';
import 'api_exceptions.dart';

/// Configured [Dio] client providing authentication interceptors, token refresh,
/// structured error handling, and timeout policies.
class ApiClient {
  late final Dio dio;
  final SecureStorageService _secureStorage;

  ApiClient({
    Dio? customDio,
    SecureStorageService? secureStorage,
  }) : _secureStorage = secureStorage ?? SecureStorageService() {
    dio = customDio ??
        Dio(
          BaseOptions(
            baseUrl: EnvConfig.apiBaseUrl,
            connectTimeout: AppConfig.connectTimeout,
            receiveTimeout: AppConfig.receiveTimeout,
            sendTimeout: AppConfig.sendTimeout,
            headers: {
              'Content-Type': 'application/json',
              'Accept': 'application/json',
            },
          ),
        );

    _setupInterceptors();
  }

  void _setupInterceptors() {
    dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          final token = await _secureStorage.getAccessToken();
          if (token != null && token.isNotEmpty) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          return handler.next(options);
        },
        onError: (DioException error, handler) async {
          // Token refresh on 401 Unauthorized
          if (error.response?.statusCode == 401 &&
              error.requestOptions.extra['retry_count'] == null) {
            final refreshed = await _refreshToken();
            if (refreshed) {
              final newOptions = error.requestOptions;
              newOptions.extra['retry_count'] = 1;
              final newToken = await _secureStorage.getAccessToken();
              newOptions.headers['Authorization'] = 'Bearer $newToken';

              try {
                final response = await dio.fetch(newOptions);
                return handler.resolve(response);
              } catch (e) {
                // If retry also fails, continue to error mapping
              }
            } else {
              await _secureStorage.clearAuthTokens();
            }
          }

          final mappedException = _mapDioErrorToApiException(error);
          return handler.reject(
            DioException(
              requestOptions: error.requestOptions,
              response: error.response,
              type: error.type,
              error: mappedException,
              message: mappedException.message,
            ),
          );
        },
      ),
    );

    // Logging in debug mode
    if (kDebugMode) {
      dio.interceptors.add(
        LogInterceptor(
          request: true,
          requestHeader: false,
          requestBody: true,
          responseHeader: false,
          responseBody: true,
          error: true,
        ),
      );
    }
  }

  /// Attempts to exchange the stored refresh token for a new access token.
  Future<bool> _refreshToken() async {
    try {
      final refreshToken = await _secureStorage.getRefreshToken();
      if (refreshToken == null || refreshToken.isEmpty) {
        return false;
      }

      // Create isolated Dio instance to avoid interceptor recursion
      final refreshDio = Dio(
        BaseOptions(
          baseUrl: EnvConfig.apiBaseUrl,
          connectTimeout: AppConfig.connectTimeout,
          receiveTimeout: AppConfig.receiveTimeout,
        ),
      );

      final response = await refreshDio.post(
        ApiEndpoints.refreshToken,
        data: {'refreshToken': refreshToken},
      );

      if (response.statusCode == 200 && response.data != null) {
        final data = response.data as Map<String, dynamic>;
        final newAccessToken = data['accessToken'] as String?;
        final newRefreshToken = (data['refreshToken'] as String?) ?? refreshToken;

        if (newAccessToken != null) {
          await _secureStorage.saveAuthTokens(
            accessToken: newAccessToken,
            refreshToken: newRefreshToken,
          );
          return true;
        }
      }
      return false;
    } catch (_) {
      return false;
    }
  }

  /// Converts low-level [DioException] into structured [ApiException].
  ApiException _mapDioErrorToApiException(DioException error) {
    switch (error.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        return const TimeoutException();

      case DioExceptionType.connectionError:
        return const NetworkException();

      case DioExceptionType.badResponse:
        final statusCode = error.response?.statusCode;
        final data = error.response?.data;
        String message = 'An unexpected server error occurred.';

        if (data is Map<String, dynamic> && data.containsKey('message')) {
          message = data['message'].toString();
        }

        switch (statusCode) {
          case 400:
          case 422:
            return ValidationException(
              message: message,
              statusCode: statusCode,
              details: data,
            );
          case 401:
            return UnauthorizedException(
              message: message,
              statusCode: statusCode,
              details: data,
            );
          case 404:
            return NotFoundException(
              message: message,
              statusCode: statusCode,
              details: data,
            );
          case 500:
          case 502:
          case 503:
          case 504:
            return ServerException(
              message: message,
              statusCode: statusCode,
              details: data,
            );
          default:
            return ApiException(
              message: message,
              statusCode: statusCode,
              details: data,
            );
        }

      case DioExceptionType.cancel:
        return const ApiException(message: 'Request was cancelled.');

      case DioExceptionType.badCertificate:
        return const ApiException(message: 'SSL Certificate validation failed.');

      case DioExceptionType.unknown:
      default:
        return ApiException(
          message: error.message ?? 'Unknown network failure occurred.',
        );
    }
  }

  /// Convenience GET request.
  Future<Response<T>> get<T>(
    String path, {
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    return await dio.get<T>(
      path,
      queryParameters: queryParameters,
      options: options,
    );
  }

  /// Convenience POST request.
  Future<Response<T>> post<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    return await dio.post<T>(
      path,
      data: data,
      queryParameters: queryParameters,
      options: options,
    );
  }

  /// Convenience PUT request.
  Future<Response<T>> put<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    return await dio.put<T>(
      path,
      data: data,
      queryParameters: queryParameters,
      options: options,
    );
  }

  /// Convenience DELETE request.
  Future<Response<T>> delete<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    return await dio.delete<T>(
      path,
      data: data,
      queryParameters: queryParameters,
      options: options,
    );
  }
}
