# Architecture Principles — Staff Engineer Reference

**Language-agnostic architectural governance.** Enforce via `scripts/analyze-architecture.py`.

---

## Foundational Principles

### 1. Dependency Rule (The Prime Directive)
```
Source code dependencies MUST point INWARD toward higher-level policies.
Inner layers know nothing of outer layers.
```

```
┌─────────────────────────────────────────────┐
│            DOMAIN LAYER                     │  ← Enterprise Business Rules
│  Entities, Value Objects, Domain Events     │     (Pure, testable, no deps)
├─────────────────────────────────────────────┤
│           APPLICATION LAYER                 │  ← Application Business Rules
│  Use Cases, Commands, Queries, Handlers     │     (Orchestrates domain)
├─────────────────────────────────────────────┤
│         INTERFACE ADAPTERS                  │  ← Controllers, Gateways, Presenters
│  REST Controllers, GraphQL Resolvers,       │     (Converts external → internal)
│  Repository Implementations, DTOs           │
├─────────────────────────────────────────────┤
│          FRAMEWORKS & DRIVERS               │  ← Tools, Frameworks, External
│  Database, Web Framework, HTTP Client,      │     (Details, replaceable)
│  Message Queue, Cache, Auth Provider        │
└─────────────────────────────────────────────┘
```

**Enforcement**: `scripts/analyze-architecture.py --layers domain,application,adapters,frameworks`

### 2. Boundaries Are Explicit
| Boundary | Mechanism | Example |
|----------|-----------|---------|
| **Module** | Package/workspace boundaries, `index.ts` exports | `packages/billing/src/index.ts` |
| **Layer** | Import rules (ESLint, ArchUnit, import-linter) | `domain` cannot import `adapters` |
| **Service** | API contracts (OpenAPI, Protobuf, AsyncAPI) | `billing-api.yaml` |
| **Team** | Code ownership (CODEOWNERS), repo boundaries | `@team-billing` owns `packages/billing` |

### 3. Coupling & Cohesion Metrics

| Metric | Good | Warning | Critical | Tool |
|--------|------|---------|----------|------|
| **Afferent Coupling (Ca)** | High (stable) | - | Low (unstable) | `analyze-architecture.py` |
| **Efferent Coupling (Ce)** | Low | > 10 | > 20 | `analyze-architecture.py` |
| **Instability (I = Ce/(Ca+Ce))** | 0.2-0.4 (libraries) | > 0.6 | > 0.8 | `analyze-architecture.py` |
| **Abstractness (A)** | High for stable | - | Low for stable | `analyze-architecture.py` |
| **Distance from Main Sequence** | < 0.1 | 0.1-0.3 | > 0.3 | `analyze-architecture.py` |
| **Cyclomatic Complexity** | ≤ 10 | 11-20 | > 20 | Linter/SAST |
| **Cognitive Complexity** | ≤ 15 | 16-30 | > 30 | Linter/SAST |
| **Nesting Depth** | ≤ 3 | 4-5 | > 5 | Linter |

---

## Domain-Driven Design (Tactical)

### Building Blocks
| Pattern | Purpose | When to Use |
|---------|---------|-------------|
| **Entity** | Identity + continuity | Has lifecycle, distinct identity |
| **Value Object** | Equality by value | Immutable, no identity, replaces primitives |
| **Aggregate** | Consistency boundary | Enforces invariants, transaction boundary |
| **Domain Event** | Side effects, integration | Something happened that others care about |
| **Repository** | Collection illusion | Abstracts persistence, returns aggregates |
| **Domain Service** | Stateless operations | Logic doesn't fit in entity/VO, cross-aggregate |
| **Factory** | Complex creation | Encapsulates creation logic |
| **Specification** | Business rules as objects | Complex queries, validation rules |

