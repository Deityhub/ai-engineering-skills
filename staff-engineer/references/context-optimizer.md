# Context Optimizer — Staff Engineer Reference

**Minimize token usage while maximizing relevance.** Core superpower for agentic workflows.

---

## The Problem

```
Typical codebase: 100K-10M lines
Context window: 8K-200K tokens
Relevant code for task: ~1-5% of codebase

Naive approach: Stuff everything → Token overflow, noise, hallucination
Smart approach: Progressive disclosure + relevance scoring → Focus, accuracy, speed
```

---

## Progressive Disclosure Levels

### L1: Metadata (Always Loaded, ~500 tokens)
```
Project Structure:
├── packages/
│   ├── billing/ (15 files, 3.2K LOC, complexity: 8.2)
│   ├── inventory/ (12 files, 2.8K LOC, complexity: 6.5)
│   └── shared/ (8 files, 1.1K LOC, complexity: 4.1)
├── apps/
│   ├── api-gateway/ (5 files, 800 LOC)
│   └── worker/ (3 files, 450 LOC)
└── tests/ (200 files, 15K LOC)

Key Metrics:
- Total: 42 files, 8.3K LOC (prod), 15K LOC (tests)
- Languages: TypeScript (95%), SQL (5%)
- Frameworks: NestJS, Prisma, Redis, Kafka
- Test coverage: 78% (unit), 45% (integration)
- Hotspots: billing/pricing.ts (CC: 24), inventory/allocation.ts (CC: 18)
- Recent changes (7d): billing/ (12 commits), inventory/ (3 commits)
```

### L2: Signatures (On Demand, ~2K tokens)
```typescript
// billing/pricing.ts (public API only)
export interface PricingEngine {
  calculate(order: Order, context: PricingContext): Promise<PriceBreakdown>;
  applyDiscount(price: PriceBreakdown, discount: Discount): PriceBreakdown;
  validatePricingRules(order: Order): ValidationResult;
}

export interface PricingContext {
  customerId: string;
  currency: Currency;
  tier: CustomerTier;
  promotions: Promotion[];
  timestamp: Date;
}

export interface PriceBreakdown {
  subtotal: Money;
  discounts: DiscountApplication[];
  taxes: TaxBreakdown[];
  shipping: Money;
  total: Money;
}

// ... 15 more interfaces, types, enums
// NO implementations shown
```

### L3: Implementations (Task-Specific, ~5K tokens)
```typescript
// billing/pricing.ts - calculate() implementation (ranked #1 for "pricing discount bug")
async calculate(order: Order, context: PricingContext): Promise<PriceBreakdown> {
  // 1. Validate input
  const validation = this.validatePricingRules(order);
  if (!validation.valid) throw new PricingError(validation.errors);

  // 2. Base price
  let subtotal = order.items.reduce((sum, item) => sum + item.price * item.quantity, Money.zero(context.currency));

  // 3. Apply promotions (RELEVANT: discount bug reported here)
  const promotions = await this.promotionService.getActive(context.customerId, context.tier);
  const { subtotal: discounted, applied } = this.applyPromotions(subtotal, promotions, order);
  
  // 4. Calculate taxes
  const taxes = await this.taxService.calculate(discounted, context);
  
  // 5. Shipping
  const shipping = await this.shippingService.calculate(order, context);
  
  return { subtotal: discounted, discounts: applied, taxes, shipping, total: discounted + taxes + shipping };
}
```

### L4: History (Debugging, ~1K tokens)
```
Recent Changes (billing/pricing.ts):
├── 2024-01-15: feat: add tier-based pricing (abc123) - by @jane
├── 2024-01-10: fix: discount stacking order (def456) - by @john  ← RELEVANT
├── 2024-01-05: refactor: extract promotion service (ghi789) - by @jane
├── 2024-01-02: test: add pricing edge cases (jkl012) - by @bob

Related Commits:
- def456: "fix: discount stacking order" - Modified applyPromotions() logic
- abc123: "feat: add tier-based pricing" - Added tier to PricingContext
```

---

## Relevance Scoring Algorithm

### Formula
```
RelevanceScore = (SemanticSimilarity × 0.40) 
               + (RecencyWeight × 0.20) 
               + (ChangeFrequency × 0.20) 
               + (DependencyCentrality × 0.20)
```

### Component Details

#### 1. Semantic Similarity (0-1)
```
Task: "Fix discount calculation bug for premium users"

Vector Search (embeddings):
- billing/pricing.ts:calculate()     → 0.92  (direct match)
- billing/promotion.service.ts       → 0.87  (promotions)
- billing/pricing.test.ts            → 0.76  (tests)
- inventory/allocation.ts            → 0.12  (unrelated)
- shared/utils/date.ts               → 0.05  (utility)
```

#### 2. Recency Weight (0-1)
```
File last modified:
- Today          → 1.0
- This week      → 0.8
- This month     → 0.5
- This quarter   → 0.3
- Older          → 0.1
```

