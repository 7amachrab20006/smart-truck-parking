import 'package:equatable/equatable.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:smart_truck_parking/features/authentication/presentation/providers/auth_provider.dart';
import '../../data/datasources/vehicle_remote_datasource.dart';
import '../../data/repositories/vehicle_repository_impl.dart';
import '../../domain/entities/vehicle.dart';
import '../../domain/repositories/vehicle_repository.dart';

/// State representation for commercial vehicles.
class VehicleState extends Equatable {
  final List<Vehicle> vehicles;
  final Vehicle? activeVehicle;
  final bool isLoading;
  final String? errorMessage;

  const VehicleState({
    this.vehicles = const [],
    this.activeVehicle,
    this.isLoading = false,
    this.errorMessage,
  });

  VehicleState copyWith({
    List<Vehicle>? vehicles,
    Vehicle? activeVehicle,
    bool? isLoading,
    String? errorMessage,
  }) {
    return VehicleState(
      vehicles: vehicles ?? this.vehicles,
      activeVehicle: activeVehicle ?? this.activeVehicle,
      isLoading: isLoading ?? this.isLoading,
      errorMessage: errorMessage,
    );
  }

  @override
  List<Object?> get props => [vehicles, activeVehicle, isLoading, errorMessage];
}

// --- Providers ---

final vehicleRemoteDataSourceProvider = Provider<VehicleRemoteDataSource>((ref) {
  final apiClient = ref.watch(apiClientProvider);
  return VehicleRemoteDataSourceImpl(apiClient: apiClient);
});

final vehicleRepositoryProvider = Provider<VehicleRepository>((ref) {
  final remote = ref.watch(vehicleRemoteDataSourceProvider);
  final local = ref.watch(localStorageProvider);
  return VehicleRepositoryImpl(
    remoteDataSource: remote,
    localStorage: local,
  );
});

/// Vehicle management StateNotifier.
class VehicleNotifier extends StateNotifier<VehicleState> {
  final VehicleRepository _repository;

  VehicleNotifier(this._repository) : super(const VehicleState()) {
    loadVehicles();
  }

  /// Fetches registered fleet vehicles for the driver.
  Future<void> loadVehicles() async {
    state = state.copyWith(isLoading: true, errorMessage: null);
    try {
      final list = await _repository.getVehicles();
      final active = await _repository.getActiveVehicle();
      state = state.copyWith(
        vehicles: list,
        activeVehicle: active,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'Unable to load vehicles: ${e.toString()}',
      );
    }
  }

  /// Sets a specific vehicle as the active navigation profile.
  Future<void> setActiveVehicle(String id) async {
    state = state.copyWith(isLoading: true);
    try {
      await _repository.setActiveVehicle(id);
      final updatedList = await _repository.getVehicles();
      final active = updatedList.firstWhere((v) => v.id == id);
      state = state.copyWith(
        vehicles: updatedList,
        activeVehicle: active,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'Failed to switch active vehicle',
      );
    }
  }

  /// Saves a new or edited vehicle.
  Future<bool> saveVehicle(Vehicle vehicle) async {
    state = state.copyWith(isLoading: true, errorMessage: null);
    try {
      if (vehicle.id.isEmpty) {
        await _repository.createVehicle(vehicle);
      } else {
        await _repository.updateVehicle(vehicle);
      }
      await loadVehicles();
      return true;
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'Failed to save vehicle: ${e.toString()}',
      );
      return false;
    }
  }

  /// Removes a vehicle profile.
  Future<bool> deleteVehicle(String id) async {
    state = state.copyWith(isLoading: true, errorMessage: null);
    try {
      await _repository.deleteVehicle(id);
      await loadVehicles();
      return true;
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'Failed to delete vehicle',
      );
      return false;
    }
  }
}

final vehicleNotifierProvider =
    StateNotifierProvider<VehicleNotifier, VehicleState>((ref) {
  return VehicleNotifier(ref.watch(vehicleRepositoryProvider));
});

final activeVehicleProvider = Provider<Vehicle?>((ref) {
  return ref.watch(vehicleNotifierProvider).activeVehicle;
});
