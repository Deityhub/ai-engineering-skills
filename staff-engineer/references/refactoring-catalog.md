# Refactoring Catalog — Staff Engineer Reference

**Safe, validated transformations with risk levels.** Run via `scripts/suggest-refactor.py`.

---

## Risk Assessment Framework

| Risk Level | Criteria | Validation Required | Rollback |
|------------|----------|---------------------|----------|
| **Low** | Single function, pure logic, >80% test coverage | Unit tests pass, complexity ↓ | Instant (git revert) |
| **Medium** | Multiple functions, shared state, interfaces | Unit + integration tests, contract tests | Feature flag (minutes) |
| **High** | Cross-module, data model, distributed | Full test suite, load test, canary deploy | Migration scripts (hours) |

---

## Catalog: Low Risk (Safe First Steps)

### 1. Extract Function
```typescript
// BEFORE
function processOrder(order: Order): Receipt {
  // 50 lines: validate → calculate → charge → ship → receipt
  if (!order.items.length) throw new Error('Empty order');
  const customer = db.getCustomer(order.customerId);
  // ... validation logic
  let subtotal = 0;
  for (const item of order.items) { /* ... */ }
  // ... calculation logic
  const charge = payment.charge(customer.paymentMethod, total);
  // ... shipping logic
  return generateReceipt(order, charge, shipment);
}

// AFTER
function processOrder(order: Order): Receipt {
  validateOrder(order);
  const customer = getCustomer(order.customerId);
  const pricing = calculatePricing(order, customer);
  const charge = processPayment(customer, pricing.total);
  const shipment = arrangeShipping(order, charge);
  return generateReceipt(order, charge, shipment);
}

// Validation: Tests pass, cyclomatic complexity 12 → 3
```

**When**: Function > 20 lines, repeated logic, complex conditionals
**Risk**: Low (if extracted functions are pure)
**Validation**: Existing tests + new unit tests for extracted functions

### 2. Replace Magic Numbers with Constants
```typescript
// BEFORE
if (user.age >= 18 && user.age <= 65) { /* ... */ }
setTimeout(() => retry(), 300000);
const maxRetries = 3;

// AFTER
const ADULT_MIN_AGE = 18;
const SENIOR_MAX_AGE = 65;
const RETRY_DELAY_MS = 5 * 60 * 1000; // 5 minutes
const MAX_RETRIES = 3;
```

**When**: Any literal with business meaning
**Risk**: Very Low
**Validation**: Tests pass, grep for remaining magic numbers

### 3. Replace Conditional with Guard Clauses
```typescript
// BEFORE
function shipOrder(order: Order): Shipment {
  if (order.isPaid) {
    if (order.hasInventory) {
      if (order.address.isValid) {
        return createShipment(order);
      }
    }
  }
  throw new Error('Cannot ship');
}

// AFTER
function shipOrder(order: Order): Shipment {
  if (!order.isPaid) throw new Error('Order not paid');
  if (!order.hasInventory) throw new Error('Insufficient inventory');
  if (!order.address.isValid) throw new Error('Invalid address');
  return createShipment(order);
}
```

**When**: Nested conditionals > 2 levels, "arrow code"
**Risk**: Low
**Validation**: Tests pass, cyclomatic complexity ↓

### 4. Introduce Parameter Object
```typescript
// BEFORE
function createUser(
  email: string, 
  name: string, 
  age: number, 
  address: Address, 
  preferences: Preferences,
  referralCode?: string
): User { /* ... */ }

// AFTER
interface CreateUserRequest {
  email: string;
  name: string;
  age: number;
  address: Address;
  preferences: Preferences;
  referralCode?: string;
}

function createUser(request: CreateUserRequest): User { /* ... */ }
```

**When**: > 3 related parameters, parameters often passed together
**Risk**: Low
**Validation**: Tests pass, call sites updated

### 5. Replace Primitive with Value Object
```typescript
// BEFORE
function calculateShipping(weight: number, distance: number): Money { /* ... */ }
// Called as: calculateShipping(2.5, 1500)

// AFTER
class Weight {
  constructor(private readonly kg: number) {
    if (kg <= 0) throw new Error('Weight must be positive');
  }
  get value(): number { return this.kg; }
  plus(other: Weight): Weight { return new Weight(this.kg + other.kg); }
}

class Distance {
  constructor(private readonly km: number) {
    if (km < 0) throw new Error('Distance cannot be negative');
  }
  get value(): number { return this.km; }
}

function calculateShipping(weight: Weight, distance: Distance): Money { /* ... */ }
// Called as: calculateShipping(new Weight(2.5), new Distance(1500))
```

