import 'package:equatable/equatable.dart';

/// Regulation model representing a curb or street restriction on the mobile map.
class RegulationItem extends Equatable {
  final String id;
  final double latitude;
  final double longitude;
  final String streetName;
  final String streetSide;
  final String regulationType;
  final String? signText;
  final String statusColor; // RED, GREEN, ORANGE, BLUE, GRAY
  final String legalStatus; // ALLOWED, PROHIBITED, CONDITIONAL, UNKNOWN
  final String? operatingHours;
  final String verificationStatus;

  const RegulationItem({
    required this.id,
    required this.latitude,
    required this.longitude,
    required this.streetName,
    required this.streetSide,
    required this.regulationType,
    this.signText,
    required this.statusColor,
    required this.legalStatus,
    this.operatingHours,
    this.verificationStatus = 'VERIFIED',
  });

  factory RegulationItem.fromJson(Map<String, dynamic> json) {
    return RegulationItem(
      id: json['id'] as String? ?? 'sims-sign',
      latitude: (json['latitude'] as num).toDouble(),
      longitude: (json['longitude'] as num).toDouble(),
      streetName: json['street_name'] as String? ?? 'Street',
      streetSide: json['street_side'] as String? ?? 'BOTH',
      regulationType: json['regulation_type'] as String? ?? 'NO_PARKING',
      signText: json['sign_text'] as String?,
      statusColor: json['status_color'] as String? ?? 'GRAY',
      legalStatus: json['legal_status'] as String? ?? 'UNKNOWN',
      operatingHours: json['operating_hours'] as String?,
      verificationStatus: json['verification_status'] as String? ?? 'VERIFIED',
    );
  }

  @override
  List<Object?> get props => [
        id,
        latitude,
        longitude,
        streetName,
        streetSide,
        regulationType,
        signText,
        statusColor,
        legalStatus,
        operatingHours,
        verificationStatus,
      ];
}
