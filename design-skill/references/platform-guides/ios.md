# iOS / SwiftUI Platform Guide

**Design token mappings, accessibility requirements, and component patterns for iOS.** All tokens reference the canonical system in `token-reference.md`.

---

## Design Token Mapping

### Colors (UIColor / Color)
```swift
// Light mode (default)
extension Color {
    static let primary = Color(hex: "2563EB")
    static let primaryHover = Color(hex: "1D4ED8")  // pressed
    static let primaryActive = Color(hex: "1E40AF")
    static let primaryDisabled = Color(hex: "93C5FD")

    static let secondary = Color(hex: "64748B")
    static let secondaryHover = Color(hex: "475569")

    static let surface = Color(hex: "FFFFFF")
    static let surfaceHover = Color(hex: "F8FAFC")
    static let surfaceElevated = Color(hex: "FFFFFF")

    static let border = Color(hex: "E2E8F0")
    static let borderStrong = Color(hex: "CBD5E1")

    static let focusRing = Color(hex: "2563EB")

    static let textPrimary = Color(hex: "0F172A")
    static let textSecondary = Color(hex: "475569")
    static let textMuted = Color(hex: "94A3B8")
    static let textInverse = Color(hex: "F8FAFC")

    static let error = Color(hex: "DC2626")
    static let errorLight = Color(hex: "FEF2F2")
    static let errorText = Color(hex: "B91C1C")

    static let success = Color(hex: "16A34A")
    static let successLight = Color(hex: "F0FDF4")
    static let successText = Color(hex: "15803D")

    static let warning = Color(hex: "CA8A04")
    static let warningLight = Color(hex: "FEFCE8")
    static let warningText = Color(hex: "A16207")
}

// Dark mode
extension Color {
    static let primaryDark = Color(hex: "3B82F6")
    static let primaryHoverDark = Color(hex: "60A5FA")
    static let surfaceDark = Color(hex: "0F172A")
    static let surfaceHoverDark = Color(hex: "1E293B")
    static let borderDark = Color(hex: "334155")
    static let textPrimaryDark = Color(hex: "F1F5F9")
    // ... etc for all colors
}

// Semantic colors (auto-adapt)
extension Color {
    static let adaptivePrimary = Color("Primary") // from Asset Catalog
    static let adaptiveSurface = Color("Surface")
    static let adaptiveTextPrimary = Color("TextPrimary")
}
```

### Spacing (CGFloat / Spacing)
```swift
extension CGFloat {
    static let space1: CGFloat = 4
    static let space2: CGFloat = 8
    static let space3: CGFloat = 12
    static let space4: CGFloat = 16
    static let space5: CGFloat = 20
    static let space6: CGFloat = 24
    static let space8: CGFloat = 32
    static let space10: CGFloat = 40
    static let space12: CGFloat = 48
    static let space16: CGFloat = 64
}

// Semantic aliases
extension CGFloat {
    static let spaceXS = CGFloat.space1
    static let spaceSM = CGFloat.space2
    static let spaceMD = CGFloat.space4
    static let spaceLG = CGFloat.space6
    static let spaceXL = CGFloat.space8
    static let space2XL = CGFloat.space12
    static let space3XL = CGFloat.space16
}
```

### Typography (Font)
```swift
extension Font {
    // System fonts with modular scale
    static let heading1 = Font.system(size: 48, weight: .bold, design: .default)      // 5xl
    static let heading2 = Font.system(size: 36, weight: .bold, design: .default)      // 4xl
    static let heading3 = Font.system(size: 30, weight: .semibold, design: .default)  // 3xl
    static let heading4 = Font.system(size: 24, weight: .semibold, design: .default)  // 2xl
    static let heading5 = Font.system(size: 20, weight: .medium, design: .default)    // xl
    static let heading6 = Font.system(size: 18, weight: .medium, design: .default)    // lg

    static let body = Font.system(size: 16, weight: .regular, design: .default)       // md
    static let bodySM = Font.system(size: 14, weight: .regular, design: .default)     // sm
    static let caption = Font.system(size: 12, weight: .regular, design: .default)    // xs
    static let overline = Font.system(size: 10, weight: .medium, design: .default)

    // Dynamic Type support (respects user text size)
    static let bodyDynamic = Font.body
    static let captionDynamic = Font.caption
    static let footnoteDynamic = Font.footnote
}
```

