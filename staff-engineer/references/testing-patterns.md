# Testing Patterns — Staff Engineer Reference

> **Principle**: Tests are specifications. They document behavior, prevent regressions, and enable fearless refactoring.

---

## Test Pyramid (Pragmatic)

```
        ████████████
       █  E2E/UI   █   ← Few, critical paths only (5-10%)
      ██████████████
     ████████████████
    █ Integration  █  ← Service boundaries, DB, external APIs (15-20%)
   ██████████████████
  ████████████████████
 █  Unit Tests   █    ← Fast, isolated, deterministic (70-80%)
██████████████████████
```

**Rule**: If a test takes >100ms, it's not a unit test. If it needs a database, it's integration.

---

## Unit Testing

### Principles
- **Fast**: <10ms per test, <1s total suite
- **Isolated**: No I/O, no shared state, no external deps
- **Deterministic**: Same input → same output, always
- **Self-documenting**: Name describes behavior, not implementation

### Structure (AAA / Given-When-Then)
```python
# Python (pytest)
def test_user_service_returns_user_when_found():
    # Given
    repo = FakeUserRepository(users={"123": User("123", "Alice")})
    service = UserService(repo)

    # When
    result = service.get_user("123")

    # Then
    assert result.name == "Alice"
```

```typescript
// TypeScript (Vitest)
it("returns user when found", () => {
  // Given
  const repo = new FakeUserRepository({ "123": new User("123", "Alice") });
  const service = new UserService(repo);

  // When
  const result = service.getUser("123");

  // Then
  expect(result.name).toBe("Alice");
});
```

### Test Doubles Hierarchy
| Double | When to Use | Example |
|--------|-------------|---------|
| **Fake** | Working impl, lightweight | In-memory repo, fake clock |
| **Stub** | Canned responses | `repo.findById.returns(user)` |
| **Spy** | Verify interactions | `verify(repo).save(user)` |
| **Mock** | Behavior verification | `expect(repo.save).toHaveBeenCalledWith(user)` |

**Prefer Fakes > Stubs > Spies > Mocks**. Mocks couple to implementation.

### Property-Based Testing
```python
# Python (hypothesis)
from hypothesis import given, strategies as st

@given(st.lists(st.integers()))
def test_sort_is_idempotent(nums):
    assert sorted(sorted(nums)) == sorted(nums)

@given(st.text())
def test_serialization_roundtrip(s):
    assert deserialize(serialize(s)) == s
```

```typescript
// TypeScript (fast-check)
import { test, expect } from "vitest";
import * as fc from "fast-check";

test("sort is idempotent", () => {
  fc.assert(fc.property(fc.array(fc.integer()), (nums) => {
    expect(sort(sort(nums))).toEqual(sort(nums));
  }));
});
```

**Use for**: Algorithms, serialization, invariants, edge cases.

---

## Integration Testing

### Definition
Tests that verify **interactions between components** using real dependencies (DB, HTTP, message queue, filesystem).

### Patterns

#### Database Integration
```python
# Python (pytest + testcontainers)
import pytest
from testcontainers.postgres import PostgresContainer
from sqlalchemy import create_engine
from myapp.repositories import PostgresUserRepository

@pytest.fixture(scope="session")
def postgres():
    with PostgresContainer("postgres:16") as pg:
        yield pg.get_connection_url()

@pytest.fixture
def repo(postgres):
    engine = create_engine(postgres)
    Base.metadata.create_all(engine)
    return PostgresUserRepository(engine)

def test_save_and_find_user(repo):
    user = User("123", "Alice")
    repo.save(user)
    found = repo.find_by_id("123")
    assert found.name == "Alice"
```

```go
// Go (testcontainers-go)
func TestPostgresUserRepository(t *testing.T) {
    ctx := context.Background()
    pg, err := postgres.Run(ctx, "postgres:16")
    require.NoError(t, err)
    defer pg.Terminate(ctx)

    connStr, _ := pg.ConnectionString(ctx, "sslmode=disable")
    repo := NewPostgresUserRepository(connStr)

    user := &User{ID: "123", Name: "Alice"}
    require.NoError(t, repo.Save(ctx, user))

    found, err := repo.FindByID(ctx, "123")
    require.NoError(t, err)
    assert.Equal(t, "Alice", found.Name)
}
```

#### HTTP/API Integration
```python
# Python (httpx + testcontainers for service)
def test_create_user_endpoint(test_client, db):
    response = test_client.post("/users", json={"name": "Alice"})
    assert response.status_code == 201
    assert response.json()["name"] == "Alice"

    # Verify in DB
    user = db.query(User).filter_by(name="Alice").first()
    assert user is not None
```

