# Design Review Protocol — Multi-Agent Validation

**Structured protocol for parallel agent validation of design work.** Ensures consistent, thorough reviews when delegating to multiple agents.

---

## When to Use This Protocol

- Reviewing a design system or component library
- Auditing an existing codebase for accessibility/consistency
- Validating new component implementations
- Cross-platform design handoffs
- Pre-release design quality gates

---

## Review Phases

### Phase 1: Context Distribution (Coordinator Agent)
```markdown
## Design Review Brief

**Scope**: [What is being reviewed — components, pages, system]
**Context**: [Project tokens, existing patterns, constraints]
**Deliverables Expected**: [Checklist findings, corrected snippets, priority list]
**Deadline**: [Timebox]

**Files to Review**:
- [ ] `tokens.css` / `tailwind.config.js` / `figma-tokens.json`
- [ ] `components/Button.tsx`
- [ ] `components/FormField.tsx`
- [ ] `pages/Dashboard.tsx`

**Reference Standards**:
- WCAG 2.1 AA (`references/accessibility-checklist.md`)
- Design tokens (`references/token-reference.md`)
- Component patterns (`references/component-patterns.md`)
- Platform guides (`references/platform-guides/`)
```

### Phase 2: Parallel Validation (Worker Agents)

Each agent receives the brief + subset of files. Agents run **deterministic scripts** + **qualitative review**.

#### Agent A: Accessibility Audit
```bash
# Deterministic checks
python scripts/audit-accessibility.py --dir ./components --output a11y-report.md

# Qualitative review
# - Focus management in modals/drawers
# - Screen reader flow (manual test)
# - Keyboard navigation completeness
# - ARIA usage correctness
```

#### Agent B: Design System Compliance
```bash
# Deterministic checks
python scripts/validate-tokens.py --dir ./components --tokens tokens.json --output token-report.md

# Qualitative review
# - Token usage consistency
# - Component variant completeness
# - Naming convention adherence
# - Presentational/container separation
```

#### Agent C: Responsive & Performance
```bash
# Deterministic checks
python scripts/audit-accessibility.py --dir ./pages --check responsive --output responsive-report.md

# Qualitative review
# - Breakpoint behavior
# - Fluid typography
# - Image optimization (dimensions, lazy loading, formats)
# - CLS prevention
# - Animation performance
```

#### Agent D: Cross-Platform Parity (if applicable)
```bash
# Qualitative review
# - iOS: safe areas, Dynamic Type, 44pt targets
# - Android: 48dp targets, Material tokens, size classes
# - Flutter: layout constraints, text scaling
# - Web: progressive enhancement
```

### Phase 3: Consensus Building (Coordinator Agent)

```markdown
## Consensus Meeting Template

### Findings Summary

| Agent | Category | Critical | Major | Minor | Total |
|-------|----------|----------|-------|-------|-------|
| A | Accessibility | 2 | 5 | 3 | 10 |
| B | Design System | 0 | 3 | 8 | 11 |
| C | Responsive/Perf | 1 | 2 | 4 | 7 |
| D | Cross-Platform | 0 | 4 | 2 | 6 |

### Conflicts to Resolve

| Issue | Agent A View | Agent B View | Resolution |
|-------|--------------|--------------|------------|
| Button focus ring width | 3px (a11y) | 2px (design) | 3px — a11y wins |
| Token naming | `--space-4` | `--space-md` | Use both (alias) |

### Priority Actions (Consensus Order)

1. 🔴 **Critical Accessibility**: Fix focus rings, add skip links
2. 🔴 **Critical Responsive**: Dashboard breaks at 320px
3. 🟡 **Design System**: 12 components use magic numbers
4. 🟡 **Cross-Platform**: iOS safe areas missing on 3 screens
5. 🟢 **Polish**: Inconsistent transition durations
```

---

## Validation Checklists per Agent

### Agent A: Accessibility Checklist
```markdown
- [ ] All interactive elements have visible focus rings (≥2px, 3:1 contrast)
- [ ] Skip link present and functional
- [ ] Heading hierarchy logical (no skipped levels)
- [ ] All images have appropriate alt text
- [ ] Form fields have associated labels (not placeholder-only)
- [ ] Error messages linked via aria-describedby + aria-invalid + aria-live
- [ ] Modals trap focus, Escape closes, focus returns to trigger
- [ ] No keyboard traps
- [ ] Touch targets ≥44×44px (web) / 48×48dp (Android) / 44×44pt (iOS)
- [ ] Reduced motion respected
- [ ] Color not sole indicator of state
- [ ] Text spacing overrides supported
- [ ] RTL: logical properties used
- [ ] Page has lang attribute and title
- [ ] Landmarks: header, nav, main, aside, footer
```