### Aggregate Design Rules
1. **Single aggregate per transaction** (true consistency)
2. **Reference other aggregates by ID only** (no object references)
3. **Small aggregates** (prefer < 10 entities)
4. **Root entity controls invariants** (no public setters on children)
5. **Events published after commit** (transactional outbox pattern)

```typescript
// ✅ Good: Aggregate root enforces invariants
class Order {
  private items: OrderItem[] = [];
  private status: OrderStatus = 'draft';

  addItem(product: Product, quantity: number): void {
    if (this.status !== 'draft') throw new Error('Cannot modify confirmed order');
    if (quantity <= 0) throw new Error('Quantity must be positive');
    // ... invariant checks
    this.items.push(new OrderItem(product, quantity));
  }

  confirm(): void {
    if (this.items.length === 0) throw new Error('Empty order');
    this.status = 'confirmed';
    this.raise(new OrderConfirmed(this.id, this.items));
  }
}

// ❌ Bad: Anemic domain model (public setters, no invariants)
class Order {
  items: OrderItem[] = [];
  status: string = 'draft';
}
```

---

## Architectural Patterns

### CQRS (Command Query Responsibility Segregation)
```
┌─────────────────┐     ┌─────────────────┐
│   COMMANDS      │     │   QUERIES       │
│  (Write Model)  │     │  (Read Model)   │
├─────────────────┤     ├─────────────────┤
│ Validate        │     │ Optimize for    │
│ Business Rules  │     │ Read Patterns   │
│ Emit Events     │     │ Denormalized    │
│ Persist State   │     │ Projections     │
└────────┬────────┘     └────────┬────────┘
         │                       │
         ▼                       ▼
┌─────────────────────────────────────┐
│         EVENT STORE / DB            │
│  (Single Source of Truth)           │
└─────────────────────────────────────┘
```

**When**: Complex domain, different read/write patterns, audit requirements, scalability.

### Event Sourcing
```typescript
// Event Store (append-only)
interface EventStore {
  append(stream: string, events: Event[], expectedVersion: number): Promise<void>;
  read(stream: string): Promise<Event[]>;
  subscribe(stream: string, handler: EventHandler): Promise<void>;
}

// Aggregate rebuilds from events
class Order {
  static fromHistory(events: Event[]): Order {
    const order = new Order();
    events.forEach(e => order.apply(e));
    return order;
  }

  private apply(event: Event): void {
    switch (event.type) {
      case 'OrderCreated': this.id = event.payload.id; break;
      case 'ItemAdded': this.items.push(event.payload); break;
      // ...
    }
  }
}
```

### Saga Pattern (Distributed Transactions)
```
Order Service          Payment Service         Inventory Service
    │                      │                       │
    ├── CreateOrder ──────►│                       │
    │◄── OrderCreated ─────│                       │
    │                      │                       │
    ├── ReservePayment ───►│                       │
    │                      │◄── PaymentReserved ───│
    │                      │                       │
    ├── ReserveStock ─────►──────────────────────►│
    │                      │                       │◄── StockReserved ──│
    │                      │                       │
    ├── ConfirmOrder ─────►│                       │
    │                      ├── CapturePayment ────►│
    │                      │◄── PaymentCaptured ───│
    │                      │                       │
```

**Compensation**: Each step has a rollback (e.g., `ReleaseStock`, `RefundPayment`).

---

## Module Organization

### Monorepo Structure (Recommended)
```
repo/
├── packages/
│   ├── shared/              # Shared kernel (types, utils, config)
│   │   ├── kernel/          # Core types, errors, events
│   │   ├── config/          # Environment config schema
│   │   └── testing/         # Test utilities, fixtures
│   │
│   ├── domain/              # Domain layer (pure, no deps)
│   │   ├── billing/
│   │   ├── inventory/
│   │   └── user/
│   │
│   ├── application/         # Application layer (use cases)
│   │   ├── billing/
│   │   ├── inventory/
│   │   └── user/
│   │
│   ├── adapters/            # Interface adapters
│   │   ├── api/             # REST, GraphQL controllers
│   │   ├── cli/             # Command-line interfaces
│   │   ├── persistence/     # Repository implementations
│   │   ├── messaging/       # Event publishers/consumers
│   │   └── external/        # Third-party integrations
│   │
│   └── apps/                # Deployable applications
│       ├── api-gateway/
│       ├── billing-service/
│       └── worker/
│
├── tools/                   # Build, deploy, migration tools
├── docs/                    # Architecture docs, ADRs
├── turbo.json               # Turborepo config
└── package.json             # Workspace root
```

