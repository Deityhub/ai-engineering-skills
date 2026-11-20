# Component Patterns — Atomic Design Reference

**Component primitives and composition rules.** Use tokens from `token-reference.md`. All components follow: presentational (UI only) + container (logic/data) separation.

---

## Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Component | PascalCase | `PrimaryButton`, `FormField` |
| Props | camelCase | `variant`, `size`, `isDisabled` |
| CSS classes | kebab-case | `.primary-button`, `.form-field__input` |
| Tokens | CSS custom properties | `var(--color-primary)` |
| Files | PascalCase.tsx / kebab-case.css | `PrimaryButton.tsx`, `primary-button.css` |

---

## Props Standard (All Components)

```typescript
// Base props every component should support
interface BaseProps {
  /** Visual variant */
  variant?: 'primary' | 'secondary' | 'tertiary' | 'ghost' | 'danger';
  /** Size variant */
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  /** Disabled state */
  disabled?: boolean;
  /** Loading state */
  loading?: boolean;
  /** Additional CSS classes */
  className?: string;
  /** Test ID for automation */
  data-testid?: string;
}
```

---

## Atoms (Primitives) — Indivisible

### Button
```tsx
// Variants: primary | secondary | tertiary | ghost | danger
// Sizes: xs | sm | md | lg | xl
interface ButtonProps extends BaseProps {
  variant?: 'primary' | 'secondary' | 'tertiary' | 'ghost' | 'danger';
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  /** HTML button type */
  type?: 'button' | 'submit' | 'reset';
  /** Icon only (requires aria-label) */
  iconOnly?: boolean;
  /** Left icon */
  startIcon?: React.ReactNode;
  /** Right icon */
  endIcon?: React.ReactNode;
  /** Full width */
  fullWidth?: boolean;
  onClick?: (e: React.MouseEvent<HTMLButtonElement>) => void;
}

// Token usage:
// - Background: var(--color-primary), var(--color-primary-hover), var(--color-primary-active)
// - Text: var(--color-text-inverse)
// - Border: var(--color-border) for ghost/secondary
// - Focus: var(--color-focus-ring)
// - Disabled: var(--color-primary-disabled), var(--color-disabled-text)
// - Padding: var(--space-2) var(--space-4) (sm), var(--space-3) var(--space-6) (md)
// - Radius: var(--radius-button)
// - Font: var(--font-size-sm), var(--font-weight-medium)
```

### Input
```tsx
interface InputProps extends BaseProps {
  /** Input type */
  type?: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url' | 'search';
  /** Associated label text */
  label: string;
  /** Helper text */
  helperText?: string;
  /** Error message (triggers error state) */
  error?: string;
  /** Placeholder (not a label replacement) */
  placeholder?: string;
  /** Value (controlled) */
  value?: string;
  /** Default value (uncontrolled) */
  defaultValue?: string;
  onChange?: (value: string, e: React.ChangeEvent<HTMLInputElement>) => void;
  onBlur?: (e: React.FocusEvent<HTMLInputElement>) => void;
  /** Left adornment (icon, prefix) */
  startAdornment?: React.ReactNode;
  /** Right adornment (icon, suffix) */
  endAdornment?: React.ReactNode;
  /** Auto-complete hint */
  autoComplete?: string;
  /** Input mode for mobile keyboards */
  inputMode?: 'text' | 'email' | 'numeric' | 'tel' | 'search';
}

// Token usage:
// - Border: var(--color-border), var(--color-border-focus), var(--color-error-border)
// - Background: var(--color-surface), var(--color-disabled-bg)
// - Text: var(--color-text-primary), var(--color-disabled-text)
// - Placeholder: var(--color-text-muted)
// - Label: var(--font-size-sm), var(--font-weight-medium), var(--color-text-secondary)
// - Helper/Error: var(--font-size-xs), var(--color-text-secondary/error-text)
// - Padding: var(--space-2) var(--space-3)
// - Radius: var(--radius-input)
// - Focus ring: var(--color-focus-ring)
// - Transition: var(--transition-fast)
```

