# Responsive Patterns — Mobile-First Reference

**Breakpoints, fluid typography, layout patterns, and mobile-first strategies.** All values reference tokens from `token-reference.md`.

---

## Breakpoint System

### Token Definitions
```css
--bp-xs: 480px;   /* Extra small phones */
--bp-sm: 640px;   /* Small tablets / large phones */
--bp-md: 768px;   /* Tablets */
--bp-lg: 1024px;  /* Small laptops */
--bp-xl: 1280px;  /* Desktops */
--bp-2xl: 1536px; /* Large desktops */
```

### Media Query Pattern (Mobile-First)
```css
/* Base styles (mobile) — no media query */
.component {
  padding: var(--space-4);
  font-size: var(--font-size-md);
}

/* ≥640px */
@media (min-width: 640px) {
  .component {
    padding: var(--space-6);
  }
}

/* ≥768px */
@media (min-width: 768px) {
  .component {
    padding: var(--space-8);
  }
}

/* ≥1024px */
@media (min-width: 1024px) {
  .component {
    padding: var(--space-10);
  }
}

/* ≥1280px */
@media (min-width: 1280px) {
  .component {
    padding: var(--space-12);
  }
}

/* ≥1536px */
@media (min-width: 1536px) {
  .component {
    padding: var(--space-16);
  }
}
```

### Container Queries (Modern Alternative)
```css
.card-container {
  container-type: inline-size;
}

@container (min-width: 400px) {
  .card { /* styles for wider container */ }
}
```

---

## Fluid Typography

### clamp() Patterns
```css
/* Fluid heading: scales between min/max based on viewport */
.heading-1 {
  font-size: clamp(var(--font-size-3xl), 5vw, var(--font-size-5xl));
  /* 1.875rem → 3rem as viewport grows */
}

.heading-2 {
  font-size: clamp(var(--font-size-2xl), 4vw, var(--font-size-4xl));
  /* 1.5rem → 2.25rem */
}

.body {
  font-size: clamp(var(--font-size-sm), 1.5vw, var(--font-size-md));
  /* 0.875rem → 1rem */
}

/* Fluid spacing */
.section {
  padding-block: clamp(var(--space-8), 8vw, var(--space-16));
  /* 32px → 64px */
}
```

### Fluid Type Scale (Complete)
```css
:root {
  /* Base: 16px at 320px, 18px at 1280px */
  --fluid-base: clamp(1rem, 0.875rem + 0.5vw, 1.125rem);
  --fluid-scale: 1.25; /* modular ratio */

  /* Generated scale */
  --fluid-xs: calc(var(--fluid-base) / var(--fluid-scale));
  --fluid-sm: calc(var(--fluid-base) / calc(var(--fluid-scale) * 0.5));
  --fluid-md: var(--fluid-base);
  --fluid-lg: calc(var(--fluid-base) * var(--fluid-scale));
  --fluid-xl: calc(var(--fluid-base) * calc(var(--fluid-scale) * var(--fluid-scale)));
  --fluid-2xl: calc(var(--fluid-base) * calc(var(--fluid-scale) * var(--fluid-scale) * var(--fluid-scale)));
  --fluid-3xl: calc(var(--fluid-base) * pow(var(--fluid-scale), 4));
  --fluid-4xl: calc(var(--fluid-base) * pow(var(--fluid-scale), 5));
}
```

---

## Layout Patterns

### 1. Stack → Grid (Progressive Enhancement)
```css
/* Mobile: stacked */
.grid {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

/* Tablet: 2 columns */
@media (min-width: 768px) {
  .grid {
    flex-direction: row;
    flex-wrap: wrap;
  }
  .grid > * {
    flex: 1 1 calc(50% - var(--space-2));
  }
}

/* Desktop: 3-4 columns */
@media (min-width: 1024px) {
  .grid > * {
    flex: 1 1 calc(33.333% - var(--space-3));
  }
}
@media (min-width: 1280px) {
  .grid > * {
    flex: 1 1 calc(25% - var(--space-4));
  }
}
```

### 2. CSS Grid (Modern)
```css
.grid {
  display: grid;
  gap: var(--space-4);
  grid-template-columns: 1fr; /* mobile: 1 column */
}

@media (min-width: 640px) {
  .grid { grid-template-columns: repeat(2, 1fr); }
}
@media (min-width: 1024px) {
  .grid { grid-template-columns: repeat(3, 1fr); }
}
@media (min-width: 1280px) {
  .grid { grid-template-columns: repeat(4, 1fr); }
}

/* Auto-fit (content-driven) */
.grid-auto {
  display: grid;
  gap: var(--space-4);
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
}
```

### 3. Sidebar Layout
```css
.layout {
  display: grid;
  grid-template-rows: auto 1fr auto; /* header, body, footer */
  grid-template-columns: 1fr;
  min-height: 100vh;
}

@media (min-width: 1024px) {
  .layout {
    grid-template-columns: 280px 1fr; /* sidebar + main */
    grid-template-rows: auto 1fr auto;
    grid-template-areas:
      "header header"
      "sidebar main"
      "footer footer";
  }
  .sidebar { grid-area: sidebar; }
  .main { grid-area: main; }
  .header { grid-area: header; }
  .footer { grid-area: footer; }
}
```