**When**: Primitive represents domain concept, validation needed, operations defined
**Risk**: Low-Medium (call sites change)
**Validation**: Tests pass, no primitive obsession remains

---

## Catalog: Medium Risk (Structural Changes)

### 6. Extract Class (Single Responsibility)
```typescript
// BEFORE: God class
class OrderProcessor {
  validateOrder(order: Order): ValidationResult { /* 50 lines */ }
  calculatePricing(order: Order): PriceBreakdown { /* 100 lines */ }
  processPayment(order: Order, payment: Payment): Charge { /* 80 lines */ }
  arrangeShipping(order: Order): Shipment { /* 60 lines */ }
  generateReceipt(order: Order): Receipt { /* 40 lines */ }
  sendConfirmation(order: Order): void { /* 30 lines */ }
}

// AFTER: Separate responsibilities
class OrderValidator { validate(order: Order): ValidationResult { /* ... */ } }
class PricingEngine { calculate(order: Order): PriceBreakdown { /* ... */ } }
class PaymentProcessor { charge(order: Order, payment: Payment): Charge { /* ... */ } }
class ShippingService { arrange(order: Order): Shipment { /* ... */ } }
class ReceiptGenerator { generate(order: Order): Receipt { /* ... */ } }
class NotificationService { sendConfirmation(order: Order): void { /* ... */ } }

// Orchestrator (thin)
class OrderService {
  constructor(
    private validator: OrderValidator,
    private pricing: PricingEngine,
    private payment: PaymentProcessor,
    private shipping: ShippingService,
    private receipts: ReceiptGenerator,
    private notifications: NotificationService
  ) {}
  
  async process(order: Order): Promise<Receipt> {
    this.validator.validate(order);
    const pricing = this.pricing.calculate(order);
    const charge = await this.payment.charge(order, pricing);
    const shipment = await this.shipping.arrange(order);
    const receipt = this.receipts.generate(order, charge, shipment);
    await this.notifications.sendConfirmation(order);
    return receipt;
  }
}
```

**When**: Class > 500 lines, > 5 public methods, mixed responsibilities
**Risk**: Medium (dependencies, wiring)
**Validation**: Unit tests per class, integration test for orchestrator, feature flag rollout

### 7. Introduce Interface (Dependency Inversion)
```typescript
// BEFORE: Direct dependency
class OrderService {
  constructor(private db: PostgreSQLDatabase) {} // Concrete!
  async getOrder(id: string): Promise<Order> {
    return this.db.query('SELECT * FROM orders WHERE id = $1', [id]);
  }
}

// AFTER: Interface + Implementation
interface OrderRepository {
  findById(id: string): Promise<Order | null>;
  save(order: Order): Promise<void>;
}

class PostgresOrderRepository implements OrderRepository {
  constructor(private db: PostgreSQLDatabase) {}
  async findById(id: string): Promise<Order | null> {
    return this.db.query('SELECT * FROM orders WHERE id = $1', [id]);
  }
  async save(order: Order): Promise<void> { /* ... */ }
}

class OrderService {
  constructor(private repo: OrderRepository) {} // Abstract!
  async getOrder(id: string): Promise<Order> {
    return this.repo.findById(id) ?? throw new NotFoundError();
  }
}
```

**When**: Testing requires mocks, multiple implementations likely, layer boundary
**Risk**: Low-Medium (wiring changes)
**Validation**: Liskov substitution test, all implementations pass same contract tests

### 8. Replace Conditional with Polymorphism
```typescript
// BEFORE: Switch on type
function calculateDiscount(customer: Customer, order: Order): Money {
  switch (customer.tier) {
    case 'basic': return Money.zero();
    case 'premium': return order.subtotal.multiply(0.10);
    case 'vip': return order.subtotal.multiply(0.20);
    case 'enterprise': return order.subtotal.multiply(0.25);
  }
}

// AFTER: Strategy pattern
interface DiscountStrategy {
  calculate(order: Order): Money;
}

class BasicDiscount implements DiscountStrategy {
  calculate(order: Order): Money { return Money.zero(); }
}
class PremiumDiscount implements DiscountStrategy {
  calculate(order: Order): Money { return order.subtotal.multiply(0.10); }
}
class VIPDiscount implements DiscountStrategy {
  calculate(order: Order): Money { return order.subtotal.multiply(0.20); }
}
class EnterpriseDiscount implements DiscountStrategy {
  calculate(order: Order): Money { return order.subtotal.multiply(0.25); }
}

// Factory
class DiscountStrategyFactory {
  create(tier: CustomerTier): DiscountStrategy {
    const strategies = {
      basic: BasicDiscount,
      premium: PremiumDiscount,
      vip: VIPDiscount,
      enterprise: EnterpriseDiscount,
    };
    return new strategies[tier]();
  }
}
```

