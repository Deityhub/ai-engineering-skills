# Accessibility Checklist — WCAG 2.1 AA + Gaps Addressed

**Run through this checklist before declaring a design task complete.** Every item must pass, or be explicitly waived with justification.

---

## 🔴 Accessibility (WCAG 2.1 AA) — Blocking

### Color & Contrast
| # | Check | Pass? | Notes |
|---|-------|-------|-------|
| A1 | Text contrast ≥4.5:1 (normal text) | | |
| A2 | Text contrast ≥3:1 (large text: 18pt+ or 14pt+ bold) | | |
| A3 | UI component contrast ≥3:1 (borders, icons, focus rings) | | |
| A4 | Focus ring contrast ≥3:1 vs adjacent colors | | |
| A5 | Error/success/warning states not color-only (icons + text) | | |

### Keyboard & Focus
| # | Check | Pass? | Notes |
|---|-------|-------|-------|
| A6 | All interactive elements keyboard-focusable | | |
| A7 | Visible focus ring on ALL interactive elements (≥2px) | | |
| A8 | Focus ring never removed without replacement (`outline: none` + box-shadow) | | |
| A9 | Focus order follows logical reading order (top-left → bottom-right) | | |
| A10 | Skip link ("Skip to main content") as first focusable element | | |
| A11 | No keyboard traps (modals trap focus, Escape closes) | | |
| A12 | Tab index only 0 or -1 (no positive tabIndex) | | |

### Semantics & Structure
| # | Check | Pass? | Notes |
|---|-------|-------|-------|
| A13 | Semantic HTML: `<button>` for actions, `<a>` for navigation | | |
| A14 | Landmarks present: `<header>`, `<nav>`, `<main>`, `<aside>`, `<footer>` | | |
| A15 | Heading hierarchy logical (h1 → h2 → h3, no skipped levels) | | |
| A16 | Lists use `<ul>`/`<ol>`/`<li>` (not divs with bullets) | | |
| A17 | Tables have `<caption>`, `<th scope="col|row">`, no layout tables | | |

### Images & Media
| # | Check | Pass? | Notes |
|---|-------|-------|-------|
| A18 | Meaningful images have descriptive `alt` text | | |
| A19 | Decorative images use `alt=""` (not missing alt) | | |
| A20 | Icons: `aria-hidden="true"` + parent has `aria-label` if icon-only | | |
| A21 | Complex images (charts) have text alternative or data table | | |
| A22 | Video: captions provided; audio: transcript provided | | |
| A23 | No auto-playing media >5s without pause/stop/mute controls | | |

### Forms
| # | Check | Pass? | Notes |
|---|-------|-------|-------|
| A24 | Every input has associated `<label for="id">` (not placeholder-only) | | |
| A25 | Required fields marked with `required` attribute + visual indicator | | |
| A26 | Error messages linked via `aria-describedby` + `aria-invalid="true"` | | |
| A27 | Error container has `aria-live="polite"` (or `assertive` for critical) | | |
| A28 | Error messages describe *how to fix*, not just *what's wrong* | | |
| A29 | Autocomplete attributes on relevant fields (`autocomplete="email"`) | | |
| A30 | Fieldsets + legends for grouped inputs (radio, checkbox groups) | | |

### Motion & Interaction
| # | Check | Pass? | Notes |
|---|-------|-------|-------|
| A31 | `prefers-reduced-motion` respected — disable non-essential animation | | |
| A32 | No flashing content >3 times/second (WCAG 2.3.1) | | |
| A33 | Parallax/scroll animations have reduced-motion alternative | | |
| A34 | Touch targets ≥44×44px (CSS) / 48×48dp (Android) / 44×44pt (iOS) | | |
| A35 | ≥8px spacing between adjacent touch targets | | |
| A36 | No hover-only interactions without touch/keyboard alternative | | |

### Text & Language
| # | Check | Pass? | Notes |
|---|-------|-------|-------|
| A37 | Page has `lang` attribute on `<html>` | | |
| A38 | Page has descriptive `<title>` | | |
| A39 | Text spacing overrides supported (user stylesheet): line-height ≥1.5, paragraph spacing ≥2× line-height, letter-spacing ≥0.12× font-size, word-spacing ≥0.16× font-size | | |
| A40 | No text in images (except logos) — use real text + CSS | | |
| A41 | RTL: logical properties used (`margin-inline-start`, `padding-inline-end`) | | |
| A42 | Design works with 200-300% text zoom (no horizontal scroll at 320px) | | |

---

## 🟡 Design System Consistency

