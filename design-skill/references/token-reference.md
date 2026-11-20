# Design Token Reference — Complete System

**Single source of truth** for all design tokens. Use CSS custom properties in code; JSON for tool interoperability (Style Dictionary, Figma Tokens, Specify, etc.).

---

## CSS Custom Properties (for direct use in stylesheets)

### Spacing — 8px Base Grid
```css
/* Base scale: multiply by 4px */
--space-1: 4px;    /* 1 × 4px */
--space-2: 8px;    /* 2 × 4px */
--space-3: 12px;   /* 3 × 4px */
--space-4: 16px;   /* 4 × 4px */
--space-5: 20px;   /* 5 × 4px */
--space-6: 24px;   /* 6 × 4px */
--space-8: 32px;   /* 8 × 4px */
--space-10: 40px;  /* 10 × 4px */
--space-12: 48px;  /* 12 × 4px */
--space-16: 64px;  /* 16 × 4px */

/* Semantic aliases */
--space-xs: var(--space-1);
--space-sm: var(--space-2);
--space-md: var(--space-4);
--space-lg: var(--space-6);
--space-xl: var(--space-8);
--space-2xl: var(--space-12);
--space-3xl: var(--space-16);
```

### Color — Semantic + Functional + State + Dark Mode

#### Light Mode (default)
```css
/* Primary brand */
--color-primary: #2563eb;
--color-primary-hover: #1d4ed8;
--color-primary-active: #1e40af;
--color-primary-disabled: #93c5fd;

/* Secondary */
--color-secondary: #64748b;
--color-secondary-hover: #475569;
--color-secondary-active: #334155;
--color-secondary-disabled: #cbd5e1;

/* Surfaces */
--color-surface: #ffffff;
--color-surface-hover: #f8fafc;
--color-surface-elevated: #ffffff;
--color-surface-overlay: rgba(15, 23, 42, 0.8);

/* Borders */
--color-border: #e2e8f0;
--color-border-strong: #cbd5e1;
--color-border-focus: var(--color-focus-ring);

/* Focus ring (critical for accessibility) */
--color-focus-ring: #2563eb;
--color-focus-ring-offset: #ffffff;

/* Text */
--color-text-primary: #0f172a;
--color-text-secondary: #475569;
--color-text-muted: #94a3b8;
--color-text-inverse: #f8fafc;
--color-text-link: var(--color-primary);
--color-text-link-hover: var(--color-primary-hover);

/* Status / Feedback */
--color-error: #dc2626;
--color-error-light: #fef2f2;
--color-error-text: #b91c1c;
--color-error-border: #fecaca;

--color-success: #16a34a;
--color-success-light: #f0fdf4;
--color-success-text: #15803d;
--color-success-border: #bbf7d0;

--color-warning: #ca8a04;
--color-warning-light: #fefce8;
--color-warning-text: #a16207;
--color-warning-border: #fef08a;

--color-info: #0284c7;
--color-info-light: #eff6ff;
--color-info-text: #0165a3;
--color-info-border: #bae6fd;

/* Disabled states */
--color-disabled-bg: #f1f5f9;
--color-disabled-text: #94a3b8;
--color-disabled-border: #e2e8f0;
```

