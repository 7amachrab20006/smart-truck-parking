import '../../domain/entities/vehicle.dart';

/// Vehicle data transfer model with JSON serialization.
class VehicleModel extends Vehicle {
  const VehicleModel({
    required super.id,
    required super.userId,
    required super.nickname,
    required super.type,
    required super.heightFeet,
    required super.widthFeet,
    required super.lengthFeet,
    required super.weightLbs,
    required super.axleCount,
    super.hasTrailer = false,
    super.trailerType,
    super.isHazmat = false,
    super.isActive = false,
    super.createdAt,
  });

  /// Factory constructor to parse JSON payloads.
  factory VehicleModel.fromJson(Map<String, dynamic> json) {
    return VehicleModel(
      id: (json['id'] ?? json['_id'] ?? '').toString(),
      userId: (json['userId'] ?? json['user_id'] ?? '').toString(),
      nickname: (json['nickname'] ?? json['name'] ?? 'Commercial Truck').toString(),
      type: VehicleType.fromKey((json['type'] ?? 'semi_truck').toString()),
      heightFeet: (json['heightFeet'] ?? json['height_feet'] ?? 13.5).toDouble(),
      widthFeet: (json['widthFeet'] ?? json['width_feet'] ?? 8.5).toDouble(),
      lengthFeet: (json['lengthFeet'] ?? json['length_feet'] ?? 53.0).toDouble(),
      weightLbs: (json['weightLbs'] ?? json['weight_lbs'] ?? 80000.0).toDouble(),
      axleCount: (json['axleCount'] ?? json['axle_count'] ?? 5) as int,
      hasTrailer: json['hasTrailer'] ?? json['has_trailer'] ?? false,
      trailerType: json['trailerType'] as String? ?? json['trailer_type'] as String?,
      isHazmat: json['isHazmat'] ?? json['is_hazmat'] ?? false,
      isActive: json['isActive'] ?? json['is_active'] ?? false,
      createdAt: json['createdAt'] != null
          ? DateTime.tryParse(json['createdAt'].toString())
          : (json['created_at'] != null
              ? DateTime.tryParse(json['created_at'].toString())
              : null),
    );
  }

  /// Serializes vehicle into JSON.
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'userId': userId,
      'nickname': nickname,
      'type': type.key,
      'heightFeet': heightFeet,
      'widthFeet': widthFeet,
      'lengthFeet': lengthFeet,
      'weightLbs': weightLbs,
      'axleCount': axleCount,
      'hasTrailer': hasTrailer,
      'trailerType': trailerType,
      'isHazmat': isHazmat,
      'isActive': isActive,
      'createdAt': createdAt?.toIso8601String(),
    };
  }

  /// Converts a [Vehicle] domain entity into [VehicleModel].
  factory VehicleModel.fromEntity(Vehicle vehicle) {
    return VehicleModel(
      id: vehicle.id,
      userId: vehicle.userId,
      nickname: vehicle.nickname,
      type: vehicle.type,
      heightFeet: vehicle.heightFeet,
      widthFeet: vehicle.widthFeet,
      lengthFeet: vehicle.lengthFeet,
      weightLbs: vehicle.weightLbs,
      axleCount: vehicle.axleCount,
      hasTrailer: vehicle.hasTrailer,
      trailerType: vehicle.trailerType,
      isHazmat: vehicle.isHazmat,
      isActive: vehicle.isActive,
      createdAt: vehicle.createdAt,
    );
  }

  /// Converts this model into a domain entity.
  Vehicle toEntity() {
    return Vehicle(
      id: id,
      userId: userId,
      nickname: nickname,
      type: type,
      heightFeet: heightFeet,
      widthFeet: widthFeet,
      lengthFeet: lengthFeet,
      weightLbs: weightLbs,
      axleCount: axleCount,
      hasTrailer: hasTrailer,
      trailerType: trailerType,
      isHazmat: isHazmat,
      isActive: isActive,
      createdAt: createdAt,
    );
  }
}
