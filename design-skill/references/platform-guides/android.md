# Android / Material Design Platform Guide

**Design token mappings, accessibility requirements, and component patterns for Android (Jetpack Compose & XML).** All tokens reference the canonical system in `token-reference.md`.

---

## Design Token Mapping

### Colors (Color / ColorStateList)
```kotlin
// Light theme
val LightColorScheme = lightColorScheme(
    primary = Color(0xFF2563EB),
    onPrimary = Color(0xFFFFFFFF),
    primaryContainer = Color(0xFFDBEAFE),
    onPrimaryContainer = Color(0xFF1E3A5F),

    secondary = Color(0xFF64748B),
    onSecondary = Color(0xFFFFFFFF),
    secondaryContainer = Color(0xFFE2E8F0),
    onSecondaryContainer = Color(0xFF334155),

    tertiary = Color(0xFF0284C7),
    onTertiary = Color(0xFFFFFFFF),
    tertiaryContainer = Color(0xFFE0F2FE),
    onTertiaryContainer = Color(0xFF0165A3),

    error = Color(0xFFDC2626),
    onError = Color(0xFFFFFFFF),
    errorContainer = Color(0xFFFEF2F2),
    onErrorContainer = Color(0xFFB91C1C),

    surface = Color(0xFFFFFFFF),
    onSurface = Color(0xFF0F172A),
    surfaceContainerHighest = Color(0xFFF8FAFC),
    onSurfaceVariant = Color(0xFF475569),

    outline = Color(0xFFE2E8F0),
    outlineVariant = Color(0xFFCBD5E1),

    surfaceTint = Color(0xFF2563EB),
    shadow = Color(0xFF000000),
    scrim = Color(0xFF000000)
)

// Dark theme
val DarkColorScheme = darkColorScheme(
    primary = Color(0xFF3B82F6),
    onPrimary = Color(0xFF0F172A),
    primaryContainer = Color(0xFF1E40AF),
    onPrimaryContainer = Color(0xFFDBEAFE),

    secondary = Color(0xFF94A3B8),
    onSecondary = Color(0xFF0F172A),
    secondaryContainer = Color(0xFF475569),
    onSecondaryContainer = Color(0xFFE2E8F0),

    tertiary = Color(0xFF38BDF8),
    onTertiary = Color(0xFF0F172A),
    tertiaryContainer = Color(0xFF0165A3),
    onTertiaryContainer = Color(0xFFE0F2FE),

    error = Color(0xFFF87171),
    onError = Color(0xFF7F1D1D),
    errorContainer = Color(0xFF7F1D1D),
    onErrorContainer = Color(0xFFFECACA),

    surface = Color(0xFF0F172A),
    onSurface = Color(0xFFF1F5F9),
    surfaceContainerHighest = Color(0xFF1E293B),
    onSurfaceVariant = Color(0xFFCBD5E1),

    outline = Color(0xFF475569),
    outlineVariant = Color(0xFF334155),

    surfaceTint = Color(0xFF3B82F6),
    shadow = Color(0xFF000000),
    scrim = Color(0xFF000000)
)

// Semantic extensions
val ColorScheme.focusRing: Color
    get() = if (brightness > 0.5) Color(0xFF2563EB) else Color(0xFF60A5FA)

val ColorScheme.disabledBg: Color
    get() = if (brightness > 0.5) Color(0xFFF1F5F9) else Color(0xFF1E293B)

val ColorScheme.disabledText: Color
    get() = if (brightness > 0.5) Color(0xFF94A3B8) else Color(0xFF64748B)
```

### Spacing (Dp)
```kotlin
// 4dp base grid (Material uses 4dp, but 8dp rhythm)
val Spacing1 = 4.dp   // 1 × 4dp
val Spacing2 = 8.dp   // 2 × 4dp
val Spacing3 = 12.dp  // 3 × 4dp
val Spacing4 = 16.dp  // 4 × 4dp
val Spacing5 = 20.dp  // 5 × 4dp
val Spacing6 = 24.dp  // 6 × 4dp
val Spacing8 = 32.dp  // 8 × 4dp
val Spacing10 = 40.dp // 10 × 4dp
val Spacing12 = 48.dp // 12 × 4dp
val Spacing16 = 64.dp // 16 × 4dp

// Semantic aliases
val SpaceXS = Spacing1
val SpaceSM = Spacing2
val SpaceMD = Spacing4
val SpaceLG = Spacing6
val SpaceXL = Spacing8
val Space2XL = Spacing12
val Space3XL = Spacing16
```