#### Dark Mode (auto via `prefers-color-scheme`)
```css
@media (prefers-color-scheme: dark) {
  /* Primary brand - adjusted for dark backgrounds */
  --color-primary: #3b82f6;
  --color-primary-hover: #60a5fa;
  --color-primary-active: #2563eb;
  --color-primary-disabled: #1e3a5f;

  --color-secondary: #94a3b8;
  --color-secondary-hover: #cbd5e1;
  --color-secondary-active: #64748b;
  --color-secondary-disabled: #475569;

  /* Surfaces */
  --color-surface: #0f172a;
  --color-surface-hover: #1e293b;
  --color-surface-elevated: #1e293b;
  --color-surface-overlay: rgba(0, 0, 0, 0.8);

  /* Borders */
  --color-border: #334155;
  --color-border-strong: #475569;
  --color-border-focus: var(--color-focus-ring);

  /* Focus ring - ensure contrast on dark */
  --color-focus-ring: #60a5fa;
  --color-focus-ring-offset: #0f172a;

  /* Text */
  --color-text-primary: #f1f5f9;
  --color-text-secondary: #cbd5e1;
  --color-text-muted: #64748b;
  --color-text-inverse: #0f172a;
  --color-text-link: var(--color-primary);
  --color-text-link-hover: var(--color-primary-hover);

  /* Status / Feedback - adjusted for dark */
  --color-error: #f87171;
  --color-error-light: #7f1d1d;
  --color-error-text: #fecaca;
  --color-error-border: #991b1b;

  --color-success: #4ade80;
  --color-success-light: #14532d;
  --color-success-text: #bbf7d0;
  --color-success-border: #166534;

  --color-warning: #facc15;
  --color-warning-light: #713f12;
  --color-warning-text: #fef08a;
  --color-warning-border: #854d0e;

  --color-info: #38bdf8;
  --color-info-light: #1e3a5f;
  --color-info-text: #bae6fd;
  --color-info-border: #1e429f;

  /* Disabled */
  --color-disabled-bg: #1e293b;
  --color-disabled-text: #64748b;
  --color-disabled-border: #334155;
}
```

### Typography — Modular Scale (1.25 Ratio)
```css
/* Font families */
--font-family-sans: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
--font-family-mono: ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace;

/* Font sizes — modular scale: base 1rem × 1.25^n */
--font-size-xs: 0.75rem;     /* 12px  = 1rem × 1.25^-1 */
--font-size-sm: 0.875rem;    /* 14px  = 1rem × 1.25^-0.5 */
--font-size-md: 1rem;        /* 16px  = base */
--font-size-lg: 1.125rem;    /* 18px  = 1rem × 1.25^0.5 */
--font-size-xl: 1.25rem;     /* 20px  = 1rem × 1.25^1 */
--font-size-2xl: 1.5rem;     /* 24px  = 1rem × 1.25^2 */
--font-size-3xl: 1.875rem;   /* 30px  = 1rem × 1.25^3 */
--font-size-4xl: 2.25rem;    /* 36px  = 1rem × 1.25^4 */
--font-size-5xl: 3rem;       /* 48px  = 1rem × 1.25^5 */
--font-size-6xl: 3.75rem;    /* 60px  = 1rem × 1.25^6 */

/* Semantic aliases */
--font-size-body: var(--font-size-md);
--font-size-body-sm: var(--font-size-sm);
--font-size-heading-1: var(--font-size-5xl);
--font-size-heading-2: var(--font-size-4xl);
--font-size-heading-3: var(--font-size-3xl);
--font-size-heading-4: var(--font-size-2xl);
--font-size-heading-5: var(--font-size-xl);
--font-size-heading-6: var(--font-size-lg);

/* Font weights */
--font-weight-normal: 400;
--font-weight-medium: 500;
--font-weight-semibold: 600;
--font-weight-bold: 700;

/* Line heights */
--line-height-tight: 1.25;
--line-height-snug: 1.375;
--line-height-normal: 1.5;
--line-height-relaxed: 1.625;
--line-height-loose: 1.75;

/* Letter spacing */
--letter-spacing-tight: -0.02em;
--letter-spacing-normal: 0;
--letter-spacing-wide: 0.02em;
--letter-spacing-wider: 0.04em;
--letter-spacing-widest: 0.1em;
```

### Border Radius
```css
--radius-none: 0;
--radius-sm: 4px;
--radius-md: 6px;
--radius-lg: 8px;
--radius-xl: 12px;
--radius-2xl: 16px;
--radius-full: 9999px;

/* Semantic aliases */
--radius-button: var(--radius-md);
--radius-input: var(--radius-md);
--radius-card: var(--radius-lg);
--radius-modal: var(--radius-xl);
--radius-badge: var(--radius-full);
```

