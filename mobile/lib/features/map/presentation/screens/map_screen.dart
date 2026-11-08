import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/constants/app_colors.dart';
import '../../../regulations/domain/entities/regulation_item.dart';
import '../providers/map_provider.dart';
import '../widgets/regulation_detail_sheet.dart';

class MapScreen extends ConsumerStatefulWidget {
  const MapScreen({super.key});

  @override
  ConsumerState<MapScreen> createState() => _MapScreenState();
}

class _MapScreenState extends ConsumerState<MapScreen> {
  Color _getColorForStatus(String color) {
    switch (color) {
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

  void _showRegulationDetails(RegulationItem item) {
    ref.read(mapNotifierProvider.notifier).selectRegulation(item);
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) => RegulationDetailSheet(
        regulation: item,
        onClose: () => Navigator.pop(ctx),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final mapState = ref.watch(mapNotifierProvider);
    final displayedRegs = mapState.filteredRegulations;

    return Scaffold(
      appBar: AppBar(
        title: const Text('NYC Smart Curb Map'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            tooltip: 'Refresh regulations',
            onPressed: () {
              ref.read(mapNotifierProvider.notifier).fetchRegulations();
            },
          ),
        ],
      ),
      body: Stack(
        children: [
          // Background Map Visual Canvas
          Container(
            color: const Color(0xFFE8ECEF),
            child: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.map_outlined, size: 80, color: AppColors.primary.withAlpha(60)),
                  const SizedBox(height: 12),
                  const Text(
                    'Manhattan Pilot Zone',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: AppColors.primary,
                    ),
                  ),
                  const Text(
                    'NYC DOT Regulatory & Loading Grid',
                    style: TextStyle(
                      fontSize: 13,
                      color: AppColors.textSecondary,
                    ),
                  ),
                ],
              ),
            ),
          ),

          // Top Regulation Category Filters
          Positioned(
            top: 12,
            left: 12,
            right: 12,
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: [
                  _buildFilterChip('ALL', 'All Curbs', mapState.activeFilter),
                  const SizedBox(width: 8),
                  _buildFilterChip('LOADING', 'Loading Zones', mapState.activeFilter),
                  const SizedBox(width: 8),
                  _buildFilterChip('PARKING', 'Parking Rules', mapState.activeFilter),
                  const SizedBox(width: 8),
                  _buildFilterChip('TRUCK', 'Truck Routes', mapState.activeFilter),
                ],
              ),
            ),
          ),

          // Bottom Draggable / Scrollable Sheet of Verified Nearby Regulations
          DraggableScrollableSheet(
            initialChildSize: 0.38,
            minChildSize: 0.18,
            maxChildSize: 0.85,
            builder: (context, scrollController) {
              return Container(
                decoration: const BoxDecoration(
                  color: AppColors.surface,
                  borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black12,
                      blurRadius: 10,
                      offset: Offset(0, -2),
                    ),
                  ],
                ),
                child: ListView.builder(
                  controller: scrollController,
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                  itemCount: displayedRegs.length + 1,
                  itemBuilder: (context, index) {
                    if (index == 0) {
                      return Column(
                        children: [
                          Center(
                            child: Container(
                              width: 36,
                              height: 4,
                              margin: const EdgeInsets.only(bottom: 12, top: 4),
                              decoration: BoxDecoration(
                                color: AppColors.border,
                                borderRadius: BorderRadius.circular(2),
                              ),
                            ),
                          ),
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text(
                                'Nearby Curb Rules (${displayedRegs.length})',
                                style: const TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.bold,
                                  color: AppColors.primary,
                                ),
                              ),
                              const Text(
                                'NYC DOT SIMS',
                                style: TextStyle(
                                  fontSize: 11,
                                  fontWeight: FontWeight.w500,
                                  color: AppColors.accent,
                                ),
                              ),
                            ],
                          ),
                          const Divider(height: 16),
                        ],
                      );
                    }

                    final item = displayedRegs[index - 1];
                    final color = _getColorForStatus(item.statusColor);

                    return Card(
                      margin: const EdgeInsets.only(bottom: 10),
                      elevation: 0,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                        side: BorderSide(color: AppColors.border.withAlpha(120)),
                      ),
                      child: ListTile(
                        onTap: () => _showRegulationDetails(item),
                        leading: CircleAvatar(
                          backgroundColor: color.withAlpha(35),
                          child: Icon(
                            item.statusColor == 'BLUE'
                                ? Icons.local_shipping
                                : item.statusColor == 'RED'
                                    ? Icons.block
                                    : Icons.check_circle,
                            color: color,
                            size: 20,
                          ),
                        ),
                        title: Text(
                          item.streetName,
                          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                        ),
                        subtitle: Text(
                          item.signText ?? item.regulationType,
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: const TextStyle(fontSize: 12),
                        ),
                        trailing: Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                          decoration: BoxDecoration(
                            color: color.withAlpha(25),
                            borderRadius: BorderRadius.circular(6),
                            border: Border.all(color: color.withAlpha(150)),
                          ),
                          child: Text(
                            item.legalStatus,
                            style: TextStyle(
                              color: color,
                              fontWeight: FontWeight.bold,
                              fontSize: 11,
                            ),
                          ),
                        ),
                      ),
                    );
                  },
                ),
              );
            },
          ),
        ],
      ),
    );
  }

  Widget _buildFilterChip(String filterKey, String label, String activeFilter) {
    final isSelected = activeFilter == filterKey;
    return ChoiceChip(
      label: Text(label),
      selected: isSelected,
      onSelected: (_) {
        ref.read(mapNotifierProvider.notifier).setFilter(filterKey);
      },
      selectedColor: AppColors.primary,
      backgroundColor: AppColors.surface,
      labelStyle: TextStyle(
        color: isSelected ? Colors.white : AppColors.primary,
        fontWeight: FontWeight.w600,
        fontSize: 12,
      ),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(20),
        side: const BorderSide(color: AppColors.border),
      ),
    );
  }
}
