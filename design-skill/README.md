# Design Skill — Production-Grade Design System & Accessibility Skill

A **universal, tool-agnostic** design skill for creating accessible, consistent, performant UIs across web, mobile, and cross-platform contexts. Works in **Goose (native)**, **Claude Code**, **Codex**, **Gemini**, **Cursor**, **Copilot**, and **any AI tool** via the portable system prompt.

---

## 🎯 What This Skill Does

| Capability | Description |
|------------|-------------|
| **Design Generation** | Create specs + code for components, pages, design systems |
| **Accessibility Audit** | WCAG 2.1 AA compliance checking (automated + manual) |
| **Token Management** | Extract, validate, convert design tokens (CSS, Tailwind, Figma, JSON) |
| **Cross-Platform** | Generate React, Vue, HTML, SwiftUI, Flutter, React Native from single spec |
| **Agentic Delegation** | Parallel validation agents with consensus protocol |
| **Context Compression** | Efficient handoff between agents/sessions |

---

## 🚀 Quick Start

### Goose (Native)
```bash
load_skill("design-skill")
# Then: "Design a login page with email/password, submit button, forgot password link. Output both spec and code."
```

### Any Other AI Tool
```bash
# 1. Copy the universal prompt
cat universal-prompt.md
# Paste the "SYSTEM PROMPT — PASTE THIS" section into your tool's system instructions

# 2. Copy references folder to your project
cp -r references /your/project/.design-skill/

# 3. Start designing
"Design a checkout form with email, card, expiry, CVC. Output both spec and code."
```

---

## 📁 Folder Structure

```
design-skill/
├── SKILL.md                      # Goose native manifest
├── universal-prompt.md           # 📋 COPY THIS for any AI tool
├── PORTABILITY.md                # Tool-specific setup guide
├── references/                   # 📚 Portable reference docs
│   ├── design-principles.md      # Condensed core principles
│   ├── token-reference.md        # Complete CSS + JSON token system
│   ├── accessibility-checklist.md # WCAG AA + gaps checklist
│   ├── component-patterns.md     # Atomic design primitives
│   ├── responsive-patterns.md    # Breakpoints, fluid type
│   ├── platform-guides/          # iOS, Android, Flutter, SwiftUI
│   └── design-review-protocol.md # Multi-agent validation
├── scripts/                      # 🛠 Deterministic Python scripts
│   ├── extract-tokens.py         # CSS/Tailwind/Figma → canonical tokens
│   ├── audit-accessibility.py    # WCAG violation scanner
│   ├── validate-tokens.py        # Magic number detector + auto-fix
│   ├── generate-component.py     # Spec → React/Vue/HTML/SwiftUI/Flutter
│   ├── convert-to-platform.py    # Cross-platform component conversion
│   └── compress-context.py       # Design decision summarization
├── assets/templates/             # 📄 Starter templates
│   ├── component-spec.md
│   ├── page-spec.md
│   └── design-system.json
├── evals/                        # 🧪 Test cases (add your own)
└── LICENSE.txt
```

---

## ✨ Key Features

### 1. Complete Design Token System
- **Spacing**: 8px base grid (4–64px)
- **Color**: Semantic + functional + state + **dark mode for all**
- **Typography**: Modular scale (1.25 ratio), 12px–60px
- **Radius/Shadow/Breakpoints/Z-index/Transitions**
- **JSON export** for Style Dictionary, Figma Tokens, Specify

### 2. WCAG 2.1 AA + Gaps Addressed
- ✅ Contrast ratios (4.5:1/3:1)
- ✅ Keyboard focus + visible focus rings
- ✅ Semantic HTML + ARIA
- ✅ **Skip links, landmarks, text spacing overrides**
- ✅ **Icon accessibility, RTL logical properties**
- ✅ **Reduced motion, touch targets (44/48/44pt)**
- ✅ **Dark mode token counterparts**

### 3. Atomic Component Library
| Level | Components |
|-------|------------|
| Atoms | Button, Input, Badge, Avatar, Icon, Typography, Spacer |
| Molecules | FormField, Card, Dropdown, Toast, Modal |
| Organisms | Header, Footer, Sidebar, DataTable, SearchResults |
| Templates | PageLayout |