#### 3. Change Frequency (Churn) (0-1)
```
Commits in last 90 days:
- 20+ commits    → 1.0 (hotspot)
- 10-19 commits  → 0.7
- 5-9 commits    → 0.5
- 1-4 commits    → 0.3
- 0 commits      → 0.1 (stable)
```

#### 4. Dependency Centrality (0-1)
```
Dependents (files that import this):
- 50+ files      → 1.0 (core library)
- 20-49 files    → 0.8
- 10-19 files    → 0.6
- 5-9 files      → 0.4
- 1-4 files      → 0.2
- 0 files        → 0.1 (leaf)
```

### Example Calculation
```
Task: "Fix discount bug for premium users"

billing/pricing.ts:
- Semantic: 0.92 × 0.40 = 0.368
- Recency: 0.80 × 0.20 = 0.160 (modified this week)
- Churn: 0.70 × 0.20 = 0.140 (12 commits/90d)
- Centrality: 0.60 × 0.20 = 0.120 (18 dependents)
- TOTAL: 0.788 → RANK #1

billing/promotion.service.ts:
- Semantic: 0.87 × 0.40 = 0.348
- Recency: 0.50 × 0.20 = 0.100 (modified this month)
- Churn: 0.50 × 0.20 = 0.100 (7 commits/90d)
- Centrality: 0.40 × 0.20 = 0.080 (8 dependents)
- TOTAL: 0.628 → RANK #2
```

---

## Context Compression Techniques

### 1. File Summarization
```python
def summarize_file(file_path: Path, max_tokens: int = 500) -> str:
    """
    Produce: Purpose + Public API + Key Algorithms + Dependencies
    """
    # Parse AST
    tree = parse_ast(file_path)
    
    summary = []
    summary.append(f"# {file_path.name}")
    summary.append(f"**Purpose**: {extract_purpose(tree)}")
    summary.append(f"**Public API**: {extract_public_api(tree)}")
    summary.append(f"**Key Algorithms**: {extract_key_algorithms(tree)}")
    summary.append(f"**Dependencies**: {extract_dependencies(tree)}")
    summary.append(f"**Complexity**: CC={cyclomatic_complexity(tree)}, Cognitive={cognitive_complexity(tree)}")
    
    # Truncate to token budget
    return truncate_to_tokens('\n'.join(summary), max_tokens)
```

### 2. Git History Compression
```python
def compress_git_history(file_path: Path, max_commits: int = 10) -> str:
    """
    Conventional commits → ADR-linked changes
    """
    commits = get_recent_commits(file_path, limit=100)
    
    # Group by type
    grouped = defaultdict(list)
    for commit in commits:
        commit_type = parse_conventional_type(commit.message)  # feat, fix, refactor, test
        grouped[commit_type].append(commit)
    
    # Summarize
    summary = []
    for commit_type, commits in grouped.items():
        summary.append(f"## {commit_type.title()} ({len(commits)})")
        for c in commits[:max_commits]:
            summary.append(f"- {c.short_sha}: {c.subject} (@{c.author})")
            if c.linked_adr:
                summary.append(f"  ↳ ADR-{c.linked_adr}")
    
    return '\n'.join(summary)
```

### 3. Pattern Deduplication
```python
def deduplicate_patterns(files: List[FileAnalysis]) -> List[Pattern]:
    """
    Find repeated code patterns across files
    """
    patterns = []
    
    # Extract n-grams from ASTs
    for file in files:
        ngrams = extract_ast_ngrams(file.ast, n=5)
        for ng in ngrams:
            patterns.append(Pattern(
                signature=hash_ast(ng),
                locations=[file.path],
                frequency=1
            ))
    
    # Merge duplicates
    merged = merge_by_signature(patterns)
    
    # Return top patterns (frequency > 1)
    return [p for p in merged if p.frequency > 1]

# Output example:
# Pattern: "Repository findById pattern" (frequency: 12)
#   Locations: billing/repo.ts, inventory/repo.ts, user/repo.ts, ...
#   Template: async findById(id: string) { return this.db.findUnique({ where: { id } }); }
```

### 4. Directory Pruning
```python
PRUNE_PATTERNS = [
    'node_modules/**',
    'dist/**', 'build/**', 'out/**',
    '.git/**',
    'coverage/**',
    '*.test.ts', '*.spec.ts', '__tests__/**',  # Unless testing task
    '*.md',  # Unless docs task
    '*.config.*',  # Unless config task
    'vendor/**',
    'target/**',
]

def should_prune(path: Path, task_type: TaskType) -> bool:
    if task_type == TaskType.TESTING:
        return any(fnmatch(path, p) for p in PRUNE_PATTERNS if 'test' not in p)
    return any(fnmatch(path, p) for p in PRUNE_PATTERNS)
```

---

## Token Budget Management