### Typography (TextStyle)
```kotlin
// Material 3 type scale (modular ~1.25 ratio)
val Typography = Typography(
    displayLarge = TextStyle(
        fontFamily = FontFamily.Default,
        fontWeight = FontWeight.Bold,
        fontSize = 57.sp,
        lineHeight = 64.sp,
        letterSpacing = -0.25.sp
    ),
    displayMedium = TextStyle(
        fontFamily = FontFamily.Default,
        fontWeight = FontWeight.Bold,
        fontSize = 45.sp,
        lineHeight = 52.sp,
        letterSpacing = 0.sp
    ),
    displaySmall = TextStyle(
        fontFamily = FontFamily.Default,
        fontWeight = FontWeight.Bold,
        fontSize = 36.sp,
        lineHeight = 44.sp,
        letterSpacing = 0.sp
    ),
    headlineLarge = TextStyle(
        fontFamily = FontFamily.Default,
        fontWeight = FontWeight.Bold,
        fontSize = 32.sp,
        lineHeight = 40.sp,
        letterSpacing = 0.sp
    ),
    headlineMedium = TextStyle(
        fontFamily = FontFamily.Default,
        fontWeight = FontWeight.Bold,
        fontSize = 28.sp,
        lineHeight = 36.sp,
        letterSpacing = 0.sp
    ),
    headlineSmall = TextStyle(
        fontFamily = FontFamily.Default,
        fontWeight = FontWeight.SemiBold,
        fontSize = 24.sp,
        lineHeight = 32.sp,
        letterSpacing = 0.sp
    ),
    titleLarge = TextStyle(
        fontFamily = FontFamily.Default,
        fontWeight = FontWeight.SemiBold,
        fontSize = 22.sp,
        lineHeight = 28.sp,
        letterSpacing = 0.sp
    ),
    titleMedium = TextStyle(
        fontFamily = FontFamily.Default,
        fontWeight = FontWeight.Medium,
        fontSize = 16.sp,
        lineHeight = 24.sp,
        letterSpacing = 0.15.sp
    ),
    titleSmall = TextStyle(
        fontFamily = FontFamily.Default,
        fontWeight = FontWeight.Medium,
        fontSize = 14.sp,
        lineHeight = 20.sp,
        letterSpacing = 0.1.sp
    ),
    bodyLarge = TextStyle(
        fontFamily = FontFamily.Default,
        fontWeight = FontWeight.Normal,
        fontSize = 16.sp,
        lineHeight = 24.sp,
        letterSpacing = 0.5.sp
    ),
    bodyMedium = TextStyle(
        fontFamily = FontFamily.Default,
        fontWeight = FontWeight.Normal,
        fontSize = 14.sp,
        lineHeight = 20.sp,
        letterSpacing = 0.25.sp
    ),
    bodySmall = TextStyle(
        fontFamily = FontFamily.Default,
        fontWeight = FontWeight.Normal,
        fontSize = 12.sp,
        lineHeight = 16.sp,
        letterSpacing = 0.4.sp
    ),
    labelLarge = TextStyle(
        fontFamily = FontFamily.Default,
        fontWeight = FontWeight.SemiBold,
        fontSize = 14.sp,
        lineHeight = 20.sp,
        letterSpacing = 0.1.sp
    ),
    labelMedium = TextStyle(
        fontFamily = FontFamily.Default,
        fontWeight = FontWeight.Medium,
        fontSize = 12.sp,
        lineHeight = 16.sp,
        letterSpacing = 0.5.sp
    ),
    labelSmall = TextStyle(
        fontFamily = FontFamily.Default,
        fontWeight = FontWeight.Medium,
        fontSize = 11.sp,
        lineHeight = 16.sp,
        letterSpacing = 0.5.sp
    )
)

// Semantic aliases for our token system
val FontSizeXS = 12.sp
val FontSizeSM = 14.sp
val FontSizeMD = 16.sp
val FontSizeLG = 18.sp
val FontSizeXL = 20.sp
val FontSize2XL = 24.sp
val FontSize3XL = 30.sp
val FontSize4XL = 36.sp
val FontSize5XL = 48.sp
```