### 4. Holy Grail Layout
```css
.holy-grail {
  display: grid;
  grid-template-rows: auto 1fr auto;
  grid-template-columns: 1fr;
  min-height: 100vh;
}

@media (min-width: 768px) {
  .holy-grail {
    grid-template-columns: 200px 1fr 200px; /* left, center, right */
    grid-template-rows: auto 1fr auto;
    grid-template-areas:
      "header header header"
      "nav main aside"
      "footer footer footer";
  }
}
```

---

## Spacing Patterns

### Responsive Spacing Scale
```css
:root {
  /* Space multipliers per breakpoint */
  --space-multiplier-xs: 0.75;  /* <480px */
  --space-multiplier-sm: 0.875; /* 480-640px */
  --space-multiplier-md: 1;     /* 640-1024px */
  --space-multiplier-lg: 1.25;  /* 1024-1280px */
  --space-multiplier-xl: 1.5;   /* >1280px */
}

/* Usage */
.section {
  padding-block: calc(var(--space-8) * var(--space-multiplier-md));
}

@media (min-width: 1024px) {
  .section {
    padding-block: calc(var(--space-8) * var(--space-multiplier-lg));
  }
}
```

### Component-Level Responsive Padding
```css
.card {
  padding: var(--space-4);
}

@media (min-width: 640px) {
  .card { padding: var(--space-5); }
}
@media (min-width: 1024px) {
  .card { padding: var(--space-6); }
}
```

---

## Image Patterns

### Responsive Images
```html
<!-- Art direction: different crops -->
<picture>
  <source media="(min-width: 1024px)" srcset="hero-desktop.webp" type="image/webp">
  <source media="(min-width: 768px)" srcset="hero-tablet.webp" type="image/webp">
  <img src="hero-mobile.webp" alt="..." width="1200" height="600" loading="lazy">
</picture>

<!-- Resolution switching: same aspect, different sizes -->
<img
  srcset="
    image-320w.webp 320w,
    image-640w.webp 640w,
    image-1024w.webp 1024w,
    image-1280w.webp 1280w
  "
  sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
  src="image-640w.webp"
  alt="..."
  width="640"
  height="400"
  loading="lazy"
>
```

### Aspect Ratio Boxes (No CLS)
```css
.aspect-ratio-box {
  aspect-ratio: 16 / 9;
  width: 100%;
  overflow: hidden;
}

.aspect-ratio-box img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* Common ratios */
.aspect-square { aspect-ratio: 1 / 1; }
.aspect-video { aspect-ratio: 16 / 9; }
.aspect-photo { aspect-ratio: 4 / 3; }
.aspect-portrait { aspect-ratio: 3 / 4; }
```

---

## Navigation Patterns

### Mobile Navigation (Hamburger → Drawer)
```tsx
// CSS
.nav-drawer {
  position: fixed;
  inset: 0;
  transform: translateX(-100%);
  transition: transform var(--transition-normal);
  z-index: var(--z-index-modal);
}

.nav-drawer.open {
  transform: translateX(0);
}

@media (min-width: 768px) {
  .nav-drawer {
    position: static;
    transform: none;
    display: flex;
  }
  .hamburger { display: none; }
}
```

### Responsive Tabs
```css
.tabs {
  display: flex;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  -webkit-overflow-scrolling: touch;
  gap: var(--space-2);
  padding: var(--space-2);
  margin: calc(var(--space-2) * -1);
}

@media (min-width: 640px) {
  .tabs {
    overflow-x: visible;
    scroll-snap-type: none;
    border-bottom: 1px solid var(--color-border);
  }
}
```

---

## Touch Target Patterns

### Minimum Touch Targets
```css
/* Ensure 44×44px minimum */
.touch-target {
  min-height: 44px;
  min-width: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

/* Icon buttons: expand hit area */
.icon-button {
  padding: var(--space-2); /* 8px → 44px with 24px icon */
}

.icon-button svg {
  width: 24px;
  height: 24px;
}

/* Spacing between targets */
.touch-target + .touch-target {
  margin-left: var(--space-2); /* 8px minimum */
}
```

---

## Testing Checklist

### Required Viewport Tests
| Width | Device | Test |
|-------|--------|------|
| 320px | iPhone SE / small Android | No horizontal scroll, touch targets work |
| 375px | iPhone 12/13/14 standard | Standard mobile |
| 414px | iPhone Plus / large Android | Large mobile |
| 768px | iPad Portrait | Tablet layout |
| 1024px | iPad Landscape / small laptop | Desktop-ish |
| 1280px | Standard desktop | Full desktop |
| 1440px | Large desktop | Wide layout |
| 1920px | Full HD | Max width constraints |

### Responsive Audit Commands
```bash
# Test with Chrome DevTools device toolbar
# Or use Playwright for automated testing

# Check for horizontal scroll at 320px
# Verify touch targets ≥44px
# Confirm no hover-only interactions
# Test font scaling (200% zoom)
# Verify RTL layout
```

---

## Common Pitfalls to Avoid

| Pitfall | Solution |
|---------|----------|
| Fixed `width: 1200px` | Use `max-width: 1200px; width: 100%` |
| `padding: 20px` (magic number) | Use `padding: var(--space-5)` |
| Desktop-first media queries | Use mobile-first `min-width` |
| Hover-only dropdowns | Add click/touch toggle + keyboard |
| Text too small on mobile | Minimum 16px (1rem) for body text |
| Images without dimensions | Always `width`/`height` or `aspect-ratio` |
| Breakpoints in px only | Use token references: `var(--bp-md)` |
| No dark mode testing | Test both light/dark at each breakpoint |