### Budget Allocation
```
Total Context: 100,000 tokens (example)

Allocation:
├── System Prompt:           8,000  (8%)
├── Project Metadata (L1):   2,000  (2%)
├── Task Context:            5,000  (5%)
├── Relevant Files (L2/L3): 70,000  (70%)
├── History (L4):           5,000  (5%)
├── Scratchpad/Reasoning:   5,000  (5%)
└── Output Buffer:          5,000  (5%)

Dynamic adjustment:
- If task is "debug":     Increase History to 15%, reduce Files to 60%
- If task is "refactor":  Increase Files to 80%, reduce History to 2%
- If task is "greenfield": Increase Metadata to 10%, reduce Files to 60%
```

### Token Counting
```python
def estimate_tokens(text: str) -> int:
    """Rough estimation: words × 1.3 (varies by model)"""
    return int(len(text.split()) * 1.3)

def truncate_to_tokens(text: str, max_tokens: int) -> str:
    """Truncate preserving structure (headings, code blocks)"""
    lines = text.split('\n')
    current_tokens = 0
    result = []
    
    for line in lines:
        line_tokens = estimate_tokens(line)
        if current_tokens + line_tokens > max_tokens:
            result.append(f"\n... [truncated {len(lines) - len(result)} lines]")
            break
        result.append(line)
        current_tokens += line_tokens
    
    return '\n'.join(result)
```

---

## Agent Handoff Protocol

### Compression for Subagents
```python
def compress_for_agent(task: Task, context: Context, max_tokens: int = 3000) -> AgentBrief:
    """
    Produce minimal brief for subagent
    """
    brief = AgentBrief(
        task_id=task.id,
        objective=task.objective,
        constraints=task.constraints,
        relevant_files=select_top_files(context.files, task, max_tokens * 0.6),
        key_decisions=context.decisions[:5],
        known_risks=context.risks[:3],
        success_criteria=task.success_criteria,
        token_budget=max_tokens,
    )
    return brief
```

### Brief Format (Markdown)
```markdown
# Agent Brief: Fix Discount Calculation Bug

## Objective
Fix discount stacking bug affecting premium users (reported in #1234)

## Constraints
- Must not break existing discounts for basic users
- Maintain backward compatibility
- No performance regression (>5%)

## Relevant Files (Top 5)
1. `billing/pricing.ts` (score: 0.79) - Main calculation logic
2. `billing/promotion.service.ts` (score: 0.63) - Promotion application
3. `billing/pricing.test.ts` (score: 0.45) - Existing tests
4. `shared/types/pricing.ts` (score: 0.31) - Type definitions
5. `billing/discount.strategy.ts` (score: 0.28) - Discount strategies

## Key Decisions
- ADR-003: Tier-based pricing model (premium gets stacking)
- Discount order: percentage → fixed → shipping

## Known Risks
- Premium users currently get double discount (bug)
- Basic users might lose valid discounts if fix is wrong
- Promotion service has no tests (tech debt)

## Success Criteria
- All existing tests pass
- New test covers premium stacking scenario
- Manual verification: premium order $100 → 20% + $10 = $70 (not $60)
- Performance: <5% latency increase
```

---

## Implementation: optimize-context.py

```python
# scripts/optimize-context.py
"""
Usage:
  python scripts/optimize-context.py --task "fix discount bug" --max-tokens 10000
  python scripts/optimize-context.py --session ./feature-x --output context.md
"""

class ContextOptimizer:
    def __init__(self, repo_path: Path):
        self.repo = repo_path
        self.embeddings = EmbeddingModel()  # Sentence transformers or API
        self.git = GitRepo(repo_path)
    
    def optimize(self, task: str, max_tokens: int = 10000) -> OptimizedContext:
        # 1. Build file index with metadata
        files = self._index_files()
        
        # 2. Score relevance
        scored = self._score_relevance(files, task)
        
        # 3. Select files within budget
        selected = self._select_files(scored, max_tokens)
        
        # 4. Determine disclosure level per file
        for file in selected:
            file.disclosure_level = self._determine_level(file, task)
        
        # 5. Generate output
        return OptimizedContext(
            task=task,
            metadata=self._get_metadata(),
            files=selected,
            git_summary=self._compress_git(selected),
            token_count=sum(f.tokens for f in selected)
        )
    
    def _determine_level(self, file: ScoredFile, task: str) -> DisclosureLevel:
        if file.score > 0.7: return DisclosureLevel.L3_IMPLEMENTATION
        if file.score > 0.4: return DisclosureLevel.L2_SIGNATURES
        return DisclosureLevel.L1_METADATA
```

---

## Best Practices Summary

| Practice | Impact |
|----------|--------|
| **Always start with L1 metadata** | Orients agent, ~500 tokens |
| **Use embeddings for semantic search** | Finds relevant code without keywords |
| **Weight recency + churn + centrality** | Surfaces hotspots, recent changes |
| **Summarize, don't truncate** | Preserves structure, intent |
| **Deduplicate patterns** | Reduces noise, highlights conventions |
| **Compress git to ADR-linked changes** | Connects code to decisions |
| **Prune aggressively** | Removes node_modules, tests, docs unless needed |
| **Budget per disclosure level** | Predictable token usage |
| **Agent briefs ≤ 3000 tokens** | Focused subagents, less hallucination |