### Border Radius
```swift
extension CGFloat {
    static let radiusSM: CGFloat = 4
    static let radiusMD: CGFloat = 6
    static let radiusLG: CGFloat = 8
    static let radiusXL: CGFloat = 12
    static let radiusFull: CGFloat = 9999

    static let radiusButton = CGFloat.radiusMD
    static let radiusInput = CGFloat.radiusMD
    static let radiusCard = CGFloat.radiusLG
    static let radiusModal = CGFloat.radiusXL
}
```

### Shadows
```swift
extension Shadow {
    static let sm = Shadow(color: .black.opacity(0.05), radius: 2, x: 0, y: 1)
    static let md = Shadow(color: .black.opacity(0.1), radius: 6, x: 0, y: 4)
    static let lg = Shadow(color: .black.opacity(0.1), radius: 15, x: 0, y: 10)
    static let card = Shadow.md
    static let modal = Shadow.lg
}
```

---

## Accessibility Requirements (iOS)

### VoiceOver
```swift
// Labels
Button("Submit") { }
    .accessibilityLabel("Submit form")
    .accessibilityHint("Submits your registration data")

// Traits
Text("Error: Invalid email")
    .accessibilityAddTraits(.isHeader) // or .updatesFrequently

// Grouping
VStack {
    Text("Username")
    TextField("", text: $username)
}
    .accessibilityElement(children: .combine)
    .accessibilityLabel("Username field")

// Custom actions
List {
    ForEach(items) { item in
        Row(item)
            .accessibilityAction(named: "Delete") { delete(item) }
            .accessibilityAction(named: "Edit") { edit(item) }
    }
}
```

### Dynamic Type (Required)
```swift
// ALL text must support Dynamic Type
Text("Hello")
    .font(.body) // Not .system(size: 16) — uses user's preferred size

// For custom fonts
Text("Hello")
    .font(.custom("SF Pro", size: 17, relativeTo: .body)) // scales with Dynamic Type

// Limit scaling for headlines
Text("Title")
    .font(.title)
    .minimumScaleFactor(0.8) // Don't shrink below 80%
```

### Touch Targets (44×44pt Minimum)
```swift
// ALWAYS meet 44pt minimum
Button(action: { }) {
    Image(systemName: "gear")
        .frame(width: 44, height: 44) // Hit area
        .contentShape(Rectangle()) // Expand touch area
}

// For small icons, add padding
Button(action: { }) {
    Image(systemName: "star")
        .padding(12) // 24pt icon + 24pt padding = 48pt
}
```

### Reduce Motion
```swift
@Environment(\.accessibilityReduceMotion) var reduceMotion

// Respect in animations
withAnimation(reduceMotion ? .none : .spring()) {
    // animation
}

// Or disable entirely
if !reduceMotion {
    withAnimation(.spring()) { ... }
}
```

### Increase Contrast
```swift
@Environment(\.accessibilityDifferentiateWithoutColor) var differentiateWithoutColor

// Don't rely on color alone for state
if differentiateWithoutColor {
    // Add icons/patterns alongside colors
}
```

---

## Component Mappings

| Web Component | SwiftUI Equivalent | Notes |
|---------------|-------------------|-------|
| `<button>` | `Button` | Use `.buttonStyle(.borderedProminent)` for primary |
| `<input>` | `TextField` / `SecureField` | Use `.textFieldStyle(.roundedBorder)` |
| `<select>` | `Picker` / `Menu` | `Picker` for few options, `Menu` for many |
| `<dialog>` | `.sheet()` / `.fullScreenCover()` | Sheets for modals |
| `<nav>` | `NavigationStack` + `NavigationLink` | iOS 16+ |
| `<aside>` | `NavigationSplitView` sidebar | iPad/macOS |
| `<table>` | `List` / `Table` (macOS) | `List` for iOS |
| `<form>` | `Form` | Groups controls, adds styling |
| Toast | Custom overlay + `.toast` modifier | No native toast |
| Tooltip | `.popover` / `.help` | macOS: `.help` |

---

## Safe Area Handling

```swift
// Respect safe areas (notches, home indicator)
VStack {
    Content()
}
.ignoresSafeArea(edges: .bottom) // Only when intentional

// For full-screen backgrounds
Color.primary
    .ignoresSafeArea()

// Container with safe area padding
VStack {
    Content()
}
.padding(.top, 0) // Let system handle top
.safeAreaInset(edge: .bottom) {
    BottomBar() // Above home indicator
}
```

### Safe Area Insets (Programmatic)
```swift
GeometryReader { geometry in
    let safeArea = geometry.safeAreaInsets
    // safeArea.top, .bottom, .leading, .trailing
    Content()
        .padding(.bottom, safeArea.bottom)
}
```

---

## Platform-Specific Tokens