#### Message Queue Integration
```go
// Go (testcontainers rabbitmq/kafka)
func TestOrderEventPublished(t *testing.T) {
    ctx := context.Background()
    rmq, _ := rabbitmq.Run(ctx, "rabbitmq:3.12")
    defer rmq.Terminate(ctx)

    conn, _ := amqp.Dial(rmq.AMQPURL(ctx))
    ch, _ := conn.Channel()
    q, _ := ch.QueueDeclare("orders", true, false, false, false, nil)

    msgs, _ := ch.Consume(q.Name, "", false, false, false, false, nil)

    // Act: place order
    service.PlaceOrder(ctx, Order{ID: "123", Item: "Widget"})

    // Assert: event published
    select {
    case msg := <-msgs:
        var event OrderPlaced
        json.Unmarshal(msg.Body, &event)
        assert.Equal(t, "123", event.OrderID)
        msg.Ack(false)
    case <-time.After(2 * time.Second):
        t.Fatal("timeout waiting for message")
    }
}
```

### Test Data Management
- **Fixtures**: Shared test data in `testdata/` or fixtures module
- **Builders**: Fluent builders for complex objects
- **Factories**: `factory_boy` (Python), `go-faker` (Go), `factory.ts` (TS)

```python
# Python (factory_boy)
class UserFactory(factory.Factory):
    class Meta:
        model = User
    id = factory.Sequence(lambda n: str(n))
    name = factory.Faker("name")
    email = factory.LazyAttribute(lambda o: f"{o.name.lower().replace(' ', '.')}@example.com")

# Usage
user = UserFactory()
admin = UserFactory(name="Admin", email="admin@example.com")
users = UserFactory.create_batch(5)
```

---

## Contract Testing

### Consumer-Driven Contracts (Pact)
```
Consumer (Frontend)          Provider (API)
     │                            │
     ├─ Defines expectations ────►│
     │                            │
     │◄─ Verifies against pact ───┤
     │                            │
     ├─ Runs against mock ───────►│
     │                            │
     │◄─ Provider publishes ──────┤
```

```typescript
// Consumer test (Pact + Vitest)
import { Pact } from "@pact-foundation/pact";

const provider = new Pact({ consumer: "WebApp", provider: "UserAPI" });

describe("User API", () => {
  beforeAll(() => provider.setup());
  afterAll(() => provider.finalize());

  it("returns user", () => {
    provider.addInteraction({
      state: "user 123 exists",
      uponReceiving: "a request for user 123",
      withRequest: { method: "GET", path: "/users/123" },
      willRespondWith: {
        status: 200,
        body: { id: "123", name: "Alice" },
      },
    });

    const user = await fetchUser("123");
    expect(user.name).toBe("Alice");
  });
});
```

```python
# Provider verification (pytest-pact)
def test_provider_against_pact(pact_verifier):
    pact_verifier.verify_provider(
        "UserAPI",
        pact_urls=["http://localhost:9292/pacts/provider/UserAPI/consumer/WebApp/latest"],
        provider_base_url="http://localhost:8080",
    )
```

---

## E2E Testing

### When to Write
- Critical user journeys (login, checkout, onboarding)
- Cross-service workflows
- Regression bugs that unit/integration missed

### Tools by Platform
| Platform | Tool |
|----------|------|
| Web | Playwright, Cypress |
| Mobile | Detox, Appium |
| CLI | Bats, shell specs |
| API | Postman, custom |

### Playwright Example (Web)
```typescript
// e2e/checkout.spec.ts
import { test, expect } from "@playwright/test";

test("complete purchase flow", async ({ page }) => {
  await page.goto("/login");
  await page.fill('[name="email"]', "user@example.com");
  await page.fill('[name="password"]', "secret");
  await page.click('button[type="submit"]');

  await page.goto("/product/123");
  await page.click('button:has-text("Add to Cart")');

  await page.goto("/cart");
  await page.click('button:has-text("Checkout")');

  await expect(page.locator(".order-confirmation")).toBeVisible();
  await expect(page.locator(".order-number")).toContainText(/ORD-\d+/);
});
```

### E2E Best Practices
- **Data isolation**: Each test creates own data, cleans up
- **No shared state**: Parallel-safe by default
- **Tag critical paths**: `@critical` for CI gate
- **Visual regression**: Screenshot diff for UI changes
- **Flaky test quarantine**: Auto-retry + separate pipeline