### Shadows
```css
--shadow-none: none;
--shadow-xs: 0 1px 1px 0 rgb(0 0 0 / 0.04);
--shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
--shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
--shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
--shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
--shadow-2xl: 0 25px 50px -12px rgb(0 0 0 / 0.25);
--shadow-inner: inset 0 2px 4px 0 rgb(0 0 0 / 0.05);

/* Semantic aliases */
--shadow-card: var(--shadow-md);
--shadow-dropdown: var(--shadow-lg);
--shadow-modal: var(--shadow-xl);
--shadow-toast: var(--shadow-lg);
```

### Breakpoints (Mobile-First)
```css
--bp-xs: 480px;   /* Extra small phones */
--bp-sm: 640px;   /* Small tablets / large phones */
--bp-md: 768px;   /* Tablets */
--bp-lg: 1024px;  /* Small laptops */
--bp-xl: 1280px;  /* Desktops */
--bp-2xl: 1536px; /* Large desktops */

/* Media query helpers */
@media (min-width: 480px)  { /* xs */ }
@media (min-width: 640px)  { /* sm */ }
@media (min-width: 768px)  { /* md */ }
@media (min-width: 1024px) { /* lg */ }
@media (min-width: 1280px) { /* xl */ }
@media (min-width: 1536px) { /* 2xl */ }
```

### Z-Index Scale
```css
--z-index-dropdown: 100;
--z-index-sticky: 200;
--z-index-fixed: 300;
--z-index-modal-backdrop: 400;
--z-index-modal: 500;
--z-index-popover: 600;
--z-index-tooltip: 700;
--z-index-toast: 800;
```

### Transitions
```css
--transition-fast: 100ms ease;
--transition-normal: 200ms ease;
--transition-slow: 300ms ease;
--transition-slower: 500ms ease;
```

---

## JSON Format (Style Dictionary / Figma Tokens / Specify Compatible)

