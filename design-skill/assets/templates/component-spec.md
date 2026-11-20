# Component Specification: [ComponentName]

## Overview
**Name**: [ComponentName]
**Category**: [Atom | Molecule | Organism]
**Status**: [Draft | Review | Approved | Deprecated]
**Owner**: [Designer/Developer]
**Last Updated**: [YYYY-MM-DD]

## Purpose
[One paragraph describing what this component does and when to use it.]

## Design Tokens Used
| Token Category | Tokens |
|----------------|--------|
| Spacing | `--space-2`, `--space-4`, `--space-6` |
| Color | `--color-primary`, `--color-primary-hover`, `--color-text-inverse`, `--color-focus-ring` |
| Typography | `--font-size-sm`, `--font-weight-medium`, `--line-height-normal` |
| Border Radius | `--radius-button` |
| Shadow | `--shadow-sm` |
| Transitions | `--transition-fast` |

## Props API
| Prop | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| variant | `'primary' \| 'secondary' \| 'tertiary' \| 'ghost' \| 'danger'` | `'primary'` | No | Visual style variant |
| size | `'xs' \| 'sm' \| 'md' \| 'lg' \| 'xl'` | `'md'` | No | Size variant |
| disabled | `boolean` | `false` | No | Disables interaction |
| loading | `boolean` | `false` | No | Shows loading spinner |
| className | `string` | `''` | No | Additional CSS classes |
| data-testid | `string` | - | No | Test automation ID |
| onClick | `() => void` | - | No | Click handler |

## Variants
| Variant | Description | Token Overrides |
|---------|-------------|-----------------|
| primary | Main action button | `background: var(--color-primary); color: var(--color-text-inverse)` |
| secondary | Secondary action | `background: var(--color-secondary); color: var(--color-text-inverse)` |
| tertiary | Low-emphasis action | `background: transparent; color: var(--color-primary)` |
| ghost | Minimal style | `background: transparent; color: var(--color-text-primary)` |
| danger | Destructive action | `background: var(--color-error); color: var(--color-text-inverse)` |

## Sizes
| Size | Padding (v/h) | Font Size | Min Height | Use Case |
|------|---------------|-----------|------------|----------|
| xs | `var(--space-1)` / `var(--space-2)` | `var(--font-size-xs)` | 28px | Compact spaces |
| sm | `var(--space-2)` / `var(--space-3)` | `var(--font-size-sm)` | 36px | Default small |
| md | `var(--space-2)` / `var(--space-4)` | `var(--font-size-sm)` | 44px | **Default** |
| lg | `var(--space-3)` / `var(--space-5)` | `var(--font-size-md)` | 48px | Prominent actions |
| xl | `var(--space-3)` / `var(--space-6)` | `var(--font-size-lg)` | 52px | Hero actions |

## States
| State | Description | Token Overrides |
|-------|-------------|-----------------|
| default | Resting state | Base tokens |
| hover | Mouse hover | `background: var(--color-primary-hover)` |
| active | Mouse down | `background: var(--color-primary-active)` |
| focus | Keyboard focus | `outline: 2px solid var(--color-focus-ring); outline-offset: 2px` |
| disabled | Non-interactive | `background: var(--color-primary-disabled); cursor: not-allowed; opacity: 0.6` |
| loading | Async action | Spinner + `aria-busy="true"` |

## Accessibility Requirements
- [ ] **Keyboard**: Fully operable via keyboard (Tab to focus, Enter/Space to activate)
- [ ] **Focus**: Visible focus ring (≥2px, 3:1 contrast) using `var(--color-focus-ring)`
- [ ] **Screen Readers**: Meaningful label via children or `aria-label` for icon-only
- [ ] **Disabled**: Announced via `aria-disabled="true"`, removed from tab order
- [ ] **Loading**: Announced via `aria-busy="true"`, spinner hidden from screen readers
- [ ] **Touch Target**: ≥44×44px (web) / 48×48dp (Android) / 44×44pt (iOS)
- [ ] **Color**: Not sole indicator of state (icon + text for loading/disabled)
- [ ] **Reduced Motion**: Spinner animation respects `prefers-reduced-motion`

## Responsive Behavior
| Breakpoint | Behavior |
|------------|----------|
| < 640px (mobile) | Full width if `fullWidth` prop, otherwise auto |
| ≥ 640px (tablet) | Auto width, minimum touch target maintained |
| ≥ 1024px (desktop) | Auto width, hover states active |

## Platform Implementations
- [ ] **HTML/CSS** — `button.html` + `button.css`
- [ ] **React** — `Button.tsx` + `Button.css`
- [ ] **Vue** — `Button.vue`
- [ ] **SwiftUI** — `Button.swift`
- [ ] **Flutter** — `button.dart`
- [ ] **React Native** — `Button.tsx`

## Testing Checklist
- [ ] Unit tests (props, variants, states)
- [ ] Visual regression (all variants × sizes × states)
- [ ] Accessibility audit (axe-core, manual keyboard, screen reader)
- [ ] Token compliance (no magic numbers)
- [ ] Cross-browser (Chrome, Firefox, Safari, Edge)
- [ ] Cross-platform (iOS Safari, Android Chrome)
- [ ] Dark mode (all variants)
- [ ] RTL (Arabic/Hebrew layouts)

## Related Components
- [Link] — For navigation actions
- [IconButton] — For icon-only actions
- [ButtonGroup] — For grouped actions

## Changelog
| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | YYYY-MM-DD | [Name] | Initial specification |