import 'package:equatable/equatable.dart';
import '../../../../core/utils/unit_converter.dart';

/// Commercial vehicle types.
enum VehicleType {
  semiTruck('semi_truck', 'Semi Truck / Tractor', 'Semi-trailer combination'),
  boxTruck('box_truck', 'Box Truck', 'Straight truck / Cube van'),
  flatbed('flatbed', 'Flatbed Truck', 'Open deck commercial freight'),
  tanker('tanker', 'Tanker', 'Liquid or gas transport'),
  dumpTruck('dump_truck', 'Dump Truck', 'Heavy aggregate transport');

  final String key;
  final String label;
  final String description;

  const VehicleType(this.key, this.label, this.description);

  static VehicleType fromKey(String key) {
    return VehicleType.values.firstWhere(
      (e) => e.key == key,
      orElse: () => VehicleType.semiTruck,
    );
  }
}

/// Pure domain entity representing a commercial motor vehicle.
class Vehicle extends Equatable {
  final String id;
  final String userId;
  final String nickname;
  final VehicleType type;
  final double heightFeet;
  final double widthFeet;
  final double lengthFeet;
  final double weightLbs;
  final int axleCount;
  final bool hasTrailer;
  final String? trailerType;
  final bool isHazmat;
  final bool isActive;
  final DateTime? createdAt;

  const Vehicle({
    required this.id,
    required this.userId,
    required this.nickname,
    required this.type,
    required this.heightFeet,
    required this.widthFeet,
    required this.lengthFeet,
    required this.weightLbs,
    required this.axleCount,
    this.hasTrailer = false,
    this.trailerType,
    this.isHazmat = false,
    this.isActive = false,
    this.createdAt,
  });

  /// Readable formatted height string (e.g., 13' 6").
  String get formattedHeight => UnitConverter.formatFeetAndInches(heightFeet);

  /// Readable formatted weight string (e.g., 80,000 lbs).
  String get formattedWeight => UnitConverter.formatWeightLbs(weightLbs);

  /// Compact summary of physical profile.
  String get dimensionsSummary =>
      '$formattedHeight H • ${lengthFeet.toStringAsFixed(0)}\' L • $formattedWeight • $axleCount Axles';

  Vehicle copyWith({
    String? id,
    String? userId,
    String? nickname,
    VehicleType? type,
    double? heightFeet,
    double? widthFeet,
    double? lengthFeet,
    double? weightLbs,
    int? axleCount,
    bool? hasTrailer,
    String? trailerType,
    bool? isHazmat,
    bool? isActive,
    DateTime? createdAt,
  }) {
    return Vehicle(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      nickname: nickname ?? this.nickname,
      type: type ?? this.type,
      heightFeet: heightFeet ?? this.heightFeet,
      widthFeet: widthFeet ?? this.widthFeet,
      lengthFeet: lengthFeet ?? this.lengthFeet,
      weightLbs: weightLbs ?? this.weightLbs,
      axleCount: axleCount ?? this.axleCount,
      hasTrailer: hasTrailer ?? this.hasTrailer,
      trailerType: trailerType ?? this.trailerType,
      isHazmat: isHazmat ?? this.isHazmat,
      isActive: isActive ?? this.isActive,
      createdAt: createdAt ?? this.createdAt,
    );
  }

  @override
  List<Object?> get props => [
        id,
        userId,
        nickname,
        type,
        heightFeet,
        widthFeet,
        lengthFeet,
        weightLbs,
        axleCount,
        hasTrailer,
        trailerType,
        isHazmat,
        isActive,
        createdAt,
      ];
}