### Border Radius (CornerRadius)
```kotlin
val RadiusSM = CornerRadius(4.dp)
val RadiusMD = CornerRadius(6.dp)
val RadiusLG = CornerRadius(8.dp)
val RadiusXL = CornerRadius(12.dp)
val RadiusFull = CornerRadius(9999.dp)

val RadiusButton = RadiusMD
val RadiusInput = RadiusMD
val RadiusCard = RadiusLG
val RadiusModal = RadiusXL
val RadiusBadge = RadiusFull
```

### Shadows (Elevation)
```kotlin
// Material elevation levels
val ElevationLevel0 = 0.dp
val ElevationLevel1 = 1.dp   // Cards, sheets
val ElevationLevel2 = 3.dp   // Raised buttons, FAB
val ElevationLevel3 = 6.dp   // Dialogs, bottom sheets
val ElevationLevel4 = 8.dp   // Modal dialogs
val ElevationLevel5 = 12.dp  // Popovers, menus

// Custom shadows (for non-Material)
val ShadowSM = Shadow(0.dp, 1.dp, 2.dp, Color.Black.copy(alpha = 0.05f))
val ShadowMD = Shadow(0.dp, 4.dp, 6.dp, Color.Black.copy(alpha = 0.1f))
val ShadowLG = Shadow(0.dp, 10.dp, 15.dp, Color.Black.copy(alpha = 0.1f))
```

### Breakpoints (WindowSizeClass)
```kotlin
// Material 3 window size classes
enum class WindowWidthSizeClass {
    COMPACT,    // < 600dp (phones)
    MEDIUM,     // 600dp - 840dp (tablets, foldables)
    EXPANDED    // > 840dp (desktop, large tablets)
}

enum class WindowHeightSizeClass {
    COMPACT,    // < 480dp
    MEDIUM,     // 480dp - 900dp
    EXPANDED    // > 900dp
}

// Usage in Compose
val windowSize = calculateWindowSizeClass(LocalConfiguration.current)
when (windowSize.widthSizeClass) {
    WindowWidthSizeClass.COMPACT -> { /* phone layout */ }
    WindowWidthSizeClass.MEDIUM -> { /* tablet layout */ }
    WindowWidthSizeClass.EXPANDED -> { /* desktop layout */ }
}
```

---

## Accessibility Requirements (Android)

### TalkBack / Screen Readers
```kotlin
// Content descriptions
Icon(
    imageVector = Icons.Default.Settings,
    contentDescription = "Settings" // Required for meaningful icons
)

// Decorative images
Icon(
    imageVector = Icons.Default.Decoration,
    contentDescription = null // null = decorative, ignored by TalkBack
)

// Custom actions
Row(
    modifier = Modifier
        .fillMaxWidth()
        .semantics {
            customActions = listOf(
                CustomAction("Delete", { delete(); true }),
                CustomAction("Edit", { edit(); true })
            )
        }
) { ... }

// Live regions (for dynamic content)
Text(
    text = errorMessage,
    modifier = Modifier.semantics { liveRegion = LiveRegionMode.Polite }
)

// Headings
Text(
    text = "Section Title",
    style = MaterialTheme.typography.headlineSmall,
    modifier = Modifier.semantics { heading() }
)
```

### Touch Targets (48×48dp Minimum)
```kotlin
// ALWAYS meet 48dp minimum
IconButton(
    onClick = { },
    modifier = Modifier
        .size(48.dp) // Minimum touch target
) {
    Icon(Icons.Default.Favorite, contentDescription = "Like")
}

// For small clickable content, expand touch area
Text(
    text = "Link",
    modifier = Modifier
        .fillMaxWidth()
        .padding(16.dp) // Expands touch area
        .clickable { }
)

// Minimum touch target enforcement
@Composable
fun MinimumTouchTarget(content: @Composable () -> Unit) {
    Box(
        modifier = Modifier
            .defaultMinSize(minWidth = 48.dp, minHeight = 48.dp)
    ) {
        content()
    }
}
```

