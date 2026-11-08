/// Centralized registry of REST API endpoint paths.
class ApiEndpoints {
  ApiEndpoints._();

  // --- Authentication ---
  static const String login = '/auth/login';
  static const String register = '/auth/register';
  static const String logout = '/auth/logout';
  static const String refreshToken = '/auth/refresh';
  static const String me = '/auth/me';

  // --- Vehicles ---
  static const String vehicles = '/vehicles';
  static String vehicleById(String id) => '/vehicles/$id';
  static String setActiveVehicle(String id) => '/vehicles/$id/active';

  // --- Parking ---
  static const String parkingSearch = '/parking/search';
  static const String parkingNearby = '/parking/nearby';
  static String parkingDetails(String id) => '/parking/$id';

  // --- Restrictions & Alerts ---
  static const String restrictions = '/restrictions';
  static const String alerts = '/alerts';
  static const String routeCalculate = '/routes/calculate';

  // --- Regulations & Smart Map ---
  static const String regulationsEvaluate = '/regulations/evaluate';
  static const String mapRegulations = '/map/regulations';
  static const String mapLoadingZones = '/map/loading-zones';
  static const String mapTruckRoutes = '/map/truck-routes';
}
