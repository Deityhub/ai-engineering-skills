# Portability Guide — Using Design Skill in Any AI Tool

This guide shows how to use the design-skill in **any AI tool** (Claude, Codex, Gemini, Cursor, Copilot, etc.) via the universal prompt and portable scripts.

---

## Quick Start (30 seconds)

### 1. Copy the Universal Prompt
```bash
cat universal-prompt.md
```
Copy the entire **"SYSTEM PROMPT — PASTE THIS"** section.

### 2. Paste into Your AI Tool

| Tool | Where to Paste |
|------|----------------|
| **Claude (Web)** | Settings → Custom Instructions |
| **Claude Code** | `.claude/CLAUDE.md` or `CLAUDE.md` in project root |
| **Codex** | `AGENTS.md` in repo root |
| **Gemini (API)** | `system_instruction` parameter |
| **Gemini (Web)** | Settings → System Instructions |
| **Cursor** | Cmd+Shift+P → "Cursor Settings" → Rules for AI |
| **Copilot** | `.github/copilot-instructions.md` |
| **Any CLI** | Start prompt with `System: [paste prompt]` |

### 3. Start Designing
```
Design a login page with email/password fields, submit button, and forgot password link. Output both spec and code. Use WCAG AA contrast.
```

---

## File Structure for Portability

```
design-skill/
├── universal-prompt.md          # ← COPY THIS (system prompt)
├── references/                  # ← COPY THIS FOLDER to your project
│   ├── design-principles.md
│   ├── token-reference.md
│   ├── accessibility-checklist.md
│   ├── component-patterns.md
│   ├── responsive-patterns.md
│   ├── platform-guides/
│   └── design-review-protocol.md
├── scripts/                     # ← RUN THESE ANYWHERE (Python 3.8+)
│   ├── extract-tokens.py
│   ├── audit-accessibility.py
│   ├── validate-tokens.py
│   ├── generate-component.py
│   ├── convert-to-platform.py
│   └── compress-context.py
├── assets/templates/            # ← COPY THESE FILES
│   ├── component-spec.md
│   ├── page-spec.md
│   └── design-system.json
└── PORTABILITY.md              # ← THIS FILE
```

---

## Using Scripts in Any Environment

All scripts are **standalone Python 3.8+** with no external dependencies (except `cssutils` for token extraction — install via `pip install cssutils`).

### Install Dependencies (Optional)
```bash
# Only needed for extract-tokens.py CSS parsing
pip install cssutils

# For full functionality
pip install -r requirements.txt  # (create if needed)
```

### Script Usage Examples

#### Extract Tokens from Any Project
```bash
# From CSS/Tailwind/Figma JSON
python scripts/extract-tokens.py --input ./my-project --output tokens.json

# Output as CSS custom properties
python scripts/extract-tokens.py --input ./styles --format css --output tokens.css
```

#### Audit Accessibility
```bash
# Single file
python scripts/audit-accessibility.py --file Component.tsx --format markdown

# Entire project
python scripts/audit-accessibility.py --dir ./src --output a11y-report.md

# Specific checks only
python scripts/audit-accessibility.py --file page.html --check contrast,forms --format json
```

#### Validate Token Compliance
```bash
# Check for magic numbers
python scripts/validate-tokens.py --file Component.tsx --tokens tokens.json

# Auto-fix violations
python scripts/validate-tokens.py --dir ./src --tokens tokens.json --fix --dry-run
python scripts/validate-tokens.py --dir ./src --tokens tokens.json --fix
```

#### Generate Components
```bash
# From spec (interactive)
python scripts/generate-component.py --interactive --framework react --output ./src/components

# From spec file
python scripts/generate-component.py --spec assets/templates/component-spec.md --framework vue --output ./src/components
```

#### Convert Between Platforms
```bash
# Single file
python scripts/convert-to-platform.py --input Button.tsx --from react --to swiftui --output Button.swift

# Entire directory
python scripts/convert-to-platform.py --dir ./src/components --from react --to flutter --output ./lib/components
```

#### Compress Context for Handoff
```bash
# From review report
python scripts/compress-context.py --input review-report.md --output handoff.md --max-tokens 2000

# Token diff
python scripts/compress-context.py --input new-tokens.json --diff old-tokens.json --output token-changes.md
```

---

## Platform-Specific Setup