**When**: Switch on type repeated in > 3 places, Open/Closed principle violated
**Risk**: Medium (new classes, factory)
**Validation**: Contract tests per strategy, factory tested, no switch statements remain

### 9. Introduce Repository Pattern
```typescript
// BEFORE: Direct DB access in domain
class Order {
  async save() {
    await db.query('INSERT INTO orders ...', [this.id, this.customerId, ...]);
  }
  static async findById(id: string): Promise<Order> {
    return db.query('SELECT * FROM orders WHERE id = $1', [id]);
  }
}

// AFTER: Repository interface in domain, implementation in infrastructure
// domain/order.repository.ts
interface OrderRepository {
  save(order: Order): Promise<void>;
  findById(id: string): Promise<Order | null>;
  findByCustomer(customerId: string): Promise<Order[]>;
}

// infrastructure/postgres-order.repository.ts
class PostgresOrderRepository implements OrderRepository {
  constructor(private pool: Pool) {}
  async save(order: Order): Promise<void> {
    await this.pool.query('INSERT ...', [order.id, order.customerId, ...]);
  }
  async findById(id: string): Promise<Order | null> {
    return this.pool.query('SELECT * FROM orders WHERE id = $1', [id]);
  }
}

// Domain service uses interface
class OrderService {
  constructor(private repo: OrderRepository) {}
  async placeOrder(order: Order): Promise<void> {
    await this.repo.save(order);
  }
}
```

**When**: Domain logic coupled to DB, testing requires DB, multiple data sources
**Risk**: Medium (new layer, wiring)
**Validation**: Contract tests for repository, integration tests with testcontainers

---

## Catalog: High Risk (Architectural Changes)

### 10. Decompose Monolith → Services (Strangler Fig)
```
PHASE 1: Identify Seams
├── Billing context → Own database, API
├── Inventory context → Own database, API
├── User context → Own database, API
└── Shared kernel → Common types, events

PHASE 2: Extract First Service (Billing)
├── Create billing-service repo
├── Implement Billing API (REST/gRPC)
├── Dual-write: Monolith → Billing DB + Billing Service
├── Feature flag: route 10% traffic to service
├── Validate: load test, data consistency, latency
├── Increase: 50% → 100%
├── Remove: Billing code from monolith

PHASE 3: Repeat for Inventory, User
PHASE 4: Decommission monolith
```

**Validation per phase**:
- Contract tests (consumer-driven)
- Data reconciliation jobs
- Load test at 2× expected traffic
- Canary with automated rollback
- Runbook for rollback

### 11. Migrate to Event Sourcing
```
PHASE 1: Add Event Store (append-only)
├── EventStore interface in domain
├── Implementation: PostgreSQL (event_store table) or EventStoreDB
├── Events: OrderCreated, ItemAdded, OrderConfirmed, OrderShipped

PHASE 2: Emit Events from Aggregates
├── Aggregate.apply(event) rebuilds state
├── Aggregate.uncommittedEvents() for persistence
├── Transactional outbox for reliability

PHASE 3: Build Projections (Read Models)
├── OrderSummaryProjection → order_summaries table
├── CustomerOrderHistoryProjection → customer_orders table
├── InventoryAvailabilityProjection → inventory_availability table

PHASE 4: Switch Reads to Projections
├── Feature flag: 10% reads from projections
├── Validate: consistency, latency, completeness
├── Full cutover

PHASE 5: Remove Direct Reads from Aggregates
```

**Validation**:
- Event replay rebuilds state correctly
- Projection lag < 100ms
- Snapshot performance for large aggregates
- Schema evolution (upcasting) tested

