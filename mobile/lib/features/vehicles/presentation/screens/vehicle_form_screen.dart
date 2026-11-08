import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/constants/app_colors.dart';
import '../../../../core/constants/app_strings.dart';
import '../../../../core/utils/unit_converter.dart';
import '../../../../core/utils/validators.dart';
import '../../domain/entities/vehicle.dart';
import '../providers/vehicle_provider.dart';

/// Form screen allowing commercial drivers to configure vehicle physical dimensions.
class VehicleFormScreen extends ConsumerStatefulWidget {
  final Vehicle? initialVehicle;

  const VehicleFormScreen({super.key, this.initialVehicle});

  @override
  ConsumerState<VehicleFormScreen> createState() => _VehicleFormScreenState();
}

class _VehicleFormScreenState extends ConsumerState<VehicleFormScreen> {
  final _formKey = GlobalKey<FormState>();

  late TextEditingController _nicknameController;
  late TextEditingController _heightFeetController;
  late TextEditingController _heightInchesController;
  late TextEditingController _widthFeetController;
  late TextEditingController _widthInchesController;
  late TextEditingController _lengthFeetController;
  late TextEditingController _weightLbsController;
  late TextEditingController _trailerTypeController;

  late VehicleType _selectedType;
  int _axleCount = 5;
  bool _hasTrailer = false;
  bool _isHazmat = false;
  bool _isActive = true;

  @override
  void initState() {
    super.initState();
    final v = widget.initialVehicle;

    _selectedType = v?.type ?? VehicleType.semiTruck;
    _axleCount = v?.axleCount ?? 5;
    _hasTrailer = v?.hasTrailer ?? true;
    _isHazmat = v?.isHazmat ?? false;
    _isActive = v?.isActive ?? true;

    _nicknameController = TextEditingController(text: v?.nickname ?? '');

    final initialHeight = v?.heightFeet ?? 13.5;
    final hFeet = initialHeight.floor();
    final hInches = ((initialHeight - hFeet) * 12).round();
    _heightFeetController = TextEditingController(text: hFeet.toString());
    _heightInchesController = TextEditingController(text: hInches.toString());

    final initialWidth = v?.widthFeet ?? 8.5;
    final wFeet = initialWidth.floor();
    final wInches = ((initialWidth - wFeet) * 12).round();
    _widthFeetController = TextEditingController(text: wFeet.toString());
    _widthInchesController = TextEditingController(text: wInches.toString());

    _lengthFeetController =
        TextEditingController(text: v != null ? v.lengthFeet.toStringAsFixed(0) : '53');
    _weightLbsController =
        TextEditingController(text: v != null ? v.weightLbs.toStringAsFixed(0) : '80000');
    _trailerTypeController =
        TextEditingController(text: v?.trailerType ?? 'Standard 53ft Dry Van');
  }

  @override
  void dispose() {
    _nicknameController.dispose();
    _heightFeetController.dispose();
    _heightInchesController.dispose();
    _widthFeetController.dispose();
    _widthInchesController.dispose();
    _lengthFeetController.dispose();
    _weightLbsController.dispose();
    _trailerTypeController.dispose();
    super.dispose();
  }

  IconData _iconForType(VehicleType type) {
    switch (type) {
      case VehicleType.semiTruck:
        return Icons.fire_truck;
      case VehicleType.boxTruck:
        return Icons.local_shipping;
      case VehicleType.flatbed:
        return Icons.rv_hookup;
      case VehicleType.tanker:
        return Icons.water_drop;
      case VehicleType.dumpTruck:
        return Icons.construction;
    }
  }

  Future<void> _handleSave() async {
    if (!_formKey.currentState!.validate()) return;

    final hFeet = int.tryParse(_heightFeetController.text) ?? 13;
    final hInches = int.tryParse(_heightInchesController.text) ?? 6;
    final totalHeightFeet = UnitConverter.toDecimalFeet(hFeet, hInches);

    final wFeet = int.tryParse(_widthFeetController.text) ?? 8;
    final wInches = int.tryParse(_widthInchesController.text) ?? 6;
    final totalWidthFeet = UnitConverter.toDecimalFeet(wFeet, wInches);

    final totalLengthFeet = double.tryParse(_lengthFeetController.text) ?? 53.0;
    final weight = double.tryParse(_weightLbsController.text) ?? 80000.0;

    final vehicle = Vehicle(
      id: widget.initialVehicle?.id ?? '',
      userId: widget.initialVehicle?.userId ?? 'u-current',
      nickname: _nicknameController.text.trim(),
      type: _selectedType,
      heightFeet: totalHeightFeet,
      widthFeet: totalWidthFeet,
      lengthFeet: totalLengthFeet,
      weightLbs: weight,
      axleCount: _axleCount,
      hasTrailer: _hasTrailer,
      trailerType: _hasTrailer ? _trailerTypeController.text.trim() : null,
      isHazmat: _isHazmat,
      isActive: _isActive,
      createdAt: widget.initialVehicle?.createdAt ?? DateTime.now(),
    );

    final success =
        await ref.read(vehicleNotifierProvider.notifier).saveVehicle(vehicle);

    if (success && mounted) {
      context.pop();
    }
  }

