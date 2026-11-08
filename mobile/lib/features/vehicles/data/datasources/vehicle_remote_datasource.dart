import '../../../../core/constants/api_endpoints.dart';
import '../../../../core/network/api_client.dart';
import '../models/vehicle_model.dart';

/// Contract for vehicle remote HTTP operations.
abstract class VehicleRemoteDataSource {
  Future<List<VehicleModel>> getVehicles();
  Future<VehicleModel> getVehicleById(String id);
  Future<VehicleModel> createVehicle(VehicleModel vehicle);
  Future<VehicleModel> updateVehicle(VehicleModel vehicle);
  Future<void> deleteVehicle(String id);
  Future<void> setActiveVehicle(String id);
}

/// Implementation using [ApiClient].
class VehicleRemoteDataSourceImpl implements VehicleRemoteDataSource {
  final ApiClient _apiClient;

  VehicleRemoteDataSourceImpl({required ApiClient apiClient})
      : _apiClient = apiClient;

  @override
  Future<List<VehicleModel>> getVehicles() async {
    final response = await _apiClient.get(ApiEndpoints.vehicles);
    final dynamic data = response.data;

    List list = [];
    if (data is List) {
      list = data;
    } else if (data is Map<String, dynamic>) {
      list = data['vehicles'] as List? ?? data['data'] as List? ?? [];
    }

    return list
        .map((item) => VehicleModel.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  @override
  Future<VehicleModel> getVehicleById(String id) async {
    final response = await _apiClient.get(ApiEndpoints.vehicleById(id));
    final data = response.data as Map<String, dynamic>;
    final vehicleData = data['vehicle'] as Map<String, dynamic>? ?? data['data'] ?? data;
    return VehicleModel.fromJson(vehicleData);
  }

  @override
  Future<VehicleModel> createVehicle(VehicleModel vehicle) async {
    final response = await _apiClient.post(
      ApiEndpoints.vehicles,
      data: vehicle.toJson(),
    );
    final data = response.data as Map<String, dynamic>;
    final vehicleData = data['vehicle'] as Map<String, dynamic>? ?? data['data'] ?? data;
    return VehicleModel.fromJson(vehicleData);
  }

  @override
  Future<VehicleModel> updateVehicle(VehicleModel vehicle) async {
    final response = await _apiClient.put(
      ApiEndpoints.vehicleById(vehicle.id),
      data: vehicle.toJson(),
    );
    final data = response.data as Map<String, dynamic>;
    final vehicleData = data['vehicle'] as Map<String, dynamic>? ?? data['data'] ?? data;
    return VehicleModel.fromJson(vehicleData);
  }

  @override
  Future<void> deleteVehicle(String id) async {
    await _apiClient.delete(ApiEndpoints.vehicleById(id));
  }

  @override
  Future<void> setActiveVehicle(String id) async {
    await _apiClient.post(ApiEndpoints.setActiveVehicle(id));
  }
}