### Badge
```tsx
interface BadgeProps extends BaseProps {
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'error' | 'info';
  size?: 'sm' | 'md' | 'lg';
  /** Dot indicator instead of text */
  dot?: boolean;
  /** Removable */
  onClose?: () => void;
}

// Token usage:
// - Background: var(--color-primary-light), var(--color-success-light), etc.
// - Text: var(--color-primary-text), var(--color-success-text), etc.
// - Border: var(--color-primary-border) for outline variant
// - Padding: var(--space-1) var(--space-2) (sm), var(--space-1) var(--space-3) (md)
// - Radius: var(--radius-badge)
// - Font: var(--font-size-xs), var(--font-weight-semibold)
```

### Avatar
```tsx
interface AvatarProps extends BaseProps {
  /** Image source */
  src?: string;
  /** Fallback text (initials) */
  alt?: string;
  /** Fallback background color (deterministic from name) */
  fallbackColor?: string;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl';
  /** Shape */
  shape?: 'circle' | 'square';
  /** Status indicator */
  status?: 'online' | 'offline' | 'busy' | 'away';
}

// Token usage:
// - Size: var(--space-8) (xs) through var(--space-24) (2xl)
// - Border: var(--color-surface) for ring
// - Fallback bg: deterministic from name hash
// - Status: var(--color-success), var(--color-warning), var(--color-text-muted)
// - Status position: absolute, bottom-right, border var(--color-surface)
```

### Icon
```tsx
interface IconProps extends BaseProps {
  /** Icon name (from icon library) */
  name: string;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  /** Decorative (aria-hidden=true) */
  decorative?: boolean;
  /** ARIA label (required if not decorative) */
  'aria-label'?: string;
}

// Token usage:
// - Size: var(--space-4) (sm) through var(--space-8) (xl) — width/height
// - Color: currentColor (inherits text color)
// - Decorative: aria-hidden="true"
// - Non-decorative: requires aria-label on parent or wrapper
```

### Typography
```tsx
interface TypographyProps extends BaseProps {
  /** HTML element */
  as?: 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6' | 'p' | 'span' | 'label' | 'small';
  /** Visual variant (overrides as for styling) */
  variant?: 'heading-1' | 'heading-2' | 'heading-3' | 'heading-4' | 'heading-5' | 'heading-6' | 'body' | 'body-sm' | 'caption' | 'overline';
  /** Font weight */
  weight?: 'normal' | 'medium' | 'semibold' | 'bold';
  /** Text alignment */
  align?: 'left' | 'center' | 'right' | 'justify';
  /** Color variant */
  color?: 'primary' | 'secondary' | 'muted' | 'inverse' | 'error' | 'success' | 'warning' | 'link';
  /** Truncate with ellipsis */
  truncate?: boolean;
  /** Max lines (requires truncate) */
  maxLines?: number;
}

// Token usage:
// - Font size: var(--font-size-heading-1) through var(--font-size-caption)
// - Weight: var(--font-weight-normal) through var(--font-weight-bold)
// - Line height: var(--line-height-tight) for headings, var(--line-height-normal) for body
// - Color: var(--color-text-primary), var(--color-text-secondary), var(--color-text-muted), etc.
// - Letter spacing: var(--letter-spacing-tight) for headings
```

### Spacer
```tsx
interface SpacerProps {
  /** Space token */
  space?: keyof SpacingTokens; // '1' | '2' | '3' | '4' | '5' | '6' | '8' | '10' | '12' | '16'
  /** Direction */
  direction?: 'vertical' | 'horizontal';
  /** Responsive overrides */
  responsive?: Partial<Record<Breakpoint, keyof SpacingTokens>>;
}

// Usage: <Spacer space="4" /> → margin-bottom: var(--space-4)
// Responsive: <Spacer space="4" responsive={{ md: '6', lg: '8' }} />
```

---

## Molecules (Composites) — Simple Compositions

### FormField (Label + Input + Error + Helper)
```tsx
interface FormFieldProps {
  /** Label text */
  label: string;
  /** Input props (spread) */
  inputProps: InputProps;
  /** Field name (for form libraries) */
  name?: string;
  /** Required indicator */
  required?: boolean;
  /** Custom error message override */
  errorMessage?: string;
}

// Composition:
// <label>
//   <Typography as="label" variant="body-sm" weight="medium">{label}</Typography>
//   {required && <span aria-hidden="true">*</span>}
//   <Input {...inputProps} />
//   {error && <Typography variant="caption" color="error" role="alert">{error}</Typography>}
//   {helperText && <Typography variant="caption" color="muted">{helperText}</Typography>}
// </label>
```

