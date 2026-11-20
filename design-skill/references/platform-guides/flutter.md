# Flutter Platform Guide

**Design token mappings, accessibility requirements, and component patterns for Flutter.** All tokens reference the canonical system in `token-reference.md`.

---

## Design Token Mapping

### Colors (Color / ColorScheme)
```dart
// Light theme
final lightColorScheme = ColorScheme.light(
  primary: Color(0xFF2563EB),
  onPrimary: Color(0xFFFFFFFF),
  primaryContainer: Color(0xFFDBEAFE),
  onPrimaryContainer: Color(0xFF1E3A5F),

  secondary: Color(0xFF64748B),
  onSecondary: Color(0xFFFFFFFF),
  secondaryContainer: Color(0xFFE2E8F0),
  onSecondaryContainer: Color(0xFF334155),

  tertiary: Color(0xFF0284C7),
  onTertiary: Color(0xFFFFFFFF),
  tertiaryContainer: Color(0xFFE0F2FE),
  onTertiaryContainer: Color(0xFF0165A3),

  error: Color(0xFFDC2626),
  onError: Color(0xFFFFFFFF),
  errorContainer: Color(0xFFFEF2F2),
  onErrorContainer: Color(0xFFB91C1C),

  surface: Color(0xFFFFFFFF),
  onSurface: Color(0xFF0F172A),
  onSurfaceVariant: Color(0xFF475569),
  surfaceContainerHighest: Color(0xFFF8FAFC),

  outline: Color(0xFFE2E8F0),
  outlineVariant: Color(0xFFCBD5E1),

  surfaceTint: Color(0xFF2563EB),
  shadow: Color(0xFF000000),
  scrim: Color(0xFF000000),
);

// Dark theme
final darkColorScheme = ColorScheme.dark(
  primary: Color(0xFF3B82F6),
  onPrimary: Color(0xFF0F172A),
  primaryContainer: Color(0xFF1E40AF),
  onPrimaryContainer: Color(0xFFDBEAFE),

  secondary: Color(0xFF94A3B8),
  onSecondary: Color(0xFF0F172A),
  secondaryContainer: Color(0xFF475569),
  onSecondaryContainer: Color(0xFFE2E8F0),

  tertiary: Color(0xFF38BDF8),
  onTertiary: Color(0xFF0F172A),
  tertiaryContainer: Color(0xFF0165A3),
  onTertiaryContainer: Color(0xFFE0F2FE),

  error: Color(0xFFF87171),
  onError: Color(0xFF7F1D1D),
  errorContainer: Color(0xFF7F1D1D),
  onErrorContainer: Color(0xFFFECACA),

  surface: Color(0xFF0F172A),
  onSurface: Color(0xFFF1F5F9),
  onSurfaceVariant: Color(0xFFCBD5E1),
  surfaceContainerHighest: Color(0xFF1E293B),

  outline: Color(0xFF475569),
  outlineVariant: Color(0xFF334155),

  surfaceTint: Color(0xFF3B82F6),
  shadow: Color(0xFF000000),
  scrim: Color(0xFF000000),
);

// Semantic extensions
extension SemanticColors on ColorScheme {
  Color get focusRing => brightness == Brightness.light
      ? Color(0xFF2563EB)
      : Color(0xFF60A5FA);

  Color get disabledBg => brightness == Brightness.light
      ? Color(0xFFF1F5F9)
      : Color(0xFF1E293B);

  Color get disabledText => brightness == Brightness.light
      ? Color(0xFF94A3B8)
      : Color(0xFF64748B);
}
```

### Spacing (Double)
```dart
// 4px base grid (Flutter uses logical pixels)
const double space1 = 4.0;
const double space2 = 8.0;
const double space3 = 12.0;
const double space4 = 16.0;
const double space5 = 20.0;
const double space6 = 24.0;
const double space8 = 32.0;
const double space10 = 40.0;
const double space12 = 48.0;
const double space16 = 64.0;

// Semantic aliases
const double spaceXS = space1;
const double spaceSM = space2;
const double spaceMD = space4;
const double spaceLG = space6;
const double spaceXL = space8;
const double space2XL = space12;
const double space3XL = space16;
```