```json
{
  "spacing": {
    "1": { "value": "4px", "type": "dimension" },
    "2": { "value": "8px", "type": "dimension" },
    "3": { "value": "12px", "type": "dimension" },
    "4": { "value": "16px", "type": "dimension" },
    "5": { "value": "20px", "type": "dimension" },
    "6": { "value": "24px", "type": "dimension" },
    "8": { "value": "32px", "type": "dimension" },
    "10": { "value": "40px", "type": "dimension" },
    "12": { "value": "48px", "type": "dimension" },
    "16": { "value": "64px", "type": "dimension" }
  },
  "color": {
    "primary": {
      "value": { "light": "#2563eb", "dark": "#3b82f6" },
      "hover": { "light": "#1d4ed8", "dark": "#60a5fa" },
      "active": { "light": "#1e40af", "dark": "#2563eb" },
      "disabled": { "light": "#93c5fd", "dark": "#1e3a5f" },
      "type": "color"
    },
    "secondary": {
      "value": { "light": "#64748b", "dark": "#94a3b8" },
      "hover": { "light": "#475569", "dark": "#cbd5e1" },
      "active": { "light": "#334155", "dark": "#64748b" },
      "disabled": { "light": "#cbd5e1", "dark": "#475569" },
      "type": "color"
    },
    "surface": {
      "value": { "light": "#ffffff", "dark": "#0f172a" },
      "hover": { "light": "#f8fafc", "dark": "#1e293b" },
      "elevated": { "light": "#ffffff", "dark": "#1e293b" },
      "overlay": { "light": "rgba(15, 23, 42, 0.8)", "dark": "rgba(0, 0, 0, 0.8)" },
      "type": "color"
    },
    "border": {
      "value": { "light": "#e2e8f0", "dark": "#334155" },
      "strong": { "light": "#cbd5e1", "dark": "#475569" },
      "focus": { "light": "#2563eb", "dark": "#60a5fa" },
      "type": "color"
    },
    "focusRing": {
      "value": { "light": "#2563eb", "dark": "#60a5fa" },
      "offset": { "light": "#ffffff", "dark": "#0f172a" },
      "type": "color"
    },
    "text": {
      "primary": { "light": "#0f172a", "dark": "#f1f5f9" },
      "secondary": { "light": "#475569", "dark": "#cbd5e1" },
      "muted": { "light": "#94a3b8", "dark": "#64748b" },
      "inverse": { "light": "#f8fafc", "dark": "#0f172a" },
      "link": { "light": "#2563eb", "dark": "#3b82f6" },
      "linkHover": { "light": "#1d4ed8", "dark": "#60a5fa" },
      "type": "color"
    },
    "error": {
      "value": { "light": "#dc2626", "dark": "#f87171" },
      "light": { "light": "#fef2f2", "dark": "#7f1d1d" },
      "text": { "light": "#b91c1c", "dark": "#fecaca" },
      "border": { "light": "#fecaca", "dark": "#991b1b" },
      "type": "color"
    },
    "success": {
      "value": { "light": "#16a34a", "dark": "#4ade80" },
      "light": { "light": "#f0fdf4", "dark": "#14532d" },
      "text": { "light": "#15803d", "dark": "#bbf7d0" },
      "border": { "light": "#bbf7d0", "dark": "#166534" },
      "type": "color"
    },
    "warning": {
      "value": { "light": "#ca8a04", "dark": "#facc15" },
      "light": { "light": "#fefce8", "dark": "#713f12" },
      "text": { "light": "#a16207", "dark": "#fef08a" },
      "border": { "light": "#fef08a", "dark": "#854d0e" },
      "type": "color"
    },
    "info": {
      "value": { "light": "#0284c7", "dark": "#38bdf8" },
      "light": { "light": "#eff6ff", "dark": "#1e3a5f" },
      "text": { "light": "#0165a3", "dark": "#bae6fd" },
      "border": { "light": "#bae6fd", "dark": "#1e429f" },
      "type": "color"
    },
    "disabled": {
      "bg": { "light": "#f1f5f9", "dark": "#1e293b" },
      "text": { "light": "#94a3b8", "dark": "#64748b" },
      "border": { "light": "#e2e8f0", "dark": "#334155" },
      "type": "color"
    }
  },
  "typography": {
    "fontFamily": {
      "sans": { "value": "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif", "type": "fontFamily" },
      "mono": { "value": "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace", "type": "fontFamily" }
    },
    "fontSize": {
      "xs": { "value": "0.75rem", "type": "fontSize" },
      "sm": { "value": "0.875rem", "type": "fontSize" },
      "md": { "value": "1rem", "type": "fontSize" },
      "lg": { "value": "1.125rem", "type": "fontSize" },
      "xl": { "value": "1.25rem", "type": "fontSize" },
      "2xl": { "value": "1.5rem", "type": "fontSize" },
      "3xl": { "value": "1.875rem", "type": "fontSize" },
      "4xl": { "value": "2.25rem", "type": "fontSize" },
      "5xl": { "value": "3rem", "type": "fontSize" },
      "6xl": { "value": "3.75rem", "type": "fontSize" }
    },
    "fontWeight": {
      "normal": { "value": 400, "type": "fontWeight" },
      "medium": { "value": 500, "type": "fontWeight" },
      "semibold": { "value": 600, "type": "fontWeight" },
      "bold": { "value": 700, "type": "fontWeight" }
    },
    "lineHeight": {
      "tight": { "value": 1.25, "type": "lineHeight" },
      "snug": { "value": 1.375, "type": "lineHeight" },
      "normal": { "value": 1.5, "type": "lineHeight" },
      "relaxed": { "value": 1.625, "type": "lineHeight" },
      "loose": { "value": 1.75, "type": "lineHeight" }
    },
    "letterSpacing": {
      "tight": { "value": "-0.02em", "type": "dimension" },
      "normal": { "value": "0", "type": "dimension" },
      "wide": { "value": "0.02em", "type": "dimension" },
      "wider": { "value": "0.04em", "type": "dimension" },
      "widest": { "value": "0.1em", "type": "dimension" }
    }
  },
  "borderRadius": {
    "none": { "value": "0", "type": "dimension" },
    "sm": { "value": "4px", "type": "dimension" },
    "md": { "value": "6px", "type": "dimension" },
    "lg": { "value": "8px", "type": "dimension" },
    "xl": { "value": "12px", "type": "dimension" },
    "2xl": { "value": "16px", "type": "dimension" },
    "full": { "value": "9999px", "type": "dimension" }
  },
  "shadow": {
    "none": { "value": "none", "type": "shadow" },
    "xs": { "value": "0 1px 1px 0 rgb(0 0 0 / 0.04)", "type": "shadow" },
    "sm": { "value": "0 1px 2px 0 rgb(0 0 0 / 0.05)", "type": "shadow" },
    "md": { "value": "0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)", "type": "shadow" },
    "lg": { "value": "0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)", "type": "shadow" },
    "xl": { "value": "0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)", "type": "shadow" },
    "2xl": { "value": "0 25px 50px -12px rgb(0 0 0 / 0.25)", "type": "shadow" },
    "inner": { "value": "inset 0 2px 4px 0 rgb(0 0 0 / 0.05)", "type": "shadow" }
  },
  "breakpoints": {
    "xs": { "value": "480px", "type": "dimension" },
    "sm": { "value": "640px", "type": "dimension" },
    "md": { "value": "768px", "type": "dimension" },
    "lg": { "value": "1024px", "type": "dimension" },
    "xl": { "value": "1280px", "type": "dimension" },
    "2xl": { "value": "1536px", "type": "dimension" }
  },
  "zIndex": {
    "dropdown": { "value": 100, "type": "number" },
    "sticky": { "value": 200, "type": "number" },
    "fixed": { "value": 300, "type": "number" },
    "modalBackdrop": { "value": 400, "type": "number" },
    "modal": { "value": 500, "type": "number" },
    "popover": { "value": 600, "type": "number" },
    "tooltip": { "value": 700, "type": "number" },
    "toast": { "value": 800, "type": "number" }
  },
  "transition": {
    "fast": { "value": "100ms ease", "type": "transition" },
    "normal": { "value": "200ms ease", "type": "transition" },
    "slow": { "value": "300ms ease", "type": "transition" },
    "slower": { "value": "500ms ease", "type": "transition" }
  }
}
```

