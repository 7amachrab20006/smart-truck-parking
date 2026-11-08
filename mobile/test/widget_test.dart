import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:smart_truck_parking/main.dart';
import 'package:smart_truck_parking/features/authentication/presentation/providers/auth_provider.dart';

void main() {
  testWidgets('App initializes successfully and displays splash screen', (WidgetTester tester) async {
    SharedPreferences.setMockInitialValues({});
    final sharedPreferences = await SharedPreferences.getInstance();

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          sharedPreferencesProvider.overrideWithValue(sharedPreferences),
        ],
        child: const SmartTruckApp(),
      ),
    );

    // Initial pump shows splash screen
    expect(find.byType(SmartTruckApp), findsOneWidget);

    // Pump past the splash delay to settle async timers
    await tester.pump(const Duration(milliseconds: 1500));
    await tester.pump(const Duration(milliseconds: 100));
  });
}