### Typography (TextStyle)
```dart
// Font family
const String fontFamily = 'system-ui'; // Uses platform default

// Modular scale (1.25 ratio) — Flutter uses logical pixels
const TextStyle heading1 = TextStyle(
  fontFamily: fontFamily,
  fontSize: 48,
  fontWeight: FontWeight.w700,
  height: 1.25,
  letterSpacing: -0.02,
);

const TextStyle heading2 = TextStyle(
  fontFamily: fontFamily,
  fontSize: 36,
  fontWeight: FontWeight.w700,
  height: 1.25,
  letterSpacing: 0,
);

const TextStyle heading3 = TextStyle(
  fontFamily: fontFamily,
  fontSize: 30,
  fontWeight: FontWeight.w600,
  height: 1.25,
  letterSpacing: 0,
);

const TextStyle heading4 = TextStyle(
  fontFamily: fontFamily,
  fontSize: 24,
  fontWeight: FontWeight.w600,
  height: 1.3,
  letterSpacing: 0,
);

const TextStyle heading5 = TextStyle(
  fontFamily: fontFamily,
  fontSize: 20,
  fontWeight: FontWeight.w500,
  height: 1.4,
  letterSpacing: 0,
);

const TextStyle heading6 = TextStyle(
  fontFamily: fontFamily,
  fontSize: 18,
  fontWeight: FontWeight.w500,
  height: 1.4,
  letterSpacing: 0,
);

const TextStyle body = TextStyle(
  fontFamily: fontFamily,
  fontSize: 16,
  fontWeight: FontWeight.w400,
  height: 1.5,
  letterSpacing: 0,
);

const TextStyle bodySM = TextStyle(
  fontFamily: fontFamily,
  fontSize: 14,
  fontWeight: FontWeight.w400,
  height: 1.5,
  letterSpacing: 0,
);

const TextStyle caption = TextStyle(
  fontFamily: fontFamily,
  fontSize: 12,
  fontWeight: FontWeight.w400,
  height: 1.5,
  letterSpacing: 0,
);

const TextStyle overline = TextStyle(
  fontFamily: fontFamily,
  fontSize: 10,
  fontWeight: FontWeight.w500,
  height: 1.5,
  letterSpacing: 0.02,
);

// Semantic aliases
const TextStyle fontSizeXS = caption;
const TextStyle fontSizeSM = bodySM;
const TextStyle fontSizeMD = body;
const TextStyle fontSizeLG = TextStyle(
  fontFamily: fontFamily,
  fontSize: 18,
  fontWeight: FontWeight.w400,
  height: 1.5,
);
const TextStyle fontSizeXL = heading5;
const TextStyle fontSize2XL = heading4;
const TextStyle fontSize3XL = heading3;
const TextStyle fontSize4XL = heading2;
const TextStyle fontSize5XL = heading1;
```

### Border Radius (BorderRadius)
```dart
const BorderRadius radiusSM = BorderRadius.all(Radius.circular(4));
const BorderRadius radiusMD = BorderRadius.all(Radius.circular(6));
const BorderRadius radiusLG = BorderRadius.all(Radius.circular(8));
const BorderRadius radiusXL = BorderRadius.all(Radius.circular(12));
const BorderRadius radiusFull = BorderRadius.all(Radius.circular(9999));

const BorderRadius radiusButton = radiusMD;
const BorderRadius radiusInput = radiusMD;
const BorderRadius radiusCard = radiusLG;
const BorderRadius radiusModal = radiusXL;
const BorderRadius radiusBadge = radiusFull;
```

### Shadows (BoxShadow)
```dart
const List<BoxShadow> shadowSM = [
  BoxShadow(
    color: Color(0x0D000000), // 5% opacity
    offset: Offset(0, 1),
    blurRadius: 2,
    spreadRadius: 0,
  ),
];

const List<BoxShadow> shadowMD = [
  BoxShadow(
    color: Color(0x1A000000), // 10% opacity
    offset: Offset(0, 4),
    blurRadius: 6,
    spreadRadius: -1,
  ),
  BoxShadow(
    color: Color(0x1A000000),
    offset: Offset(0, 2),
    blurRadius: 4,
    spreadRadius: -2,
  ),
];

const List<BoxShadow> shadowLG = [
  BoxShadow(
    color: Color(0x1A000000),
    offset: Offset(0, 10),
    blurRadius: 15,
    spreadRadius: -3,
  ),
  BoxShadow(
    color: Color(0x1A000000),
    offset: Offset(0, 4),
    blurRadius: 6,
    spreadRadius: -4,
  ),
];

const List<BoxShadow> shadowCard = shadowMD;
const List<BoxShadow> shadowModal = shadowLG;
```

