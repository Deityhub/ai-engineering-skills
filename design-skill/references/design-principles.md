# Design Principles — Condensed Reference

Quick-reference for the 5 core principles. Full details in `universal-prompt.md` or `SKILL.md`.

---

## 1. Accessibility First (WCAG 2.1 AA)
| Rule | Minimum |
|------|---------|
| Text contrast | 4.5:1 (normal), 3:1 (large: 18pt+/14pt+ bold) |
| UI component contrast | 3:1 |
| Focus ring | ≥2px, 3:1 vs adjacent, never `outline: none` alone |
| Touch targets | 44×44px (CSS), 48×48dp (Android), 44×44pt (iOS) |
| Semantics | `<button>`, `<nav>`, `<main>`, `<label>`, `<fieldset>`, landmarks |
| Forms | `label[for]` + `input[id]`, `aria-describedby` + `aria-invalid` + `aria-live` |
| Motion | Respect `prefers-reduced-motion` |
| Focus order | Logical; skip link first |
| Text spacing | User overrides: line-height ≥1.5, para spacing ≥2×, letter ≥0.12em, word ≥0.16em |
| RTL | Logical properties (`margin-inline-start`) |

---

## 2. Design System Consistency
**Never magic numbers — only named tokens.**

| Category | Tokens |
|----------|--------|
| Spacing | `--space-1` (4px) through `--space-16` (64px), 8px base grid |
| Color | Semantic (primary, surface, text), functional (error, success, warning), state (hover, active, disabled, focus-ring), **dark mode for all** |
| Typography | Modular scale 1.25: xs (0.75rem) → 5xl (3rem); weights 400/500/600/700 |
| Radius | sm (4px), md (6px), lg (8px), xl (12px), full (9999px) |
| Shadow | sm, md, lg |
| Breakpoints | sm (640), md (768), lg (1024), xl (1280) — mobile-first |

**JSON export** in `token-reference.md` for Style Dictionary / Figma Tokens interop.

---

## 3. Responsive by Default
- Mobile-first: base styles → `@media (min-width: ...)` overrides
- Fluid type: `clamp(min, preferred, max)` where appropriate
- Test widths: 320px, 768px, 1024px, 1440px+
- No hover-only without touch alternative
- Touch targets ≥44px on mobile

---

## 4. Performance Conscious
- Images: WebP/AVIF, `width`/`height`, `loading="lazy"`
- Minimal CLS: reserve space, avoid reflow animations
- CSS > JS for animations (`transition`, `@keyframes`, `:hover`, `:focus`)
- Avoid heavy CSS-in-JS unless already adopted

---

## 5. Component Thinking (Atomic Design)
| Level | Examples | Purpose |
|-------|----------|---------|
| Atoms | Button, Input, Badge, Avatar, Icon, Typography, Spacer | Indivisible primitives |
| Molecules | FormField, Card, Dropdown, Toast, Modal | Simple compositions |
| Organisms | Header, Footer, Sidebar, DataTable, SearchResults | Complex sections |
| Templates/Pages | Layout compositions | Full views |

**Separate presentational from container components.**
Props: `variant`, `size`, `disabled`, `loading` — consistent naming.

---

## Review Priority Order
1. 🔴 **Accessibility** (blocking)
2. 🟡 **Design System** (inconsistency)
3. 🟢 **Responsiveness** (breakage)
4. ⚪ **Performance** (optimization)

---

## Agentic Delegation
- **Extract context**: `scripts/compress-context.py` → token diff + decisions + findings
- **Parallel validate**: Multiple agents run `audit-accessibility.py` / `validate-tokens.py` on different components
- **Consensus**: `design-review-protocol.md` for structured validation
- **Handoff**: Compressed context + specs = minimal context waste