### 12. Database Migration (Zero-Downtime)
```
STRATEGY: Expand/Contract (Blue-Green for Data)

PHASE 1: Expand (Add New)
├── Add new columns/tables (nullable, defaults)
├── Write to BOTH old and new (dual-write)
├── Backfill historical data (batch, idempotent)
├── Verify: new data matches old (reconciliation)

PHASE 2: Migrate Reads
├── Switch reads to new schema (feature flag)
├── Validate: query results identical
├── Monitor: error rates, latency

PHASE 3: Contract (Remove Old)
├── Stop dual-write
├── Drop old columns/tables
├── Remove migration code
```

**Tools**: `pgloader`, `gh-ost`, `pt-online-schema-change`, logical replication
**Validation**: Shadow queries, data diff, automated rollback triggers

---

## Automated Refactoring Detection (suggest-refactor.py)

### Detection Rules
```python
REFactoring_RULES = [
    # Low risk
    {
        'name': 'Long Function',
        'detect': lambda f: f.lines > 50 and f.cyclomatic > 10,
        'suggest': 'Extract Function',
        'risk': 'low',
    },
    {
        'name': 'Large Class',
        'detect': lambda c: c.lines > 500 or c.methods > 15,
        'suggest': 'Extract Class',
        'risk': 'medium',
    },
    {
        'name': 'Primitive Obsession',
        'detect': lambda f: count_primitive_params(f) > 3,
        'suggest': 'Introduce Parameter Object / Value Object',
        'risk': 'low',
    },
    {
        'name': 'Switch on Type',
        'detect': lambda f: count_switch_on_type(f) > 2,
        'suggest': 'Replace with Polymorphism',
        'risk': 'medium',
    },
    {
        'name': 'God Class',
        'detect': lambda c: c.responsibilities > 3,
        'suggest': 'Extract Class per Responsibility',
        'risk': 'medium',
    },
    {
        'name': 'Direct DB in Domain',
        'detect': lambda f: has_db_imports(f) and is_domain_layer(f),
        'suggest': 'Introduce Repository Pattern',
        'risk': 'medium',
    },
    {
        'name': 'Cyclic Dependencies',
        'detect': lambda modules: find_cycles(modules),
        'suggest': 'Restructure Modules / Introduce Interfaces',
        'risk': 'high',
    },
]
```

### Output Format
```markdown
# Refactoring Suggestions for: src/billing

## 🟢 Low Risk (Safe to Apply)
1. **Extract Function** in `pricing.ts:calculate()` (lines 45-120)
   - Cyclomatic: 18 → Target: <5 per function
   - Candidates: `validateOrder()`, `applyPromotions()`, `calculateTaxes()`
   - Est: 2 hours, Tests: existing + 3 new unit tests

2. **Replace Magic Numbers** in `shipping.ts` (lines 12, 45, 78)
   - Found: `300000`, `2.5`, `100`
   - Est: 30 min, Tests: existing

## 🟡 Medium Risk (Feature Flag Recommended)
3. **Extract Class** `OrderProcessor` (420 lines, 8 methods)
   - Responsibilities: validation, pricing, payment, shipping, notification
   - Target: OrderValidator, PricingEngine, PaymentProcessor, ShippingService, NotificationService
   - Est: 1 day, Tests: per-class units + integration, Flag: `new-order-pipeline`

4. **Introduce Interface** `PaymentGateway` (direct Stripe dependency in domain)
   - Location: `services/payment.ts`
   - Target: `PaymentGateway` interface + `StripePaymentGateway` adapter
   - Est: 4 hours, Tests: contract tests, Flag: `new-payment-abstraction`

## 🔴 High Risk (Requires Migration Plan)
5. **Decompose Billing Module** (cyclic deps with Inventory)
   - Cycle: Billing → Inventory → Shared → Billing
   - Target: Event-driven integration, separate databases
   - Est: 2 weeks, ADR required, Phased rollout
```

---

## Refactoring Safety Checklist

### Before Any Refactoring
- [ ] Tests exist and pass (baseline)
- [ ] Feature flag created (if user-facing)
- [ ] Rollback plan documented
- [ ] ADR written (if architectural)
- [ ] Team notified

### During Refactoring
- [ ] Small commits (one logical change each)
- [ ] Tests pass after each commit
- [ ] No behavior change (unless intentional)
- [ ] Complexity metrics improving
- [ ] No new lint violations

### After Refactoring
- [ ] All tests pass (unit, integration, contract)
- [ ] Load test (if performance-sensitive)
- [ ] Canary deployed (if user-facing)
- [ ] Monitoring alerts configured
- [ ] Documentation updated
- [ ] ADR status → Accepted
- [ ] Feature flag → 100% / removed
- [ ] Retrospective: what worked, what didn't