### iOS-Specific Additions
```swift
extension Color {
    // System colors (auto-adapt)
    static let systemBackground = Color(.systemBackground)
    static let secondarySystemBackground = Color(.secondarySystemBackground)
    static let tertiarySystemBackground = Color(.tertiarySystemBackground)

    static let systemGroupedBackground = Color(.systemGroupedBackground)
    static let secondarySystemGroupedBackground = Color(.secondarySystemGroupedBackground)

    static let label = Color(.label)
    static let secondaryLabel = Color(.secondaryLabel)
    static let tertiaryLabel = Color(.tertiaryLabel)
    static let quaternaryLabel = Color(.quaternaryLabel)

    static let separator = Color(.separator)
    static let opaqueSeparator = Color(.opaqueSeparator)

    static let systemBlue = Color(.systemBlue)
    static let systemGreen = Color(.systemGreen)
    static let systemRed = Color(.systemRed)
    static let systemOrange = Color(.systemOrange)
    static let systemYellow = Color(.systemYellow)
}
```

### Spacing for iOS
```swift
// iOS standard spacings (Human Interface Guidelines)
extension CGFloat {
    static let iOSMargin: CGFloat = 16      // Standard screen edge margin
    static let iOSItemSpacing: CGFloat = 8  // Between list items
    static let iOSSectionSpacing: CGFloat = 24 // Between sections
    static let iOSButtonHeight: CGFloat = 44 // Minimum touch target
    static let iOSBarHeight: CGFloat = 44   // Navigation/tool bar
    static let iOSTabBarHeight: CGFloat = 49 // Tab bar
}
```

---

## Testing Checklist (iOS)

- [ ] VoiceOver navigation works (swipe order logical)
- [ ] All text scales with Dynamic Type (test 5 sizes)
- [ ] Touch targets ≥44×44pt
- [ ] Reduce Motion respected
- [ ] Increase Contrast works
- [ ] Dark mode: all colors adapt correctly
- [ ] Safe areas respected (notch, home indicator)
- [ ] RTL: Arabic/Hebrew layouts work
- [ ] Landscape orientation works
- [ ] iPad split view / slide over works
- [ ] Keyboard navigation (tab order, Escape dismisses)

---

## Asset Catalog Setup

1. Create `Colors.xcassets` with color sets for each semantic token
2. Enable "Appearances: Any, Dark" for each color
3. Set light/dark values from token reference
4. Reference in code: `Color("Primary")`, `Color("Surface")`

---

## SwiftUI View Modifiers for Consistency

```swift
// Consistent button styling
struct PrimaryButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .font(.body.weight(.medium))
            .foregroundColor(.textInverse)
            .padding(.horizontal, .space4)
            .padding(.vertical, .space2)
            .background(configuration.isPressed ? Color.primaryActive : Color.primary)
            .cornerRadius(.radiusButton)
            .scaleEffect(configuration.isPressed ? 0.98 : 1)
            .animation(.easeOut(duration: 0.1), value: configuration.isPressed)
    }
}

// Consistent card styling
struct CardModifier: ViewModifier {
    func body(content: Content) -> some View {
        content
            .background(Color.surface)
            .cornerRadius(.radiusCard)
            .shadow(Shadow.card)
    }
}

// Consistent input styling
struct InputStyle: ViewModifier {
    @FocusState var isFocused: Bool
    func body(content: Content) -> some View {
        content
            .padding(.horizontal, .space3)
            .padding(.vertical, .space2)
            .background(Color.surface)
            .cornerRadius(.radiusInput)
            .overlay(
                RoundedRectangle(cornerRadius: .radiusInput)
                    .stroke(isFocused ? Color.focusRing : Color.border, lineWidth: isFocused ? 2 : 1)
            )
            .focused($isFocused)
    }
}
```

---

## Handoff from Web Design

| Web Token | iOS Token | Conversion |
|-----------|-----------|------------|
| `--color-primary` | `Color.primary` | Direct hex |
| `--space-4` | `.space4` | 16pt = 16px |
| `--font-size-md` | `.body` | 16pt = 16px (but Dynamic Type!) |
| `--radius-md` | `.radiusMD` | 6pt = 6px |
| `--shadow-md` | `Shadow.md` | Convert to Shadow struct |
| `clamp()` fluid type | Dynamic Type | Different paradigm — use system fonts |
| `@media (min-width: 768px)` | Size classes / GeometryReader | Horizontal: Regular/Compact, Vertical: Regular/Compact |

**Key difference**: iOS uses **Dynamic Type** and **Size Classes** instead of fluid CSS and breakpoints. Design for the *system*, not fixed viewports.