### Breakpoints (MediaQuery / LayoutBuilder)
```dart
// Flutter uses layout-based breakpoints (not media queries)
class Breakpoints {
  static const double xs = 480;
  static const double sm = 640;
  static const double md = 768;
  static const double lg = 1024;
  static const double xl = 1280;
  static const double xxl = 1536;
}

// Usage with LayoutBuilder
LayoutBuilder(
  builder: (context, constraints) {
    if (constraints.maxWidth < Breakpoints.sm) {
      return MobileLayout();
    } else if (constraints.maxWidth < Breakpoints.lg) {
      return TabletLayout();
    } else {
      return DesktopLayout();
    }
  },
)

// Or with MediaQuery (for full-screen decisions)
MediaQuery.of(context).size.width < Breakpoints.md
```

---

## Accessibility Requirements (Flutter)

### Semantics (Screen Readers)
```dart
// Labels
Semantics(
  label: 'Submit form',
  hint: 'Submits your registration data',
  button: true,
  child: ElevatedButton(
    onPressed: () {},
    child: Text('Submit'),
  ),
)

// Exclude decorative elements
Semantics(
  excludeSemantics: true, // Ignored by screen readers
  child: Icon(Icons.decoration),
)

// Live regions
Semantics(
  liveRegion: true, // Announces changes
  child: Text(errorMessage),
)

// Headings
Semantics(
  header: true,
  child: Text('Section Title', style: heading3),
)

// Custom actions
Semantics(
  customSemanticsActions: [
    CustomSemanticsAction(
      id: 'delete',
      label: 'Delete',
      action: () { delete(); },
    ),
  ],
  child: ListTile(...),
)
```

### Touch Targets (48×48dp Minimum)
```dart
// Material buttons already meet 48dp
ElevatedButton(
  onPressed: () {},
  child: Text('Button'), // Automatically 48dp height
)

// For custom widgets, enforce minimum
SizedBox(
  width: 48,
  height: 48,
  child: IconButton(
    icon: Icon(Icons.settings),
    onPressed: () {},
  ),
)

// Expand touch area for small content
InkWell(
  onTap: () {},
  child: Padding(
    padding: EdgeInsets.all(16), // 24 icon + 32 padding = 56
    child: Icon(Icons.link),
  ),
)

// Minimum touch target wrapper
class MinimumTouchTarget extends StatelessWidget {
  final Widget child;
  const MinimumTouchTarget({required this.child});

  @override
  Widget build(BuildContext context) {
    return ConstrainedBox(
      constraints: BoxConstraints(minWidth: 48, minHeight: 48),
      child: child,
    );
  }
}
```

### High Contrast / Color Blindness
```dart
// Check high contrast mode
MediaQuery.of(context).highContrast

// Don't rely on color alone
// BAD: Red border only
// GOOD: Red border + Icon(Icons.error) + Text('Error')

// Use Theme colors (automatically adapt)
Container(
  decoration: BoxDecoration(
    border: Border.all(
      color: Theme.of(context).colorScheme.error, // Adapts to contrast
      width: 2,
    ),
  ),
)
```

### Font Scaling (Text Scale Factor)
```dart
// Flutter respects textScaleFactor automatically
Text('Hello', style: TextStyle(fontSize: 16)) // Scales with system setting

// Limit scaling
MediaQuery(
  data: MediaQuery.of(context).copyWith(
    textScaler: TextScaler.linear(1.3), // Max 130%
  ),
  child: Text('Limited scaling', style: TextStyle(fontSize: 16)),
)

// Disable scaling (rare)
MediaQuery(
  data: MediaQuery.of(context).copyWith(
    textScaler: TextScaler.noScaling,
  ),
  child: Text('Fixed', style: TextStyle(fontSize: 16)),
)
```

### RTL Support
```dart
// Flutter handles RTL automatically for most widgets
// Use start/end alignment
Row(
  mainAxisAlignment: MainAxisAlignment.start, // Works RTL
  children: [...],
)

// For explicit RTL
Directionality(
  textDirection: TextDirection.rtl,
  child: MyWidget(),
)

// Check direction
Directionality.of(context) == TextDirection.rtl
```

---

## Component Mappings

| Web Component | Flutter (Material 3) | Cupertino (iOS-style) | Notes |
|---------------|---------------------|----------------------|-------|
| `<button>` | `ElevatedButton`, `FilledButton`, `OutlinedButton`, `TextButton` | `CupertinoButton` | Use `FilledButton` for primary |
| `<input>` | `TextField` / `TextFormField` | `CupertinoTextField` | Use `TextFormField` for forms |
| `<select>` | `DropdownButton` / `DropdownMenu` (Material 3) | `CupertinoPicker` | `DropdownMenu` is newer |
| `<dialog>` | `AlertDialog`, `Dialog`, `showModalBottomSheet` | `CupertinoAlertDialog` | Use `showDialog` |
| `<nav>` | `NavigationBar` (bottom), `NavigationDrawer` (side) | `CupertinoTabBar` / `CupertinoNavigationBar` | |
| `<aside>` | `NavigationDrawer` / `Drawer` | N/A | |
| `<table>` | `DataTable` / `PaginatedDataTable` | N/A | `DataTable` for data grids |
| `<form>` | `Form` + `TextFormField` | `Form` + `CupertinoTextField` | `Form` for validation |
| Toast | `SnackBar` / `Toast` (package) | N/A | `SnackBar` is Material |
| Tooltip | `Tooltip` | N/A | Built-in |