### Agent B: Design System Checklist
```markdown
- [ ] Zero magic numbers (all spacing, color, type, radius, shadow via tokens)
- [ ] Color system complete: semantic + functional + state + dark mode
- [ ] Type scale used consistently (no arbitrary font-sizes)
- [ ] Spacing follows 8px base grid
- [ ] Border radius tokens used
- [ ] Shadow tokens used
- [ ] Component names: PascalCase, descriptive
- [ ] Props: variant, size, disabled, loading (consistent)
- [ ] Presentational vs container separation
- [ ] Component variants documented
- [ ] JSON token export available
- [ ] Aligns with existing project conventions
```

### Agent C: Responsive/Performance Checklist
```markdown
- [ ] Layout works at 320px, 768px, 1024px, 1440px+
- [ ] Mobile-first media queries (min-width)
- [ ] Fluid typography via clamp() where appropriate
- [ ] No hover-only interactions without touch alternative
- [ ] Images: width/height defined, lazy-loaded, WebP/AVIF
- [ ] No layout shift (CLS): space reserved for images/fonts
- [ ] CSS over JS for animations
- [ ] No heavy CSS-in-JS unless required
- [ ] Font-display: swap for web fonts
- [ ] Critical CSS inlined
```

### Agent D: Cross-Platform Checklist
```markdown
iOS:
- [ ] Safe area insets respected (env(safe-area-inset-*))
- [ ] Dynamic Type supported (all text scales)
- [ ] 44×44pt minimum touch targets
- [ ] Reduce motion respected

Android:
- [ ] 48×48dp minimum touch targets
- [ ] Material Design tokens considered
- [ ] Window size classes handled (COMPACT/MEDIUM/EXPANDED)
- [ ] RTL layouts tested

Flutter:
- [ ] LayoutBuilder breakpoints used
- [ ] Text scaling works (textScaleFactor)
- [ ] 48×48dp touch targets
- [ ] High contrast mode works

Web (Progressive Enhancement):
- [ ] Works without JS (core content)
- [ ] Works without CSS (semantic HTML)
- [ ] Graceful degradation for unsupported features
```

---

## Dispute Resolution

| Conflict Type | Resolution Rule |
|---------------|-----------------|
| Accessibility vs Design | **Accessibility wins** — WCAG is non-negotiable |
| Performance vs Features | **Performance wins** if Core Web Vitals fail |
| Consistency vs Innovation | **Consistency wins** for system components; innovation allowed for new patterns with review |
| Platform vs Unity | **Platform conventions win** for native feel; unify only shared logic |

---

## Output Format

Each agent produces:
```markdown
# Agent [Letter] Review: [Component/Page]

## Summary
- **Critical**: N
- **Major**: N
- **Minor**: N
- **Pass**: N

## Findings

### 🔴 Critical
1. **Issue**: [Description]
   **Location**: [File:line]
   **Standard**: [WCAG/Token/Reference]
   **Fix**: [Corrected snippet]

### 🟡 Major
...

### 🟢 Minor
...

## Script Output
[Paste deterministic script results]

## Qualitative Notes
[Observations not caught by scripts]
```

Coordinator produces:
```markdown
# Design Review Consensus: [Scope]

## Executive Summary
[2-3 sentences]

## Priority Actions
1. [Action] — Owner: [Agent] — Due: [Date]
2. ...

## Resolved Conflicts
[Table]

## Waived Items (with justification)
[List]

## Sign-off
- Agent A (Accessibility): ✅ / ❌
- Agent B (Design System): ✅ / ❌
- Agent C (Responsive/Perf): ✅ / ❌
- Agent D (Cross-Platform): ✅ / ❌
- Coordinator: ✅ / ❌
```

---

## Automation Integration

```python
# scripts/design-review-coordinator.py
# Orchestrates parallel agent reviews

async def run_design_review(scope: ReviewScope):
    # 1. Distribute context
    brief = create_brief(scope)

    # 2. Spawn parallel agents
    tasks = [
        run_agent("accessibility", brief, scope.files),
        run_agent("design-system", brief, scope.files),
        run_agent("responsive", brief, scope.files),
        run_agent("cross-platform", brief, scope.files),
    ]

    results = await asyncio.gather(*tasks)

    # 3. Build consensus
    consensus = build_consensus(results)

    # 4. Generate report
    generate_report(consensus, scope.output_path)

    return consensus
```

---

## Context Compression for Handoff

Use `scripts/compress-context.py` to summarize review for next phase:

```bash
python scripts/compress-context.py \
  --input consensus-report.md \
  --output handoff-summary.md \
  --max-tokens 2000
```

Output includes:
- Token diff (what changed)
- Critical fixes applied
- Remaining known issues
- Component spec updates
- Next review focus areas