| # | Check | Pass? | Notes |
|---|-------|-------|-------|
| D1 | Only named tokens used (no magic numbers: px, rem, hex, rgb) | | |
| D2 | Color system complete: semantic + functional + state + dark mode | | |
| D3 | Modular type scale used consistently (no arbitrary font-sizes) | | |
| D4 | 8px base spacing grid (all spacing multiples of 4px) | | |
| D5 | Border radius tokens used (no arbitrary border-radius) | | |
| D6 | Shadow tokens used (no arbitrary box-shadow) | | |
| D7 | Breakpoint tokens used (no arbitrary media queries) | | |
| D8 | Component names descriptive (PascalCase): `PrimaryButton`, `InputField` | | |
| D9 | Presentational vs container components separated | | |
| D10 | Props allow customization without forking (`variant`, `size`, `disabled`) | | |
| D11 | Aligns with existing project conventions (if applicable) | | |
| D12 | JSON token export available for tool interoperability | | |

---

## 🟢 Responsiveness

| # | Check | Pass? | Notes |
|---|-------|-------|-------|
| R1 | Layout functional at 320px width (no horizontal scroll) | | |
| R2 | Layout functional at 768px | | |
| R3 | Layout functional at 1024px | | |
| R4 | Layout functional at 1440px+ | | |
| R5 | Mobile-first media queries (`min-width`) used | | |
| R6 | Fluid typography via `clamp()` where appropriate | | |
| R7 | Images responsive (`max-width: 100%`, `height: auto`) | | |
| R8 | Touch targets ≥44px on mobile viewports | | |
| R9 | No content loss or overlap at any breakpoint | | |
| R10 | Navigation usable on mobile (hamburger, drawer, etc.) | | |

---

## ⚪ Performance

| # | Check | Pass? | Notes |
|---|-------|-------|-------|
| P1 | Images have explicit `width`/`height` attributes | | |
| P2 | Off-screen images use `loading="lazy"` | | |
| P3 | Images use modern formats (WebP/AVIF) with fallbacks | | |
| P4 | CSS preferred over JS for animations/interactions | | |
| P5 | No layout shift (CLS): space reserved for images/ads/fonts | | |
| P6 | Fonts: `font-display: swap` or `optional`; preload critical fonts | | |
| P7 | No heavy CSS-in-JS runtime unless project requires it | | |

---

## 📱 Platform-Specific

### iOS / Safari
| # | Check | Pass? | Notes |
|---|-------|-------|-------|
| I1 | Safe area insets respected (`env(safe-area-inset-*)`) | | |
| I2 | Dynamic Type supported (text scales with system setting) | | |
| I3 | Touch targets 44×44pt minimum | | |
| I4 | `-webkit-tap-highlight-color` managed | | |

### Android / Chrome
| # | Check | Pass? | Notes |
|---|-------|-------|-------|
| A1 | Material Design tokens considered (if applicable) | | |
| A2 | Touch targets 48×48dp minimum | | |
| A3 | RTL layouts tested | | |
| A4 | Back gesture / navigation handled | | |

### Cross-Platform (React Native, Flutter, etc.)
| # | Check | Pass? | Notes |
|---|-------|-------|-------|
| C1 | Platform-specific component mappings documented | | |
| C2 | Tokens exported in platform-native format | | |
| C3 | Accessibility APIs used (AccessibilityInfo, Semantics, etc.) | | |

---

## Sign-off

| Field | Value |
|-------|-------|
| Reviewer | |
| Date | |
| Waived items (with reason) | |

---

## Automated Validation

Run these scripts for deterministic checks:

```bash
# Accessibility audit (HTML/React/Vue)
python scripts/audit-accessibility.py --file Component.tsx --format markdown

# Token compliance (no magic numbers)
python scripts/validate-tokens.py --file Component.tsx --tokens tokens.json

# Full project scan
python scripts/audit-accessibility.py --dir ./src --output report.md
python scripts/validate-tokens.py --dir ./src --tokens tokens.json --output report.md
```

---

## Quick Reference: Most Common Failures

| Failure | Fix |
|---------|-----|
| `outline: none` on focus | Replace with `box-shadow: 0 0 0 2px var(--color-focus-ring)` |
| Missing `label` for input | Add `<label for="id">` + `<input id="id">` |
| Color-only error state | Add icon + text: `<span aria-live="polite">⚠ Error: message</span>` |
| Magic number `padding: 16px` | Use `padding: var(--space-4)` |
| No dark mode colors | Define all colors in `@media (prefers-color-scheme: dark)` |
| No skip link | Add `<a href="#main" class="skip-link">Skip to main content</a>` as first child of `<body>` |
| Heading skip (h1 → h3) | Ensure sequential hierarchy |
| Fixed `width: 1200px` | Use `max-width: var(--container-max)` + `width: 100%` |