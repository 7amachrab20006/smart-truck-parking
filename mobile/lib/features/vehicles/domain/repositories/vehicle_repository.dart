import '../entities/vehicle.dart';

/// Abstract contract for managing commercial vehicle profiles.
abstract class VehicleRepository {
  /// Fetches all vehicles registered for current driver.
  Future<List<Vehicle>> getVehicles();

  /// Fetches a single vehicle profile by [id].
  Future<Vehicle> getVehicleById(String id);

  /// Registers a new vehicle profile.
  Future<Vehicle> createVehicle(Vehicle vehicle);

  /// Updates an existing vehicle profile.
  Future<Vehicle> updateVehicle(Vehicle vehicle);

  /// Deletes a vehicle profile.
  Future<void> deleteVehicle(String id);

  /// Designates a vehicle as the currently active profile for navigation.
  Future<void> setActiveVehicle(String id);

  /// Retrieves the currently active vehicle profile.
  Future<Vehicle?> getActiveVehicle();
}