### Dependency Rules (Enforced)
```json
// package.json (workspace root)
{
  "dependencies": {},
  "devDependencies": {
    "eslint-plugin-import": "^2.29.0",
    "eslint-plugin-boundaries": "^3.0.0"
  }
}

// .eslintrc.js (enforced via linting)
module.exports = {
  rules: {
    'boundaries/element-types': [
      'error',
      {
        default: 'disallow',
        rules: [
          { from: 'domain', allow: ['domain', 'shared'] },
          { from: 'application', allow: ['application', 'domain', 'shared'] },
          { from: 'adapters', allow: ['adapters', 'application', 'domain', 'shared'] },
          { from: 'apps', allow: ['*'] }
        ]
      }
    ]
  }
}
```

---

## API Design Standards

### REST
| Principle | Standard |
|-----------|----------|
| **Naming** | Plural nouns, kebab-case: `/api/v1/users/{id}/orders` |
| **Versioning** | URL path: `/api/v1/`, `/api/v2/` (never headers) |
| **Filtering** | Query params: `?status=active&created_after=2024-01-01` |
| **Pagination** | Cursor-based: `?cursor=abc123&limit=20` |
| **Sorting** | `?sort=-created_at,name` |
| **Errors** | RFC 7807 Problem Details: `application/problem+json` |
| **Rate limiting** | Headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `Retry-After` |

### GraphQL
```graphql
# Schema design
type Query {
  # Connections for pagination (Relay spec)
  users(first: Int, after: String, filter: UserFilter): UserConnection!
  
  # Node interface for refetching
  node(id: ID!): Node
}

type UserConnection {
  edges: [UserEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

# Mutations: explicit, verb-based
type Mutation {
  createUser(input: CreateUserInput!): CreateUserPayload!
  updateUser(id: ID!, input: UpdateUserInput!): UpdateUserPayload!
  deleteUser(id: ID!): DeleteUserPayload!
}

# Payload pattern (always return result + errors)
type CreateUserPayload {
  user: User
  errors: [UserError!]!
  clientMutationId: String
}
```

### Async/Event-Driven
```yaml
# AsyncAPI specification
asyncapi: 3.0.0
info:
  title: Order Events
  version: 1.0.0
channels:
  order.created:
    publish:
      message:
        payload:
          type: object
          properties:
            orderId: { type: string, format: uuid }
            customerId: { type: string }
            total: { type: number }
            items: { type: array }
          required: [orderId, customerId, total, items]
        headers:
          type: object
          properties:
            correlationId: { type: string, format: uuid }
            causationId: { type: string, format: uuid }
            timestamp: { type: string, format: date-time }
```

---

## Observability Architecture

### Three Pillars (Implemented as Code)

#### Structured Logging
```typescript
// JSON, correlation IDs, sampling
interface LogEntry {
  timestamp: string;           // ISO 8601
  level: 'debug' | 'info' | 'warn' | 'error';
  service: string;             // service name
  traceId: string;             // W3C TraceContext
  spanId: string;
  message: string;             // Human-readable
  fields: Record<string, any>; // Structured data
  // No PII, secrets, or stack traces in production
}

// Usage
logger.info('Order confirmed', {
  orderId: order.id,
  customerId: order.customerId,
  total: order.total,
  itemsCount: order.items.length,
  traceId: context.traceId,
});
```