### High Contrast / Color Blindness
```kotlin
// Don't rely on color alone
// BAD: Red border only for error
// GOOD: Red border + error icon + error text

// Use Material's built-in contrast handling
// Colors in ColorScheme automatically meet contrast ratios

// Test with "High contrast text" in Settings > Accessibility
```

### Font Scaling (User Font Size)
```kotlin
// Compose respects system font scale automatically when using .sp
Text("Hello", fontSize = 16.sp) // Scales with user preference

// For fixed sizes that shouldn't scale (rare)
Text("Fixed", fontSize = 16.dp) // Doesn't scale — avoid for body text

// Limit maximum scaling
CompositionLocalProvider(LocalFontScaling provides 1.3f) { // Max 130%
    Text("Limited scaling", fontSize = 16.sp)
}
```

### RTL Support
```kotlin
// Use start/end instead of left/right
Modifier.padding(start = 16.dp, end = 16.dp)
Modifier.align(Alignment.Start) // Not Alignment.Left

// Compose handles RTL automatically for most layouts
// Test with "Force RTL layout" in Developer Options
```

---

## Component Mappings

| Web Component | Compose (Material 3) | XML (Material) | Notes |
|---------------|---------------------|----------------|-------|
| `<button>` | `Button`, `ElevatedButton`, `OutlinedButton`, `TextButton` | `MaterialButton` | Variants map to button types |
| `<input>` | `TextField`, `OutlinedTextField` | `TextInputLayout` + `TextInputEditText` | Use `OutlinedTextField` for consistency |
| `<select>` | `Menu` + `DropdownMenu` / `ExposedDropdownMenuBox` | `AutoCompleteTextView` / `Spinner` | No native select; use menu |
| `<dialog>` | `Dialog`, `AlertDialog` | `MaterialAlertDialogBuilder` | Use `Dialog` for custom |
| `<nav>` | `NavigationBar`, `NavigationDrawer` | `BottomNavigationView`, `NavigationView` | Use `NavigationBar` for bottom nav |
| `<aside>` | `NavigationDrawer` / `PermanentNavigationDrawer` | `DrawerLayout` | |
| `<table>` | `LazyColumn` / `LazyRow` (no native table) | `RecyclerView` | Compose: lists not tables |
| `<form>` | No direct equivalent — compose `Column` + validation | No direct equivalent | Use `Form` pattern manually |
| Toast | `Toast` (system) / `Snackbar` (Material) | `Toast` / `Snackbar` | `Snackbar` preferred for actions |
| Tooltip | `Tooltip` (Compose 1.6+) | `TooltipCompat` | Use `TooltipBox` in Compose |

---

## Material 3 Component Usage

### Buttons
```kotlin
// Primary (filled)
Button(onClick = { }) {
    Text("Primary", style = MaterialTheme.typography.labelLarge)
}

// Secondary (outlined)
OutlinedButton(onClick = { }) {
    Text("Secondary", style = MaterialTheme.typography.labelLarge)
}

// Tertiary (text)
TextButton(onClick = { }) {
    Text("Tertiary", style = MaterialTheme.typography.labelLarge)
}

// Danger
Button(
    onClick = { },
    colors = ButtonDefaults.buttonColors(
        containerColor = MaterialTheme.colorScheme.error,
        contentColor = MaterialTheme.colorScheme.onError
    )
) {
    Text("Delete", style = MaterialTheme.typography.labelLarge)
}
```

### Text Fields
```kotlin
OutlinedTextField(
    value = text,
    onValueChange = { text = it },
    label = { Text("Email") },
    placeholder = { Text("you@example.com") },
    leadingIcon = { Icon(Icons.Default.Email, contentDescription = null) },
    trailingIcon = {
        if (error) Icon(Icons.Default.Error, contentDescription = "Error")
        else null
    },
    isError = error,
    supportingText = { if (error) Text("Invalid email") else Text("We'll never share your email") },
    singleLine = true,
    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Email),
    keyboardActions = KeyboardActions(onDone = { /* submit */ })
)
```