### 4. Cross-Platform Generation
```bash
# One spec → 6 platforms
python scripts/generate-component.py --spec button-spec.md --framework react
python scripts/generate-component.py --spec button-spec.md --framework swiftui
python scripts/generate-component.py --spec button-spec.md --framework flutter
```

### 5. Deterministic Scripts (Run Anywhere)
```bash
# Extract tokens from any codebase
python scripts/extract-tokens.py --input ./my-project --output tokens.json

# Audit accessibility
python scripts/audit-accessibility.py --dir ./src --output report.md

# Validate token compliance (auto-fix!)
python scripts/validate-tokens.py --dir ./src --tokens tokens.json --fix

# Convert between platforms
python scripts/convert-to-platform.py --dir ./components --from react --to flutter --output ./lib
```

### 6. Agentic Delegation Ready
```bash
# Parallel validation agents
python scripts/audit-accessibility.py --dir ./src --check contrast,forms &
python scripts/validate-tokens.py --dir ./src --tokens tokens.json &
python scripts/audit-accessibility.py --dir ./src --check responsive &

# Consensus + handoff
python scripts/compress-context.py --session ./design-review --output handoff.md
```

---

## 🛠 Scripts Reference

| Script | Purpose | Input | Output |
|--------|---------|-------|--------|
| `extract-tokens.py` | Parse CSS/Tailwind/Figma → canonical tokens | Files/dir | `tokens.json` or `tokens.css` |
| `audit-accessibility.py` | Scan for WCAG violations | Files/dir | Markdown/JSON report |
| `validate-tokens.py` | Find magic numbers, suggest tokens | Files/dir + tokens | Report + optional auto-fix |
| `generate-component.py` | Spec → component code (6 frameworks) | Spec markdown | Component files |
| `convert-to-platform.py` | Transform component between platforms | Component files | Converted component files |
| `compress-context.py` | Summarize design decisions for handoff | Reports/tokens | Compressed markdown |

---

## 📋 Templates

| Template | Use For |
|----------|---------|
| `component-spec.md` | New component specifications |
| `page-spec.md` | Page/layout specifications |
| `design-system.json` | Complete design system (Style Dictionary compatible) |

---

## 🔧 Requirements

- **Python 3.8+** (scripts)
- **cssutils** `pip install cssutils` (for `extract-tokens.py` CSS parsing)
- **No Node.js, no build tools, no framework deps**

---

## 📖 Documentation

| File | Contents |
|------|----------|
| `universal-prompt.md` | Complete system prompt + token reference + usage |
| `references/design-principles.md` | 5 core principles condensed |
| `references/token-reference.md` | Full CSS + JSON token system |
| `references/accessibility-checklist.md` | WCAG AA checklist with fixes |
| `references/component-patterns.md` | Atomic components + props API |
| `references/responsive-patterns.md` | Breakpoints, fluid type, layouts |
| `references/platform-guides/` | iOS, Android, Flutter, SwiftUI mappings |
| `references/design-review-protocol.md` | Multi-agent validation workflow |
| `PORTABILITY.md` | Tool-specific setup (Claude, Codex, Gemini, Cursor, Copilot) |

---

## 🧪 Adding Test Cases

Create eval cases in `evals/`:

```
evals/
├── login-page-design/
│   ├── prompt.md
│   ├── case.yaml
│   └── files/
├── button-accessibility/
├── token-compliance/
├── dark-mode-tokens/
└── responsive-breakpoints/
```

Run with Goose's eval system or manually test.

---

## 🤝 Contributing

1. Fork the skill
2. Add scripts/references/templates
3. Add eval cases
4. Test in multiple AI tools
5. Submit PR

---

## 📄 License

MIT — See `LICENSE.txt`

---

## 🙏 Acknowledgments

- WCAG 2.1 AA (W3C)
- Design Tokens Community Group (W3C)
- Material Design 3 (Google)
- Human Interface Guidelines (Apple)
- Atomic Design (Brad Frost)
- Style Dictionary (Amazon)
- Figma Tokens Plugin