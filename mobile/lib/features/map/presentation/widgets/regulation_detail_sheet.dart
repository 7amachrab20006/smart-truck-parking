import 'package:flutter/material.dart';

import '../../../../core/constants/app_colors.dart';
import '../../../regulations/domain/entities/regulation_item.dart';

class RegulationDetailSheet extends StatelessWidget {
  final RegulationItem regulation;
  final VoidCallback onClose;

  const RegulationDetailSheet({
    super.key,
    required this.regulation,
    required this.onClose,
  });

  Color _getStatusColor() {
    switch (regulation.statusColor) {
      case 'RED':
        return AppColors.error;
      case 'GREEN':
        return AppColors.success;
      case 'ORANGE':
        return AppColors.warning;
      case 'BLUE':
        return AppColors.accent;
      default:
        return AppColors.unknown;
    }
  }

  IconData _getStatusIcon() {
    switch (regulation.legalStatus) {
      case 'PROHIBITED':
        return Icons.block;
      case 'ALLOWED':
        return Icons.check_circle;
      case 'CONDITIONAL':
        return Icons.warning_amber_rounded;
      default:
        return Icons.help_outline;
    }
  }

  @override
  Widget build(BuildContext context) {
    final statusColor = _getStatusColor();

    return Container(
      decoration: const BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
        boxShadow: [
          BoxShadow(
            color: Colors.black26,
            blurRadius: 16,
            offset: Offset(0, -4),
          ),
        ],
      ),
      padding: const EdgeInsets.all(20),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header Row with Handle & Close
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: statusColor.withAlpha(30),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: statusColor),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(_getStatusIcon(), size: 16, color: statusColor),
                    const SizedBox(width: 6),
                    Text(
                      regulation.legalStatus,
                      style: TextStyle(
                        color: statusColor,
                        fontWeight: FontWeight.bold,
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ),
              IconButton(
                icon: const Icon(Icons.close),
                onPressed: onClose,
                padding: EdgeInsets.zero,
                constraints: const BoxConstraints(),
              ),
            ],
          ),
          const SizedBox(height: 12),

          // Street & Side info
          Text(
            regulation.streetName,
            style: const TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: AppColors.primary,
            ),
          ),
          Text(
            'Curb Side: ${regulation.streetSide}',
            style: const TextStyle(
              fontSize: 13,
              color: AppColors.textSecondary,
            ),
          ),
          const SizedBox(height: 12),

          // Official Sign Text Card
          if (regulation.signText != null)
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: AppColors.background,
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: AppColors.border),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'OFFICIAL POSTED SIGN:',
                    style: TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                      letterSpacing: 0.5,
                      color: AppColors.textMuted,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    regulation.signText!,
                    style: const TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                      color: AppColors.textPrimary,
                    ),
                  ),
                ],
              ),
            ),
          const SizedBox(height: 12),

          // Schedule & Hours
          if (regulation.operatingHours != null)
            Row(
              children: [
                const Icon(Icons.access_time, size: 16, color: AppColors.textSecondary),
                const SizedBox(width: 8),
                Text(
                  'Hours: ${regulation.operatingHours}',
                  style: const TextStyle(fontSize: 13, color: AppColors.textPrimary),
                ),
              ],
            ),
          const SizedBox(height: 12),

          // Source Provenance Badge
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Row(
                children: [
                  Icon(Icons.verified, size: 14, color: AppColors.accent),
                  SizedBox(width: 4),
                  Text(
                    'NYC DOT SIMS Verified',
                    style: TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w500,
                      color: AppColors.accent,
                    ),
                  ),
                ],
              ),
              Text(
                'ID: ${regulation.id}',
                style: const TextStyle(
                  fontSize: 11,
                  color: AppColors.textMuted,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