---

## Material 3 Component Usage

### Buttons
```dart
// Primary (filled)
FilledButton(
  onPressed: () {},
  child: Text('Primary'),
)

// Secondary (outlined)
OutlinedButton(
  onPressed: () {},
  child: Text('Secondary'),
)

// Tertiary (text)
TextButton(
  onPressed: () {},
  child: Text('Tertiary'),
)

// Danger
FilledButton(
  onPressed: () {},
  style: FilledButton.styleFrom(
    backgroundColor: Theme.of(context).colorScheme.error,
    foregroundColor: Theme.of(context).colorScheme.onError,
  ),
  child: Text('Delete'),
)

// Icon button
IconButton(
  onPressed: () {},
  icon: Icon(Icons.settings),
  tooltip: 'Settings', // Accessibility
)
```

### Text Fields
```dart
TextFormField(
  decoration: InputDecoration(
    labelText: 'Email',
    hintText: 'you@example.com',
    prefixIcon: Icon(Icons.email_outlined),
    suffixIcon: error ? Icon(Icons.error, color: colorScheme.error) : null,
    errorText: error ? 'Invalid email' : null,
    helperText: 'We\'ll never share your email',
    border: OutlineInputBorder(
      borderRadius: radiusInput,
    ),
  ),
  keyboardType: TextInputType.emailAddress,
  textInputAction: TextInputAction.done,
  validator: (value) {
    if (value?.isEmpty ?? true) return 'Required';
    if (!value!.contains('@')) return 'Invalid email';
    return null;
  },
)
```

### Cards
```dart
// Elevated card
Card(
  elevation: 3,
  shape: RoundedRectangleBorder(borderRadius: radiusCard),
  child: Padding(
    padding: EdgeInsets.all(spaceMD),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Title', style: Theme.of(context).textTheme.titleMedium),
        SizedBox(height: spaceSM),
        Text('Description', style: Theme.of(context).textTheme.bodyMedium),
      ],
    ),
  ),
)

// Outlined card
Card(
  elevation: 0,
  shape: RoundedRectangleBorder(
    borderRadius: radiusCard,
    side: BorderSide(color: colorScheme.outline),
  ),
  child: Padding(...),
)
```

### Navigation
```dart
// Bottom navigation
NavigationBar(
  destinations: [
    NavigationDestination(icon: Icon(Icons.home), label: 'Home'),
    NavigationDestination(icon: Icon(Icons.search), label: 'Search'),
    NavigationDestination(icon: Icon(Icons.person), label: 'Profile'),
  ],
  selectedIndex: currentIndex,
  onDestinationSelected: (index) => setState(() => currentIndex = index),
)

// Navigation drawer
NavigationDrawer(
  children: [
    DrawerHeader(child: Text('Menu')),
    ListTile(
      leading: Icon(Icons.home),
      title: Text('Home'),
      onTap: () {},
    ),
    // ...
  ],
)
```

---

## Platform-Specific Tokens

### Flutter-Specific Additions
```dart
// Standard dimensions (Material guidelines)
const double kToolbarHeight = 56.0;
const double kBottomNavigationBarHeight = 80.0; // Material 3 taller
const double kTabBarHeight = 48.0;
const double kTextFieldHeight = 56.0; // With label
const double kMinTouchTarget = 48.0;

// Animation durations
const Duration animFast = Duration(milliseconds: 100);
const Duration animMedium = Duration(milliseconds: 200);
const Duration animSlow = Duration(milliseconds: 300);

// Theme extensions for custom tokens
class AppThemeExtension extends ThemeExtension<AppThemeExtension> {
  final Color focusRing;
  final Color disabledBg;
  final Color disabledText;

  const AppThemeExtension({
    required this.focusRing,
    required this.disabledBg,
    required this.disabledText,
  });

  @override
  AppThemeExtension copyWith({
    Color? focusRing,
    Color? disabledBg,
    Color? disabledText,
  }) {
    return AppThemeExtension(
      focusRing: focusRing ?? this.focusRing,
      disabledBg: disabledBg ?? this.disabledBg,
      disabledText: disabledText ?? this.disabledText,
    );
  }

  @override
  AppThemeExtension lerp(ThemeExtension<AppThemeExtension>? other, double t) {
    if (other is! AppThemeExtension) return this;
    return AppThemeExtension(
      focusRing: Color.lerp(focusRing, other.focusRing, t)!,
      disabledBg: Color.lerp(disabledBg, other.disabledBg, t)!,
      disabledText: Color.lerp(disabledText, other.disabledText, t)!,
    );
  }
}
```

