/// Application-wide localized string constants.
class AppStrings {
  AppStrings._();

  // --- General ---
  static const String appName = 'Smart Truck & Parking';
  static const String appTagline = 'Commercial Navigation & Parking Assistant';
  static const String comingSoon = 'Coming Soon';
  static const String retry = 'Retry';
  static const String cancel = 'Cancel';
  static const String save = 'Save';
  static const String delete = 'Delete';
  static const String edit = 'Edit';
  static const String done = 'Done';
  static const String search = 'Search';
  static const String close = 'Close';
  static const String error = 'Error';
  static const String success = 'Success';
  static const String loading = 'Loading...';

  // --- Onboarding ---
  static const String onboardingSkip = 'Skip';
  static const String onboardingNext = 'Next';
  static const String onboardingGetStarted = 'Get Started';

  static const String onboarding1Title = 'Know Where You Can Drive';
  static const String onboarding1Desc =
      'Avoid low clearance bridges, weight-restricted routes, and illegal truck turns with precision commercial-grade routing.';

  static const String onboarding2Title = 'Avoid Parking Violations';
  static const String onboarding2Desc =
      'Discover designated truck rest areas, real-time bay availability, and verified overnight parking spots along your route.';

  static const String onboarding3Title = 'Deliver Without Fines';
  static const String onboarding3Desc =
      'Receive instant alerts for municipal loading zones, time-limited deliveries, and restricted urban freight corridors.';

  // --- Authentication ---
  static const String welcomeBack = 'Welcome Back';
  static const String loginSubtitle = 'Sign in to access your commercial truck assistant';
  static const String emailLabel = 'Email Address';
  static const String emailHint = 'driver@fleet.com';
  static const String passwordLabel = 'Password';
  static const String passwordHint = '••••••••';
  static const String confirmPasswordLabel = 'Confirm Password';
  static const String confirmPasswordHint = '••••••••';
  static const String firstNameLabel = 'First Name';
  static const String firstNameHint = 'John';
  static const String lastNameLabel = 'Last Name';
  static const String lastNameHint = 'Doe';
  static const String rememberMe = 'Remember me';
  static const String forgotPassword = 'Forgot password?';
  static const String signIn = 'Sign In';
  static const String createAccount = 'Create Account';
  static const String dontHaveAccount = "Don't have an account? ";
  static const String alreadyHaveAccount = 'Already have an account? ';
  static const String registerTitle = 'Create Driver Account';
  static const String registerSubtitle = 'Set up your driver profile to get started';
  static const String driverRole = 'Commercial Driver';

  // --- Validation Messages ---
  static const String emailRequired = 'Please enter an email address';
  static const String emailInvalid = 'Please enter a valid email address';
  static const String passwordRequired = 'Please enter your password';
  static const String passwordTooShort = 'Password must be at least 8 characters';
  static const String passwordsDoNotMatch = 'Passwords do not match';
  static const String firstNameRequired = 'Please enter your first name';
  static const String lastNameRequired = 'Please enter your last name';
  static const String fieldRequired = 'This field is required';
  static const String invalidNumber = 'Please enter a valid number';

  // --- Navigation Tabs ---
  static const String navHome = 'Home';
  static const String navMap = 'Map';
  static const String navParking = 'Parking';
  static const String navAlerts = 'Alerts';
  static const String navProfile = 'Profile';

  // --- Home Dashboard ---
  static const String goodMorning = 'Good morning,';
  static const String goodAfternoon = 'Good afternoon,';
  static const String goodEvening = 'Good evening,';
  static const String driverDefault = 'Driver';
  static const String activeVehicle = 'Active Vehicle';
  static const String noActiveVehicleTitle = 'No Active Vehicle Selected';
  static const String noActiveVehiclePrompt = 'Set up your truck specifications to ensure safe routing and legal parking.';
  static const String setupVehicleButton = 'Set Up Vehicle';
  static const String quickActions = 'Quick Actions';
  static const String actionMap = 'Truck Map';
  static const String actionFindParking = 'Find Parking';
  static const String actionNavigate = 'Navigate';
  static const String actionReport = 'Report Hazard';
  static const String nearbyRestrictions = 'Nearby Restrictions';
  static const String recentAlerts = 'Recent Route Alerts';
  static const String viewAll = 'View All';
  static const String noNearbyRestrictions = 'No immediate clearance or weight restrictions nearby.';
  static const String noRecentAlerts = 'All routes clear in your perimeter.';

  // --- Vehicles ---
  static const String myVehicles = 'My Vehicles';
  static const String addVehicle = 'Add Vehicle';
  static const String editVehicle = 'Edit Vehicle';
  static const String vehicleDetails = 'Vehicle Specifications';
  static const String vehicleNickname = 'Vehicle Nickname';
  static const String vehicleNicknameHint = 'e.g. Peterbilt 579 - Big Red';
  static const String vehicleType = 'Vehicle Type';
  static const String height = 'Height';
  static const String width = 'Width';
  static const String length = 'Length';
  static const String totalWeight = 'Total Gross Weight';
  static const String axleCount = 'Axle Count';
  static const String trailerAttached = 'Trailer Attached';
  static const String trailerType = 'Trailer Type';
  static const String hazmat = 'Hazardous Materials (HAZMAT)';
  static const String noVehiclesFound = 'No vehicles configured yet.';
  static const String noVehiclesDesc = 'Add your primary commercial vehicle to calculate clearance-safe routing.';
  static const String setActiveVehicle = 'Set as Active';
  static const String activeBadge = 'Active';

  // --- Profile ---
  static const String driverProfile = 'Driver Profile';
  static const String accountSettings = 'Account Settings';
  static const String vehicleProfiles = 'Vehicle Fleet Profiles';
  static const String routingPreferences = 'Routing Preferences';
  static const String notifications = 'Notifications';
  static const String helpSupport = 'Help & Support';
  static const String privacyPolicy = 'Privacy Policy';
  static const String logout = 'Log Out';
  static const String logoutConfirmTitle = 'Log Out?';
  static const String logoutConfirmMessage = 'Are you sure you want to log out of your driver account?';
}