#### Metrics (Prometheus Format)
```typescript
// RED metrics (every service)
http_requests_total{service="api",method="GET",route="/users",status="200"} 1234
http_request_duration_seconds{service="api",method="GET",route="/users",quantile="0.99"} 0.145

// USE metrics (resources)
process_cpu_seconds_total{service="api"} 567.89
process_resident_memory_bytes{service="api"} 157286400
go_goroutines{service="api"} 42

// Business metrics
orders_created_total{service="billing",status="confirmed"} 1234
payment_amount_usd{service="billing",method="card"} 56789.00
```

#### Distributed Tracing (W3C TraceContext)
```
Headers:
  traceparent: 00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01
  tracestate:  vendor=value

Span Attributes (Semantic Conventions):
  http.method: GET
  http.route: /api/v1/users/{id}
  http.status_code: 200
  http.target: /api/v1/users/123
  db.system: postgresql
  db.operation: SELECT
  db.statement: SELECT * FROM users WHERE id = $1
  messaging.system: kafka
  messaging.destination: order.created
```

---

## Architecture Decision Records (ADRs)

### When to Write
- New technology choice (DB, framework, cloud service)
- Significant pattern adoption (CQRS, Event Sourcing, Saga)
- Cross-cutting concern (auth, logging, caching, observability)
- Data model changes (schema, partitioning, migration strategy)
- Team topology changes (service extraction, monorepo split)

### Template
```markdown
# ADR 0003: Migrate from MongoDB to PostgreSQL

## Status
Accepted (2024-01-15)

## Context
- MongoDB scaling issues with complex transactions
- Team lacks MongoDB expertise
- Reporting requires complex joins
- PostgreSQL supports ACID, JSONB, mature tooling

## Decision
Migrate billing and inventory services to PostgreSQL.
Use dual-write during transition (6 weeks).

## Consequences
### Positive
- ACID transactions for order/payment consistency
- Rich query capabilities for reporting
- Team familiarity, hiring pool
- Mature migration tooling (pgloader, logical replication)

### Negative
- Migration effort (6 weeks, dual-write complexity)
- Schema migrations required (vs schemaless)
- JSONB less flexible than BSON for deeply nested data

### Risks
- Data loss during migration (mitigation: verification scripts)
- Performance regression (mitigation: load test, indexes)
- Dual-write inconsistency (mitigation: reconciliation job)

## Alternatives Considered
1. **Stay on MongoDB**: Add transaction support (limited), invest in expertise
2. **CockroachDB**: Distributed SQL, PostgreSQL-compatible (immature tooling)
3. **DynamoDB**: Managed, scalable (vendor lock-in, limited queries)

## Links
- [Migration Plan](docs/migrations/003-mongodb-to-postgres.md)
- [Load Test Results](benchmarks/mongodb-vs-postgres.md)
- [Schema Design](packages/billing/persistence/schema.sql)
```

---

## Architecture Governance (CI/CD)

### Automated Checks
```yaml
# .github/workflows/architecture.yml
jobs:
  architecture:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Check dependency rules
        run: python scripts/analyze-architecture.py --fail-on cycles,boundaries,forbidden
      - name: Check complexity budgets
        run: python scripts/analyze-architecture.py --max-cyclomatic 10 --max-cognitive 15
      - name: Check coupling metrics
        run: python scripts/analyze-architecture.py --max-instability 0.6
      - name: Generate architecture diagram
        run: python scripts/analyze-architecture.py --diagram docs/architecture.mmd
```