---

## Usage in Code

### CSS (Recommended)
```css
.button {
  padding: var(--space-2) var(--space-4);
  background: var(--color-primary);
  color: var(--color-text-inverse);
  border-radius: var(--radius-button);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  transition: background var(--transition-fast);
}

.button:hover {
  background: var(--color-primary-hover);
}

.button:focus-visible {
  outline: 2px solid var(--color-focus-ring);
  outline-offset: 2px;
}

.button:disabled {
  background: var(--color-primary-disabled);
  cursor: not-allowed;
}
```

### With Dark Mode (Automatic)
```css
/* No extra work needed — tokens switch automatically via prefers-color-scheme */
.card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-card);
  border-radius: var(--radius-card);
}
```

### JSON Import (Style Dictionary)
```bash
# Install
npm install --save-dev style-dictionary

# Build
npx style-dictionary build --config sd.config.js
```

```js
// sd.config.js
module.exports = {
  source: ['references/token-reference.json'],
  platforms: {
    css: {
      transformGroup: 'css',
      buildPath: 'dist/tokens/',
      files: [{
        destination: 'tokens.css',
        format: 'css/variables'
      }]
    },
    scss: { /* ... */ },
    js: { /* ... */ },
    json: { /* ... */ }
  }
};
```

---

## Token Naming Conventions

| Pattern | Example | Use For |
|---------|---------|---------|
| `--color-{category}-{role}-{state}` | `--color-primary-hover` | Color states |
| `--space-{scale}` | `--space-4` | Spacing scale |
| `--font-size-{scale}` | `--font-size-xl` | Type scale |
| `--radius-{component}` | `--radius-button` | Component-specific |
| `--shadow-{component}` | `--shadow-card` | Component-specific |

**Never use:** `--color-blue-500`, `--space-16px`, `--font-size-18px` — these are magic numbers.