### Card
```tsx
interface CardProps extends BaseProps {
  /** Card variant */
  variant?: 'default' | 'outlined' | 'elevated' | 'filled';
  /** Padding */
  padding?: 'none' | 'sm' | 'md' | 'lg';
  /** Hoverable */
  hoverable?: boolean;
  /** Clickable (renders as button) */
  onClick?: () => void;
  /** Header content */
  header?: React.ReactNode;
  /** Footer content */
  footer?: React.ReactNode;
  children: React.ReactNode;
}

// Token usage:
// - Background: var(--color-surface), var(--color-surface-hover), var(--color-surface-elevated)
// - Border: var(--color-border), var(--color-border-strong)
// - Shadow: var(--shadow-card), var(--shadow-md) for elevated
// - Radius: var(--radius-card)
// - Padding: var(--space-4) (md), var(--space-6) (lg)
```

### Dropdown / Select
```tsx
interface SelectProps extends BaseProps {
  /** Options */
  options: Array<{ value: string; label: string; disabled?: boolean }>;
  /** Placeholder */
  placeholder?: string;
  /** Value (controlled) */
  value?: string;
  onChange?: (value: string) => void;
  /** Searchable */
  searchable?: boolean;
  /** Multiple */
  multiple?: boolean;
  /** Error state */
  error?: boolean;
}

// Composition: Label + Trigger (Button) + Popover (Listbox) + Options
// Keyboard: Arrow keys, Enter, Escape, Type-ahead
// ARIA: combobox, listbox, option roles
```

### Toast / Notification
```tsx
interface ToastProps extends BaseProps {
  variant?: 'default' | 'success' | 'error' | 'warning' | 'info';
  /** Title */
  title: string;
  /** Description */
  description?: string;
  /** Action button */
  action?: { label: string; onClick: () => void };
  /** Auto-dismiss duration (ms) */
  duration?: number;
  /** Persistent (no auto-dismiss) */
  persistent?: boolean;
  onClose?: () => void;
}

// Token usage:
// - Background: var(--color-surface-elevated)
// - Border: var(--color-border) + variant color accent bar
// - Icon: variant color
// - Shadow: var(--shadow-toast)
// - Animation: slide-in + fade, respects prefers-reduced-motion
```

### Modal / Dialog
```tsx
interface ModalProps extends BaseProps {
  /** Open state */
  open: boolean;
  onClose: () => void;
  /** Title */
  title: string;
  /** Description (for aria-describedby) */
  description?: string;
  /** Size */
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  /** Close on overlay click */
  closeOnOverlayClick?: boolean;
  /** Close on Escape */
  closeOnEscape?: boolean;
  /** Footer actions */
  footer?: React.ReactNode;
  children: React.ReactNode;
}

// Token usage:
// - Overlay: var(--color-surface-overlay)
// - Container: var(--color-surface), var(--radius-modal), var(--shadow-modal)
// - Focus trap: required
// - ARIA: role="dialog", aria-modal="true", aria-labelledby, aria-describedby
// - Animation: fade + scale, respects prefers-reduced-motion
```

---

## Organisms — Complex Sections

### Header
```tsx
interface HeaderProps {
  /** Logo */
  logo: React.ReactNode;
  /** Navigation items */
  navigation: Array<{ label: string; href: string; children?: NavigationItem[] }>;
  /** Actions (auth, settings) */
  actions?: React.ReactNode;
  /** Sticky */
  sticky?: boolean;
  /** Mobile menu breakpoint */
  mobileBreakpoint?: 'sm' | 'md' | 'lg';
}

// Composition: Logo + Navigation (desktop) + MobileMenuButton + Drawer (mobile) + Actions
// ARIA: <header>, <nav>, aria-label="Main navigation"
// Responsive: Hamburger at mobileBreakpoint, drawer with focus trap
```