  @override
  Widget build(BuildContext context) {
    final isEditing = widget.initialVehicle != null;
    final vehicleState = ref.watch(vehicleNotifierProvider);

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: Text(isEditing ? AppStrings.editVehicle : AppStrings.addVehicle),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.pop(),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 20),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Vehicle Type Selector Section
              const Text(
                'Vehicle Classification',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: AppColors.textPrimary,
                ),
              ),
              const SizedBox(height: 12),
              SizedBox(
                height: 100,
                child: ListView.separated(
                  scrollDirection: Axis.horizontal,
                  itemCount: VehicleType.values.length,
                  separatorBuilder: (_, __) => const SizedBox(width: 12),
                  itemBuilder: (context, index) {
                    final type = VehicleType.values[index];
                    final isSelected = _selectedType == type;

                    return GestureDetector(
                      onTap: () => setState(() => _selectedType = type),
                      child: AnimatedContainer(
                        duration: const Duration(milliseconds: 200),
                        width: 110,
                        padding: const EdgeInsets.all(10),
                        decoration: BoxDecoration(
                          color: isSelected ? AppColors.primary : AppColors.surface,
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(
                            color: isSelected ? AppColors.primary : AppColors.border,
                            width: 1.5,
                          ),
                          boxShadow: isSelected
                              ? [
                                  BoxShadow(
                                    color: AppColors.primary.withAlpha(40),
                                    blurRadius: 8,
                                    offset: const Offset(0, 4),
                                  ),
                                ]
                              : [],
                        ),
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(
                              _iconForType(type),
                              color: isSelected ? AppColors.secondary : AppColors.primary,
                              size: 28,
                            ),
                            const SizedBox(height: 8),
                            Text(
                              type.label,
                              textAlign: TextAlign.center,
                              maxLines: 2,
                              overflow: TextOverflow.ellipsis,
                              style: TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.w600,
                                color: isSelected ? AppColors.secondary : AppColors.textPrimary,
                              ),
                            ),
                          ],
                        ),
                      ),
                    );
                  },
                ),
              ),
              const SizedBox(height: 24),

              // Nickname
              TextFormField(
                controller: _nicknameController,
                decoration: const InputDecoration(
                  labelText: AppStrings.vehicleNickname,
                  hintText: AppStrings.vehicleNicknameHint,
                  prefixIcon: Icon(Icons.badge_outlined),
                ),
                validator: (v) => Validators.validateRequired(v, 'Nickname'),
              ),
              const SizedBox(height: 20),

              // Physical Dimensions Section
              const Text(
                'Clearance & Dimensions (Imperial)',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: AppColors.textPrimary,
                ),
              ),
              const SizedBox(height: 12),

              // Height: Feet & Inches
              Row(
                children: [
                  Expanded(
                    flex: 3,
                    child: TextFormField(
                      controller: _heightFeetController,
                      keyboardType: TextInputType.number,
                      decoration: const InputDecoration(
                        labelText: 'Height (ft)',
                        hintText: '13',
                        prefixIcon: Icon(Icons.height),
                        suffixText: 'ft',
                      ),
                      validator: (v) => Validators.validateDimension(v, 'Height (ft)'),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    flex: 2,
                    child: TextFormField(
                      controller: _heightInchesController,
                      keyboardType: TextInputType.number,
                      decoration: const InputDecoration(
                        labelText: 'Inches',
                        hintText: '6',
                        suffixText: 'in',
                      ),
                      validator: (v) {
                        final val = int.tryParse(v ?? '');
                        if (val == null || val < 0 || val >= 12) {
                          return '0-11 in';
                        }
                        return null;
                      },
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),

              // Width: Feet & Inches
              Row(
                children: [
                  Expanded(
                    flex: 3,
                    child: TextFormField(
                      controller: _widthFeetController,
                      keyboardType: TextInputType.number,
                      decoration: const InputDecoration(
                        labelText: 'Width (ft)',
                        hintText: '8',
                        prefixIcon: Icon(Icons.swap_horiz),
                        suffixText: 'ft',
                      ),
                      validator: (v) => Validators.validateDimension(v, 'Width (ft)'),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    flex: 2,
                    child: TextFormField(
                      controller: _widthInchesController,
                      keyboardType: TextInputType.number,
                      decoration: const InputDecoration(
                        labelText: 'Inches',
                        hintText: '6',
                        suffixText: 'in',
                      ),
                      validator: (v) {
                        final val = int.tryParse(v ?? '');
                        if (val == null || val < 0 || val >= 12) {
                          return '0-11 in';
                        }
                        return null;
                      },
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),

              // Length (ft) & Total Weight (lbs)
              Row(
                children: [
                  Expanded(
                    child: TextFormField(
                      controller: _lengthFeetController,
                      keyboardType: TextInputType.number,
                      decoration: const InputDecoration(
                        labelText: 'Total Length (ft)',
                        hintText: '53',
                        prefixIcon: Icon(Icons.straighten),
                        suffixText: 'ft',
                      ),
                      validator: (v) => Validators.validateDimension(v, 'Length'),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: TextFormField(
                      controller: _weightLbsController,
                      keyboardType: TextInputType.number,
                      decoration: const InputDecoration(
                        labelText: 'Gross Weight (lbs)',
                        hintText: '80000',
                        prefixIcon: Icon(Icons.scale),
                        suffixText: 'lbs',
                      ),
                      validator: Validators.validateWeight,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 20),

              // Axle Count Selector
              const Text(
                'Axle Count',
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                  color: AppColors.textPrimary,
                ),
              ),
              const SizedBox(height: 8),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [2, 3, 4, 5, 6, 7].map((count) {
                  final isSelected = _axleCount == count;
                  return ChoiceChip(
                    label: Text('$count'),
                    selected: isSelected,
                    selectedColor: AppColors.primary,
                    labelStyle: TextStyle(
                      color: isSelected ? AppColors.secondary : AppColors.textPrimary,
                      fontWeight: FontWeight.bold,
                    ),
                    onSelected: (selected) {
                      if (selected) setState(() => _axleCount = count);
                    },
                  );
                }).toList(),
              ),
              const SizedBox(height: 24),

              // Trailer Toggle Section
              Card(
                margin: EdgeInsets.zero,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                  side: const BorderSide(color: AppColors.border),
                ),
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                  child: Column(
                    children: [
                      SwitchListTile(
                        contentPadding: EdgeInsets.zero,
                        title: const Text(
                          AppStrings.trailerAttached,
                          style: TextStyle(fontWeight: FontWeight.w600),
                        ),
                        subtitle: const Text('Account for trailer articulation and length'),
                        value: _hasTrailer,
                        activeThumbColor: AppColors.primary,
                        onChanged: (val) => setState(() => _hasTrailer = val),
                      ),
                      if (_hasTrailer) ...[
                        const Divider(height: 1),
                        const SizedBox(height: 12),
                        TextFormField(
                          controller: _trailerTypeController,
                          decoration: const InputDecoration(
                            labelText: AppStrings.trailerType,
                            hintText: 'e.g. 53ft Refrigerated Reefer',
                          ),
                        ),
                        const SizedBox(height: 8),
                      ],
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),

              // HAZMAT Toggle Card
              Card(
                margin: EdgeInsets.zero,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                  side: const BorderSide(color: AppColors.border),
                ),
                child: SwitchListTile(
                  title: const Text(
                    AppStrings.hazmat,
                    style: TextStyle(fontWeight: FontWeight.w600),
                  ),
                  subtitle: const Text('Enforce hazmat-prohibited tunnel & corridor routing'),
                  value: _isHazmat,
                  activeThumbColor: AppColors.warning,
                  onChanged: (val) => setState(() => _isHazmat = val),
                ),
              ),
              const SizedBox(height: 32),

              // Save Button
              ElevatedButton(
                onPressed: vehicleState.isLoading ? null : _handleSave,
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.primary,
                  foregroundColor: AppColors.secondary,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
                child: vehicleState.isLoading
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          valueColor: AlwaysStoppedAnimation<Color>(AppColors.secondary),
                        ),
                      )
                    : Text(
                        isEditing ? 'Save Vehicle Specs' : 'Add Vehicle to Fleet',
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
              ),
              const SizedBox(height: 30),
            ],
          ),
        ),
      ),
    );
  }
}