### Claude Code
```bash
# Option 1: Project-level (recommended)
cp universal-prompt.md .claude/CLAUDE.md
cp -r references .claude/references

# Option 2: User-level
cp universal-prompt.md ~/.claude/CLAUDE.md
```

**Usage:**
```bash
# In any project with the skill loaded
> Design a checkout form with email, card, expiry, CVC. Output both.

# With existing tokens
> Here are my tokens: @.claude/references/token-reference.md
> Review this Button component: @src/components/Button.tsx
```

### Codex
```bash
# Repo-level
cp universal-prompt.md AGENTS.md
cp -r references .codex/references

# Run scripts in Codex terminal
codex exec python scripts/audit-accessibility.py --dir ./src
```

### Gemini (API)
```python
import google.generative as genai

with open("universal-prompt.md") as f:
    prompt = f.read()
    # Extract system prompt section
    system_prompt = prompt.split("SYSTEM PROMPT — PASTE THIS")[1].split("---")[0]

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    system_instruction=system_prompt
)

response = model.generate_content("Design a login page...")
```

### Cursor
```json
// .cursor/rules/design-skill.mdc
---
description: "Design system and accessibility rules"
globs: ["**/*.tsx", "**/*.vue", "**/*.css", "**/*.html"]
alwaysApply: true
---

[PASTE UNIVERSAL PROMPT HERE]
```

### Copilot
```markdown
<!-- .github/copilot-instructions.md -->
[PASTE UNIVERSAL PROMPT HERE]
```

---

## Working with Existing Projects

### 1. Extract Existing Tokens
```bash
python scripts/extract-tokens.py --input ./my-project --output project-tokens.json
```

### 2. Share Tokens with AI
```markdown
# In your prompt
Here are my project's design tokens:
```json
[paste project-tokens.json]
```
Use these tokens. Review this component for accessibility and consistency: [paste code]
```

### 3. Validate Against Project Tokens
```bash
python scripts/validate-tokens.py --dir ./src --tokens project-tokens.json --output compliance-report.md
```

---

## Agentic Workflow (Multi-Agent)

For tools supporting subagents (Claude Code, custom setups):

```bash
# 1. Coordinator creates brief
python scripts/compress-context.py --session ./design-session --output brief.md

# 2. Spawn parallel validation agents
# Agent A: Accessibility
python scripts/audit-accessibility.py --dir ./src --output a11y.md

# Agent B: Token Compliance
python scripts/validate-tokens.py --dir ./src --tokens tokens.json --output tokens.md

# Agent C: Responsive
python scripts/audit-accessibility.py --dir ./src --check responsive --output responsive.md

# 3. Coordinator builds consensus
python scripts/compress-context.py --input a11y.md --input tokens.md --input responsive.md --output consensus.md
```

---

## Requirements

| Requirement | Version |
|-------------|---------|
| Python | 3.8+ |
| cssutils | 2.4+ (for `extract-tokens.py` only) |
| Standard library | json, re, pathlib, argparse, dataclasses |

**No Node.js, no build tools, no framework dependencies.**

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `cssutils` not found | `pip install cssutils` |
| Scripts not executable | `chmod +x scripts/*.py` |
| Python version error | Use `python3` explicitly |
| Token diff empty | Ensure both files have same structure |
| Large output truncated | Increase `--max-tokens` |

---

## File Formats Supported

### Input (extract-tokens.py)
- `.css`, `.scss`, `.sass` — CSS custom properties
- `tailwind.config.js/ts/json` — Tailwind theme
- `figma-tokens.json`, `tokens.json` — Figma Tokens / Style Dictionary

### Output (extract-tokens.py)
- `.json` — Style Dictionary compatible
- `.css` — CSS custom properties (`:root { --token: value; }`)

### Validation (validate-tokens.py)
- `.tsx`, `.jsx`, `.ts`, `.js` — React/Vue/JS
- `.vue` — Vue SFC
- `.css`, `.scss` — Stylesheets

### Generation (generate-component.py)
- React (`.tsx` + `.css`)
- Vue (`.vue`)
- HTML (`.html`)
- SwiftUI (`.swift`)
- Flutter (`.dart`)

### Conversion (convert-to-platform.py)
- React ↔ Vue ↔ HTML ↔ SwiftUI ↔ Flutter ↔ React Native

---

## License

MIT — Use freely in any project, commercial or personal.

---

## Support

- **Issues**: Report via GitHub Issues
- **Discussions**: GitHub Discussions
- **Docs**: See `references/` for detailed specifications