### DataTable
```tsx
interface DataTableProps<T> {
  /** Column definitions */
  columns: Array<{
    key: string;
    header: string;
    render?: (row: T) => React.ReactNode;
    sortable?: boolean;
    width?: string;
    align?: 'left' | 'center' | 'right';
  }>;
  /** Data rows */
  data: T[];
  /** Sort state */
  sort?: { key: string; direction: 'asc' | 'desc' };
  onSort?: (key: string, direction: 'asc' | 'desc') => void;
  /** Selection */
  selection?: string[];
  onSelectionChange?: (keys: string[]) => void;
  /** Pagination */
  pagination?: { page: number; pageSize: number; total: number };
  onPaginationChange?: (page: number, pageSize: number) => void;
  /** Loading state */
  loading?: boolean;
  /** Empty state */
  emptyMessage?: string;
  /** Row key */
  rowKey: keyof T | ((row: T) => string);
}

// Composition: Toolbar + Table + Pagination
// Keyboard: Arrow keys for row nav, Space for selection, Enter for action
// ARIA: role="grid", columnheader, rowheader, gridcell
// Responsive: Horizontal scroll on mobile, column hiding
```

### SearchResults
```tsx
interface SearchResultsProps<T> {
  /** Query */
  query: string;
  /** Results */
  results: T[];
  /** Render result item */
  renderResult: (item: T, highlight: string) => React.ReactNode;
  /** Loading */
  loading?: boolean;
  /** Total count */
  total?: number;
  /** Pagination */
  page?: number;
  onPageChange?: (page: number) => void;
  /** Empty state */
  emptyMessage?: string;
}

// Composition: Query display + Results list + Pagination + Facets (optional)
// Highlight: mark matching text with <mark> (styled with var(--color-primary-light))
```

---

## Templates / Pages — Layout Compositions

### Page Layout
```tsx
interface PageLayoutProps {
  /** Header */
  header?: React.ReactNode;
  /** Sidebar */
  sidebar?: React.ReactNode;
  /** Main content */
  children: React.ReactNode;
  /** Footer */
  footer?: React.ReactNode;
  /** Container max width */
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  /** Padding */
  padding?: 'none' | 'sm' | 'md' | 'lg';
}

// Structure:
// <div class="page-layout">
//   <a href="#main" class="skip-link">Skip to main content</a>
//   <header role="banner">{header}</header>
//   <div class="page-layout__body">
//     {sidebar && <aside role="complementary">{sidebar}</aside>}
//     <main id="main" role="main" class="page-layout__main">{children}</main>
//   </div>
//   <footer role="contentinfo">{footer}</footer>
// </div>
```

---

## Platform Mappings

| Web (HTML/CSS) | React | Vue | SwiftUI | Flutter | React Native |
|----------------|-------|-----|---------|---------|--------------|
| `<button>` | `<Button>` | `<Button>` | `Button` | `ElevatedButton` | `<Pressable>` |
| `<input>` | `<Input>` | `<Input>` | `TextField` | `TextField` | `<TextInput>` |
| `<select>` | `<Select>` | `<Select>` | `Picker` | `DropdownButton` | `<Picker>` |
| `<dialog>` | `<Modal>` | `<Modal>` | `.sheet()` | `showDialog` | `<Modal>` |
| `<table>` | `<DataTable>` | `<DataTable>` | `Table`/`List` | `DataTable` | `<FlatList>` |
| `<nav>` | `<Navigation>` | `<Navigation>` | `NavigationStack` | `NavigationBar` | `<NavigationContainer>` |
| `<aside>` | `<Sidebar>` | `<Sidebar>` | `Sidebar` | `Drawer` | `<Drawer>` |

See `references/platform-guides/` for detailed mappings.

---

## Component Specification Template

Use `assets/templates/component-spec.md` for documenting new components:

```markdown
# Component: [Name]

## Purpose
[What problem does this solve?]

## Props API
| Prop | Type | Default | Description |
|------|------|---------|-------------|

## Variants
| Variant | Description | Token Overrides |
|---------|-------------|-----------------|

## States
| State | Description | Token Overrides |
|-------|-------------|-----------------|

## Accessibility
- [ ] Keyboard navigation
- [ ] Focus management
- [ ] ARIA attributes
- [ ] Screen reader testing

## Responsive Behavior
| Breakpoint | Behavior |
|------------|----------|

## Platform Implementations
- [ ] Web (HTML/CSS)
- [ ] React
- [ ] Vue
- [ ] SwiftUI
- [ ] Flutter
- [ ] React Native

## Tests
- [ ] Unit tests
- [ ] Visual regression
- [ ] Accessibility audit
- [ ] Token compliance
```