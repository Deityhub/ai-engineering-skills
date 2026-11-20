# Page Specification: [PageName]

## Overview
**Name**: [PageName]
**Route**: [/path/to/page]
**Category**: [Landing | Dashboard | Form | Detail | Settings | Auth]
**Status**: [Draft | Review | Approved | Deprecated]
**Owner**: [Designer/Developer]
**Last Updated**: [YYYY-MM-DD]

## Purpose
[One paragraph describing the page's primary goal and user intent.]

## User Flow
[Describe the user journey leading to and from this page.]

## Layout Structure
```
┌─────────────────────────────────────┐
│ Header (Organism)                   │
├─────────────┬───────────────────────┤
│ Sidebar     │ Main Content          │
│ (Organism)  │ ┌───────────────────┐ │
│             │ │ Section 1         │ │
│             │ │ (Molecule/Organism)│ │
│             │ ├───────────────────┤ │
│             │ │ Section 2         │ │
│             │ └───────────────────┘ │
├─────────────┴───────────────────────┤
│ Footer (Organism)                   │
└─────────────────────────────────────┘
```

## Sections

### Section 1: [Name]
**Component**: [ComponentName]
**Purpose**: [What this section achieves]
**Props**: [Key props passed]
**Variants**: [Which variants used]
**Responsive**: [Behavior at each breakpoint]

### Section 2: [Name]
...

## Components Used
| Component | Variant | Size | Quantity | Location |
|-----------|---------|------|----------|----------|
| Button | primary | md | 3 | Header, Main, Footer |
| Card | elevated | - | 5 | Main grid |
| Input | - | md | 4 | Form section |
| Badge | success | sm | 8 | Card headers |

## Design Tokens
### Spacing
- Page padding: `var(--space-6)` (md), `var(--space-8)` (lg)
- Section gap: `var(--space-8)` (md), `var(--space-12)` (lg)
- Component gap: `var(--space-4)` (md), `var(--space-6)` (lg)

### Color
- Background: `var(--color-surface)`
- Section backgrounds: `var(--color-surface)`, `var(--color-surface-hover)` (alternating)
- Text: `var(--color-text-primary)`, `var(--color-text-secondary)`

### Typography
- Page title: `var(--font-size-4xl)`, `var(--font-weight-bold)`
- Section headings: `var(--font-size-2xl)`, `var(--font-weight-semibold)`
- Body: `var(--font-size-md)`, `var(--font-weight-normal)`

### Breakpoints
| Breakpoint | Layout Changes |
|------------|----------------|
| < 640px | Single column, stacked sections, hamburger menu |
| 640px - 1023px | Two-column sidebar + main, condensed header |
| ≥ 1024px | Full layout with sidebar, expanded header |

## Responsive Behavior
### Mobile (< 640px)
- [ ] Single column layout
- [ ] Collapsible navigation
- [ ] Touch-optimized controls (44px targets)
- [ ] Stacked form fields
- [ ] Bottom sheet for modals

### Tablet (640px - 1023px)
- [ ] Two-column layout (sidebar + main)
- [ ] Condensed header
- [ ] Side-by-side form fields where appropriate

### Desktop (≥ 1024px)
- [ ] Full layout with persistent sidebar
- [ ] Hover states active
- [ ] Keyboard shortcuts available
- [ ] Multi-column grids

## Accessibility
- [ ] **Landmarks**: `<header>`, `<nav>`, `<main>`, `<aside>`, `<footer>`
- [ ] **Skip Link**: "Skip to main content" as first focusable element
- [ ] **Heading Hierarchy**: h1 → h2 → h3 (no skipped levels)
- [ ] **Focus Management**: Logical tab order, focus trap in modals
- [ ] **ARIA**: Live regions for dynamic content, labels for all inputs
- [ ] **Color**: WCAG AA contrast, not color-only indicators
- [ ] **Touch**: 44×44px minimum on mobile
- [ ] **Reduced Motion**: Animations respect preference

## Performance
- [ ] **Images**: WebP/AVIF, `width`/`height`, `loading="lazy"` below fold
- [ ] **Fonts**: `font-display: swap`, preload critical fonts
- [ ] **CSS**: Critical CSS inlined, non-critical deferred
- [ ] **JS**: Code-split by route, lazy-load heavy components
- [ ] **CLS**: Space reserved for images/ads/fonts

## SEO / Meta
- [ ] **Title**: Unique, descriptive, ≤60 chars
- [ ] **Description**: Unique, ≤160 chars
- [ ] **Open Graph**: og:title, og:description, og:image
- [ ] **Canonical**: Self-referencing
- [ ] **Structured Data**: JSON-LD for page type

## Analytics / Tracking
| Event | Trigger | Properties |
|-------|---------|------------|
| page_view | Mount | page_name, referrer |
| cta_click | Button click | cta_name, location |
| form_submit | Form submit | form_name, success/error |

## Testing Checklist
- [ ] Visual regression (all breakpoints)
- [ ] Accessibility audit (axe-core, keyboard, screen reader)
- [ ] Cross-browser (Chrome, Firefox, Safari, Edge)
- [ ] Mobile devices (iOS Safari, Android Chrome)
- [ ] Performance (Lighthouse ≥90)
- [ ] SEO (meta tags, structured data)
- [ ] Analytics events firing

## Related Pages
- [Previous Page] — User comes from
- [Next Page] — User goes to
- [Error Page] — Fallback

## Changelog
| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | YYYY-MM-DD | [Name] | Initial specification |