### Cards
```kotlin
// Elevated card
Card(
    elevation = CardDefaults.cardElevation(defaultElevation = 3.dp),
    colors = CardDefaults.cardColors(
        containerColor = MaterialTheme.colorScheme.surface
    ),
    shape = RoundedCornerShape(RadiusCard)
) {
    Column(modifier = Modifier.padding(SpaceMD)) {
        Text("Title", style = MaterialTheme.typography.titleMedium)
        Text("Description", style = MaterialTheme.typography.bodyMedium)
    }
}

// Outlined card
Card(
    elevation = CardDefaults.cardElevation(defaultElevation = 0.dp),
    colors = CardDefaults.cardColors(
        containerColor = MaterialTheme.colorScheme.surface,
        contentColor = MaterialTheme.colorScheme.onSurface
    ),
    shape = RoundedCornerShape(RadiusCard),
    border = BorderStroke(1.dp, MaterialTheme.colorScheme.outline)
) { ... }
```

---

## Platform-Specific Tokens

### Android-Specific Additions
```kotlin
// Material system colors (already in ColorScheme)
val ColorScheme.surfaceDim = Color(0xFFDEDDE0) // Light
val ColorScheme.surfaceDim = Color(0xFF1C1B1F) // Dark

// Standard dimensions (Material guidelines)
val NavBarHeight = 48.dp
val AppBarHeight = 64.dp
val BottomSheetPeekHeight = 56.dp
val TouchTargetSize = 48.dp
val StandardMargin = 16.dp
val ContentPadding = 16.dp

// Animation durations
val AnimFast = 100
val AnimMedium = 200
val AnimSlow = 300
```

---

## Testing Checklist (Android)

- [ ] TalkBack navigation works (swipe order, gestures)
- [ ] All text scales with system font size (test 85%-200%)
- [ ] Touch targets ≥48×48dp
- [ ] High contrast mode works
- [ ] Dark theme: all colors adapt correctly
- [ ] RTL: Arabic/Hebrew/Farsi layouts work
- [ ] Landscape orientation works
- [ ] Foldable/dual-screen layouts work
- [ ] Window size classes: COMPACT/MEDIUM/EXPANDED
- [ ] Keyboard navigation (Tab, Enter, Escape, arrows)
- [ ] Screen magnification (triple-tap zoom)

---

## XML Layouts (Legacy / Migration)

```xml
<!-- Button -->
<com.google.android.material.button.MaterialButton
    style="@style/Widget.Material3.Button"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:text="Primary" />

<!-- Outlined button -->
<com.google.android.material.button.MaterialButton
    style="@style/Widget.Material3.Button.OutlinedButton"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:text="Secondary" />

<!-- Text field -->
<com.google.android.material.textfield.TextInputLayout
    style="@style/Widget.Material3.TextInputLayout.OutlinedBox"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:hint="Email">

    <com.google.android.material.textfield.TextInputEditText
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:inputType="textEmailAddress" />
</com.google.android.material.textfield.TextInputLayout>

<!-- Card -->
<com.google.android.material.card.MaterialCardView
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    app:cardElevation="3dp"
    app:strokeWidth="0dp"
    app:cardCornerRadius="8dp">

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="vertical"
        android:padding="16dp">
        ...
    </LinearLayout>
</com.google.android.material.card.MaterialCardView>
```

---

## Handoff from Web Design

| Web Token | Android Token | Conversion |
|-----------|---------------|------------|
| `--color-primary` | `ColorScheme.primary` | Direct hex → ARGB |
| `--space-4` | `Spacing4` (16dp) | 16px = 16dp (mdpi baseline) |
| `--font-size-md` | `Typography.bodyLarge` (16sp) | 16px = 16sp (scales!) |
| `--radius-md` | `RadiusMD` (6dp) | 6px = 6dp |
| `--shadow-md` | `ElevationLevel1` (1dp) + `ElevationLevel2` (3dp) | Different paradigm |
| `clamp()` fluid type | System font scaling | Different paradigm — use `.sp` |
| `@media (min-width: 768px)` | `WindowWidthSizeClass.MEDIUM` | Size classes, not breakpoints |

**Key difference**: Android uses **Window Size Classes** (COMPACT/MEDIUM/EXPANDED) and **system font scaling** instead of CSS breakpoints and fluid type. Design for *size classes*, not fixed viewports.