---

## Theme Setup

```dart
// main.dart
MaterialApp(
  theme: ThemeData(
    useMaterial3: true,
    colorScheme: lightColorScheme,
    textTheme: TextTheme(
      displayLarge: heading1,
      displayMedium: heading2,
      displaySmall: heading3,
      headlineLarge: heading4,
      headlineMedium: heading5,
      headlineSmall: heading6,
      bodyLarge: body,
      bodyMedium: bodySM,
      bodySmall: caption,
      labelLarge: TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
      labelMedium: TextStyle(fontSize: 12, fontWeight: FontWeight.w500),
      labelSmall: TextStyle(fontSize: 11, fontWeight: FontWeight.w500),
    ),
    extensions: [
      AppThemeExtension(
        focusRing: Color(0xFF2563EB),
        disabledBg: Color(0xFFF1F5F9),
        disabledText: Color(0xFF94A3B8),
      ),
    ],
    // Component themes
    filledButtonTheme: FilledButtonThemeData(
      style: FilledButton.styleFrom(
        shape: RoundedRectangleBorder(borderRadius: radiusButton),
        padding: EdgeInsets.symmetric(horizontal: space4, vertical: space2),
        textStyle: TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
      ),
    ),
    outlinedButtonTheme: OutlinedButtonThemeData(...),
    textButtonTheme: TextButtonThemeData(...),
    inputDecorationTheme: InputDecorationTheme(
      border: OutlineInputBorder(borderRadius: radiusInput),
      filled: true,
      fillColor: lightColorScheme.surface,
      contentPadding: EdgeInsets.symmetric(horizontal: space3, vertical: space2),
    ),
    cardTheme: CardTheme(
      elevation: 3,
      shape: RoundedRectangleBorder(borderRadius: radiusCard),
      margin: EdgeInsets.all(spaceMD),
    ),
  ),
  darkTheme: ThemeData(
    useMaterial3: true,
    colorScheme: darkColorScheme,
    // ... same component themes
    extensions: [
      AppThemeExtension(
        focusRing: Color(0xFF60A5FA),
        disabledBg: Color(0xFF1E293B),
        disabledText: Color(0xFF64748B),
      ),
    ],
  ),
  themeMode: ThemeMode.system,
)
```

---

## Testing Checklist (Flutter)

- [ ] TalkBack / VoiceOver works (semantics labels, hints)
- [ ] Text scales with system font size (test 0.85x - 2.0x)
- [ ] Touch targets ≥48×48dp
- [ ] High contrast mode works
- [ ] Dark theme: all colors adapt correctly
- [ ] RTL: Arabic/Hebrew layouts work
- [ ] Landscape orientation works
- [ ] Foldable/dual-screen layouts work
- [ ] LayoutBuilder breakpoints: mobile/tablet/desktop
- [ ] Keyboard navigation (Tab, Enter, Escape, arrows)
- [ ] Screen magnification (triple-tap zoom)

---

## Handoff from Web Design

| Web Token | Flutter Token | Conversion |
|-----------|---------------|------------|
| `--color-primary` | `ColorScheme.primary` | Direct hex → `Color(0xFF2563EB)` |
| `--space-4` | `space4` (16.0) | 16px = 16.0 (logical pixels) |
| `--font-size-md` | `body` (16.0) | 16px = 16.0 (scales with textScaleFactor!) |
| `--radius-md` | `radiusMD` (6.0) | 6px = 6.0 |
| `--shadow-md` | `shadowMD` | Convert to `List<BoxShadow>` |
| `clamp()` fluid type | `textScaleFactor` | Different paradigm — use system scaling |
| `@media (min-width: 768px)` | `LayoutBuilder` + `constraints.maxWidth` | Layout-based, not viewport-based |

**Key difference**: Flutter uses **layout-based breakpoints** (`LayoutBuilder`) and **system text scaling** instead of CSS media queries and fluid type. Design for *constraints*, not fixed viewports.