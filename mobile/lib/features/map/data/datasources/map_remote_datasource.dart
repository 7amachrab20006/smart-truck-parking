import '../../../../core/constants/api_endpoints.dart';
import '../../../../core/network/api_client.dart';
import '../../../regulations/domain/entities/regulation_item.dart';

abstract class MapRemoteDataSource {
  Future<List<RegulationItem>> getMapRegulations({
    required double latitude,
    required double longitude,
    double radiusMeters = 1000.0,
  });
}

class MapRemoteDataSourceImpl implements MapRemoteDataSource {
  final ApiClient apiClient;

  MapRemoteDataSourceImpl({required this.apiClient});

  @override
  Future<List<RegulationItem>> getMapRegulations({
    required double latitude,
    required double longitude,
    double radiusMeters = 1000.0,
  }) async {
    final response = await apiClient.get<Map<String, dynamic>>(
      ApiEndpoints.mapRegulations,
      queryParameters: {
        'latitude': latitude,
        'longitude': longitude,
        'radius_meters': radiusMeters,
      },
    );

    final dataList = response.data?['data'] as List<dynamic>? ?? [];
    return dataList
        .map((item) => RegulationItem.fromJson(item as Map<String, dynamic>))
        .toList();
  }
}