### Architecture Fitness Functions
```python
# tests/architecture/test_fitness.py
def test_no_cycles():
    cycles = analyze_architecture.find_cycles()
    assert len(cycles) == 0, f"Cycles detected: {cycles}"

def test_layer_isolation():
    violations = analyze_architecture.check_layers({
        'domain': ['shared'],
        'application': ['domain', 'shared'],
        'adapters': ['application', 'domain', 'shared'],
    })
    assert len(violations) == 0, f"Layer violations: {violations}"

def test_complexity_budgets():
    hotspots = analyze_architecture.find_complexity_hotspots(
        max_cyclomatic=10, max_cognitive=15
    )
    assert len(hotspots) == 0, f"Complexity violations: {hotspots}"

def test_dependency_direction():
    instability = analyze_architecture.calculate_instability()
    for module, score in instability.items():
        if module.startswith('domain') or module.startswith('application'):
            assert score < 0.3, f"{module} too unstable: {score}"
```

---

## Team Topology & Architecture Alignment

### Team Types (Team Topologies)
| Team Type | Responsibility | Architecture Role |
|-----------|----------------|-------------------|
| **Stream-aligned** | End-to-end feature delivery | Owns domain module(s) |
| **Enabling** | Platform, tools, practices | Provides shared kernel, adapters |
| **Complicated-subsystem** | Specialized domain (ML, crypto) | Owns complex domain module |
| **Platform** | Infrastructure, CI/CD, observability | Owns frameworks & drivers layer |

### Conway's Law in Practice
```
Team Structure ──────────────────► System Architecture
     │                                      │
     ▼                                      ▼
┌─────────┐                          ┌─────────────┐
│ Team A  │  ────── communicates ──► │ Service A   │
│ Team B  │                          │ Service B   │
└─────────┘                          └─────────────┘
     │                                      │
     ▼                                      ▼
  Shared kernel                      Shared library
```

**Design teams and architecture together.** If you want microservices, organize as stream-aligned teams. If you want a modular monolith, organize as feature teams with module ownership.

---

## Migration Strategies (Brownfield)

### Strangler Fig Pattern
```
┌─────────────────────────────────────────────────────────────┐
│                        LEGACY SYSTEM                          │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│  │ Module A│  │ Module B│  │ Module C│  │ Module D│        │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘        │
│       │            │            │            │               │
└───────┼────────────┼────────────┼────────────┼───────────────┘
        │            │            │            │
        ▼            ▼            ▼            ▼
┌─────────────────────────────────────────────────────────────┐
│                      NEW SYSTEM                               │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│  │ Module A│  │ Module B│  │ Module C│  │ Module D│        │
│  │ (New)  │  │ (New)  │  │ (Legacy)│  │ (Legacy)│        │
│  └────────┘  └────────┘  └─────────┘  └─────────┘        │
└─────────────────────────────────────────────────────────────┘
        ▲
        │
   Feature flags / routing
```

### Feature Toggle Strategy
```typescript
// Gradual migration with feature flags
const features = {
  'new-billing-engine': {
    enabled: (context) => context.user.tier === 'premium', // Canary
    rollout: 0.1, // 10% of traffic
  },
  'new-inventory-service': {
    enabled: () => true, // Full rollout
    rollout: 1.0,
  },
};

// Router
function routeRequest(request: Request): Handler {
  if (features['new-billing-engine'].enabled(request.context)) {
    return newBillingHandler;
  }
  return legacyBillingHandler;
}
```

---

## Architecture Review Checklist

### Pre-Implementation
- [ ] ADR written and reviewed
- [ ] Threat model completed
- [ ] Data flow diagram drawn
- [ ] API contracts defined (OpenAPI/AsyncAPI)
- [ ] Migration plan (if brownfield)
- [ ] Rollback plan
- [ ] Load test plan
- [ ] Observability requirements defined

### Post-Implementation
- [ ] Architecture fitness functions pass
- [ ] Dependency rules enforced
- [ ] Complexity budgets met
- [ ] Observability dashboards live
- [ ] Runbooks written
- [ ] Team ownership assigned (CODEOWNERS)
- [ ] Documentation updated
- [ ] Post-deploy monitoring (24h, 7d, 30d)