---

## Test Organization

### Directory Structure
```
project/
├── src/
│   └── ...
├── tests/
│   ├── unit/              # Fast, isolated
│   │   ├── domain/
│   │   ├── application/
│   │   └── utils/
│   ├── integration/       # Real deps
│   │   ├── repositories/
│   │   ├── http/
│   │   └── messaging/
│   ├── contract/          # Pact files
│   │   ├── consumer/
│   │   └── provider/
│   ├── e2e/               # Critical paths
│   │   ├── web/
│   │   └── mobile/
│   ├── fixtures/          # Shared test data
│   │   ├── builders/
│   │   ├── factories/
│   │   └── testdata/
│   └── conftest.py        # Shared fixtures (pytest)
```

### Naming Conventions
| Type | Pattern |
|------|---------|
| Unit | `test_<function>_<scenario>_<expected>` |
| Integration | `test_<component>_<integration>_<scenario>` |
| Contract | `test_<consumer>_<provider>_<interaction>` |
| E2E | `test_<journey>_<step>_<outcome>` |

---

## CI/CD Integration

### Pipeline Stages
```yaml
# .github/workflows/test.yml
jobs:
  unit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: make test-unit          # <30s, must pass

  integration:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        ports: [5432:5432]
    steps:
      - uses: actions/checkout@v4
      - run: make test-integration   # <5min

  contract:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: make test-contract      # Consumer + Provider

  e2e:
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request' || github.ref == 'main'
    steps:
      - uses: actions/checkout@v4
      - run: make test-e2e           # @critical only on PR, full on main

  quality-gate:
    needs: [unit, integration, contract, e2e]
    runs-on: ubuntu-latest
    steps:
      - run: |
          # Enforce thresholds
          coverage=$(cat coverage/unit/lcov.info | lcov --summary | grep "lines" | awk '{print $2}')
          if (( $(echo "$coverage < 80" | bc -l) )); then exit 1; fi
```

### Coverage Thresholds
| Layer | Target | Tool |
|-------|--------|------|
| Unit | ≥80% lines, ≥70% branches | pytest-cov, vitest --coverage, go tool cover |
| Integration | Not measured (speed) | — |
| Critical paths | 100% (E2E tagged) | Playwright --reporter=line |

---

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| Testing implementation | Brittle, blocks refactoring | Test behavior/output |
| Shared mutable fixtures | Flaky, order-dependent | Fresh fixtures per test |
| Sleep/wait in tests | Slow, flaky | Poll with timeout, fake time |
| Real external calls | Slow, unreliable | Fake/stub at boundary |
| No assertions | Passes but validates nothing | Always assert |
| Testing private methods | Couples to internals | Test via public API |
| Giant test methods | Hard to debug | One assertion per test |

---

## Language-Specific Tooling

| Language | Unit | Integration | Property | Contract | E2E |
|----------|------|-------------|----------|----------|-----|
| **Python** | pytest | pytest + testcontainers | Hypothesis | pytest-pact | Playwright |
| **TypeScript** | Vitest | Vitest + testcontainers | fast-check | @pact-foundation/pact | Playwright |
| **Go** | testing, testify | testcontainers-go | gopter | pact-go | Playwright |
| **Rust** | built-in, proptest | testcontainers-rs | proptest | pact-verifier | Playwright |
| **Java** | JUnit 5, Mockito | Testcontainers | jqwik | Pact JVM | Playwright |

---

## Staff Engineer Checklist for Test Reviews

- [ ] **Unit tests** cover all business logic, edge cases, error paths
- [ ] **Integration tests** verify real DB/HTTP/queue interactions
- [ ] **Contract tests** exist for service boundaries
- [ ] **E2E tests** cover critical user journeys (tagged `@critical`)
- [ ] **No flaky tests** — quarantined or fixed
- [ ] **Fast feedback** — unit <30s, integration <5min
- [ ] **Coverage** ≥80% on unit, 100% on critical paths
- [ ] **Test names** document behavior (readable as specs)
- [ ] **No implementation coupling** — mocks/fakes at boundaries only
- [ ] **Property tests** for algorithms, serialization, invariants
- [ ] **Mutation testing** runs in CI (Stryker, pitest, go-mutesting)

---

## Further Reading
- *Growing Object-Oriented Software, Guided by Tests* — Freeman & Pryce
- *Unit Testing Principles, Practices, and Patterns* — Vladimir Khorikov
- *Testing Microservices* — Toby Clemson
- *Property-Based Testing* — F. Huch
- Pact.io docs for contract testing