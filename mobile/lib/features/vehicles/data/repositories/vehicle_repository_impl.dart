import '../../../../core/storage/local_storage_service.dart';
import '../../domain/entities/vehicle.dart';
import '../../domain/repositories/vehicle_repository.dart';
import '../datasources/vehicle_remote_datasource.dart';
import '../models/vehicle_model.dart';

/// Implementation of [VehicleRepository].
class VehicleRepositoryImpl implements VehicleRepository {
  final VehicleRemoteDataSource _remoteDataSource;
  final LocalStorageService _localStorage;

  // Local in-memory cache for fast display and offline fallback
  final List<Vehicle> _cachedVehicles = [];

  VehicleRepositoryImpl({
    required VehicleRemoteDataSource remoteDataSource,
    required LocalStorageService localStorage,
  })  : _remoteDataSource = remoteDataSource,
        _localStorage = localStorage;

  @override
  Future<List<Vehicle>> getVehicles() async {
    try {
      final models = await _remoteDataSource.getVehicles();
      _cachedVehicles.clear();
      final activeId = _localStorage.getActiveVehicleId();

      for (final m in models) {
        final vehicle = m.toEntity();
        _cachedVehicles.add(
          vehicle.copyWith(isActive: vehicle.id == activeId),
        );
      }
      return List.unmodifiable(_cachedVehicles);
    } catch (_) {
      // Return cached list if available, or default sample if empty
      if (_cachedVehicles.isNotEmpty) {
        return List.unmodifiable(_cachedVehicles);
      }

      // Default initial mock vehicle for demo / testing
      final activeId = _localStorage.getActiveVehicleId();
      final sampleVehicle = Vehicle(
        id: 'v-101',
        userId: 'u-1',
        nickname: 'Freightliner Cascadia #1',
        type: VehicleType.semiTruck,
        heightFeet: 13.5,
        widthFeet: 8.5,
        lengthFeet: 53.0,
        weightLbs: 80000.0,
        axleCount: 5,
        hasTrailer: true,
        trailerType: 'Dry Van 53ft',
        isHazmat: false,
        isActive: activeId == null || activeId == 'v-101',
        createdAt: DateTime.now().subtract(const Duration(days: 10)),
      );

      _cachedVehicles.add(sampleVehicle);
      if (activeId == null) {
        await _localStorage.setActiveVehicleId('v-101');
      }
      return List.unmodifiable(_cachedVehicles);
    }
  }

  @override
  Future<Vehicle> getVehicleById(String id) async {
    try {
      final model = await _remoteDataSource.getVehicleById(id);
      final activeId = _localStorage.getActiveVehicleId();
      return model.toEntity().copyWith(isActive: id == activeId);
    } catch (_) {
      final cached = _cachedVehicles.firstWhere(
        (v) => v.id == id,
        orElse: () => throw Exception('Vehicle not found'),
      );
      return cached;
    }
  }

  @override
  Future<Vehicle> createVehicle(Vehicle vehicle) async {
    try {
      final model = VehicleModel.fromEntity(vehicle);
      final created = await _remoteDataSource.createVehicle(model);
      final entity = created.toEntity();
      _cachedVehicles.add(entity);
      return entity;
    } catch (_) {
      // Local fallback creation
      final entity = vehicle.copyWith(
        id: vehicle.id.isNotEmpty ? vehicle.id : 'v-${DateTime.now().millisecondsSinceEpoch}',
        createdAt: DateTime.now(),
      );
      _cachedVehicles.add(entity);
      return entity;
    }
  }

  @override
  Future<Vehicle> updateVehicle(Vehicle vehicle) async {
    try {
      final model = VehicleModel.fromEntity(vehicle);
      final updated = await _remoteDataSource.updateVehicle(model);
      final entity = updated.toEntity();
      final index = _cachedVehicles.indexWhere((v) => v.id == vehicle.id);
      if (index != -1) {
        _cachedVehicles[index] = entity;
      }
      return entity;
    } catch (_) {
      final index = _cachedVehicles.indexWhere((v) => v.id == vehicle.id);
      if (index != -1) {
        _cachedVehicles[index] = vehicle;
      }
      return vehicle;
    }
  }

  @override
  Future<void> deleteVehicle(String id) async {
    try {
      await _remoteDataSource.deleteVehicle(id);
    } catch (_) {
      // Continue locally
    }
    _cachedVehicles.removeWhere((v) => v.id == id);
    if (_localStorage.getActiveVehicleId() == id) {
      final nextActive = _cachedVehicles.isNotEmpty ? _cachedVehicles.first.id : null;
      await _localStorage.setActiveVehicleId(nextActive);
    }
  }

  @override
  Future<void> setActiveVehicle(String id) async {
    await _localStorage.setActiveVehicleId(id);
    try {
      await _remoteDataSource.setActiveVehicle(id);
    } catch (_) {
      // Network failure ignored for local active vehicle switch
    }

    for (int i = 0; i < _cachedVehicles.length; i++) {
      final v = _cachedVehicles[i];
      _cachedVehicles[i] = v.copyWith(isActive: v.id == id);
    }
  }

  @override
  Future<Vehicle?> getActiveVehicle() async {
    final list = await getVehicles();
    final activeId = _localStorage.getActiveVehicleId();
    if (activeId != null) {
      return list.firstWhere(
        (v) => v.id == activeId,
        orElse: () => list.isNotEmpty ? list.first : throw Exception(),
      );
    }
    return list.isNotEmpty ? list.first : null;
  }
}
