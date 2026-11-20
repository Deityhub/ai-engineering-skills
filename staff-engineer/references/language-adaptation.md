# Language Adaptation Framework — Universal Principles for Any Language

**Instead of language-specific guides, this framework shows how to apply universal staff engineer principles to ANY detected language.**

---

## Core Universal Principles (Language-Agnostic)

These 10 principles apply to **every language, every codebase, every project**:

| # | Principle | Universal Definition |
|---|-----------|---------------------|
| 1 | **Secure by Default** | Validate all inputs at boundaries. Never trust external data. Use parameterized queries. Encrypt in transit/rest. Rotate secrets. |
| 2 | **Explicit over Implicit** | No magic. Dependencies declared. Types explicit. Configuration over convention. Fail fast on ambiguity. |
| 3 | **Single Responsibility** | One reason to change per module/function/class. Cohesive, not coupled. |
| 4 | **Dependency Inversion** | High-level policies don't depend on low-level details. Both depend on abstractions (interfaces/protocols/traits). |
| 5 | **Fail Fast, Fail Loud** | Validate early. Crash on programmer errors. Return structured errors for expected failures. Never swallow exceptions. |
| 6 | **Observability Built-In** | Structured logs (JSON), metrics (RED/USE), traces (W3C). Not an afterthought. |
| 7 | **Test as Specification** | Tests document behavior. Unit: fast, isolated. Integration: real dependencies. Contract: consumer-driven. |
| 8 | **Performance by Measurement** | No optimization without profiling. Algorithmic → Architectural → Config → Micro. Budgets in CI. |
| 9 | **Immutable by Default** | Values over references. Pure functions. No shared mutable state. Explicit mutability where needed. |
| 10 | **Document Decisions, Not Code** | ADRs capture *why*. Code shows *what*. Comments explain *intent*, not mechanics. |

---

## Language Detection & Adaptation

When you encounter a codebase, **detect the language(s)** and apply the adaptation pattern:

### Detection Signals
```bash
# Primary indicators (in priority order)
*.go + go.mod              → Go
*.rs + Cargo.toml          → Rust
*.py + pyproject.toml      → Python
*.ts + tsconfig.json       → TypeScript
*.js + package.json        → JavaScript
*.java + pom.xml/build.gradle → Java/Kotlin
*.cs + *.csproj            → C#
*.php + composer.json      → PHP
*.rb + Gemfile             → Ruby
*.swift + Package.swift    → Swift
*.kt + build.gradle.kts    → Kotlin
*.scala + build.sbt        → Scala
*.clj + deps.edn           → Clojure
*.ex + mix.exs             → Elixir
*.hs + *.cabal             → Haskell
*.cpp/*.h + CMakeLists.txt → C++
*.zig + build.zig          → Zig
```

### Adaptation Template (Apply to ANY Language)

For each detected language, instantiate this template:

```markdown
# Language Adaptation: [LANGUAGE]

## Type System & Safety
- **Strict mode**: [How to enable strict type checking]
- **Null safety**: [How to avoid null/undefined bugs]
- **Generics/Parametric polymorphism**: [Syntax for reusable type-safe code]
- **Sum types / Discriminated unions**: [How to model "this OR that" safely]
- **Branded/nominal types**: [How to prevent primitive obsession]

## Error Handling (No Exceptions for Control Flow)
- **Result/Either type**: [How to return success/failure explicitly]
- **Error types**: [How to define domain errors vs infrastructure errors]
- **Fail fast**: [How to validate at boundaries]

## Dependency Injection & Modularity
- **Module system**: [Packages/crates/modules/namespaces]
- **Interface abstraction**: [Protocols/traits/interfaces/abstract classes]
- **Wiring/composition root**: [Where dependencies are assembled]
- **Boundary enforcement**: [How to prevent layer violations]

## Testing Strategy
- **Unit test framework**: [Fast, isolated, no I/O]
- **Integration test framework**: [Real dependencies, testcontainers]
- **Contract testing**: [Consumer-driven contracts]
- **Property-based testing**: [Generative testing if available]

## Observability
- **Structured logging**: [JSON logger, correlation IDs]
- **Metrics**: [Prometheus/OpenTelemetry client]
- **Tracing**: [OpenTelemetry instrumentation]

## Security
- **Input validation**: [Schema validation at boundaries]
- **Secrets management**: [Env vars, vault integration]
- **Dependency scanning**: [Tool for vulnerability scanning]
- **SAST**: [Static analysis tool]

## Performance
- **Profiling**: [CPU/memory profiler]
- **Benchmarking**: [Microbenchmark framework]
- **Connection pooling**: [DB, HTTP, Redis pools]
- **Caching**: [Redis/client library]

## CI/CD Standards
- **Linting**: [Tool + strict config]
- **Type checking**: [Strict mode command]
- **Testing**: [Unit + integration + contract]
- **Security**: [SAST + secrets + deps + license]
- **Build**: [Reproducible, hermetic]
```

---

## Canonical Examples (Reference Only)

These are **examples of the adaptation pattern** — not exhaustive guides. Use them as templates when you encounter these languages.

### Example: Go Adaptation
```markdown
## Type System & Safety
- Strict mode: `go vet`, `staticcheck`, `govet` in CI
- Null safety: No nil interfaces, use `*T` only when nil is valid
- Generics: `type Result[T any] struct { value T; err error }`
- Sum types: Interface + type switch, or `github.com/dave/jennifer` for codegen
- Branded types: `type UserID string` + constructor `func NewUserID(s string) (UserID, error)`

## Error Handling
- Result type: Custom `Result[T]` with `IsOk()`, `Unwrap()`, `Map()`
- Error types: `AppError{Code, Message, Err, Fields}` implementing `error`
- Wrap: `errors.Wrap(err, Code, "context")`, unwrap with `errors.As()`

## Dependency Injection
- Module system: Packages + `internal/` for private
- Interface: `type Repository interface { FindByID(ctx, id) (*Order, error) }`
- Wire: `google/wire` for compile-time DI
- Boundary enforcement: `golangci-lint` with `depguard`, `importas`

## Testing
- Unit: `testing` + `testify/assert`, `testify/require`
- Integration: `testcontainers-go` with PostgreSQL, Redis
- Contract: `pact-go` for provider verification
- Benchmarks: `testing.B` with `-bench=. -benchmem`

## Observability
- Logging: `zerolog` or `slog` (Go 1.21+)
- Metrics: `prometheus/client_golang` with `promauto`
- Tracing: `go.opentelemetry.io/otel` + `otelhttp`, `otelsql`

## Security
- Validation: `go-playground/validator/v10` on structs
- Secrets: `caarlos0/env/v11` for config, never in code
- Deps: `govulncheck`, `gosec`, `nancy` for license
- SAST: `staticcheck`, `gosec` in CI

## Performance
- Profiling: `net/http/pprof`, `go tool pprof -http=:8080`
- Benchmarks: `go test -bench=. -benchmem`
- DB: `pgx/v5` + `sqlx`, prepared statements
- Cache: `redis/go-redis/v9` with stampede protection

## CI/CD
- Lint: `golangci-lint` with strict config
- Type: `go vet ./...` + `staticcheck ./...`
- Test: `go test -race -coverprofile=coverage.out ./...`
- Security: `gosec ./...`, `govulncheck ./...`, `go-licenses`
```

### Example: TypeScript Adaptation
```markdown
## Type System & Safety
- Strict mode: `tsconfig.json` with `strict: true`, `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`
- Null safety: `strictNullChecks`, `undefined` vs `null` distinction
- Generics: `type Result<T, E = Error> = Ok<T> | Err<E>`
- Discriminated unions: `type Event = UserCreated | UserUpdated | UserDeleted`
- Branded types: `type UserId = string & { __brand: 'UserId' }`

## Error Handling
- Result type: `Result<T, E>` with pattern matching via `match()` or `if/else`
- Error types: `AppError` class with `code`, `message`, `cause`, `fields`
- Zod for runtime validation at boundaries

## Dependency Injection
- Module system: ES modules + workspaces (npm/yarn/pnpm)
- Interfaces: `interface PaymentGateway { charge(...): Promise<Charge> }`
- DI: Manual composition root, or `dependency-injector` / `inversify`
- Boundary enforcement: `eslint-plugin-boundaries`, `import/no-cycle`

## Testing
- Unit: `vitest` (fast) or `jest`
- Integration: `testcontainers` + real DB
- Contract: `@pact-foundation/pact` for consumer-driven
- E2E: `playwright` for API + UI

## Observability
- Logging: `pino` (structured JSON, redaction)
- Metrics: `prom-client` with `prom-auto`
- Tracing: `@opentelemetry/sdk-node` + auto-instrumentations

## Security
- Validation: `zod` schemas at API boundaries
- Secrets: `process.env` + `dotenv` (local), secret manager (prod)
- Deps: `npm audit`, `pip-audit`, `snyk`
- SAST: `semgrep`, `eslint-security-plugin`

## Performance
- Profiling: `--inspect` + Chrome DevTools, `0x`, `clinic.js`
- Benchmarks: `vitest --bench` or custom
- DB: `pg` + prepared statements, connection pooling
- Cache: `ioredis` with stampede protection
- Bundle: `vite`/`webpack` + `webpack-bundle-analyzer`

## CI/CD
- Lint: `eslint` + `typescript-eslint` strict
- Type: `tsc --noEmit`
- Test: `vitest run --coverage`
- Security: `semgrep scan`, `npm audit`, `license-checker`
```

### Example: Python Adaptation
```markdown
## Type System & Safety
- Strict mode: `mypy --strict` in CI, `pyproject.toml` config
- Null safety: `Optional[T]` vs `T`, `None` checks required
- Generics: `TypeVar`, `Generic[T]`, `Protocol` for structural typing
- Discriminated unions: `Result = Ok[T] | Err[E]` with `match` (3.10+)
- Branded types: `NewType('UserId', str)` + constructor

## Error Handling
- Result type: `@dataclass(frozen=True) class Ok[T]...` + `match`
- Error types: `AppError` with `code`, `message`, `cause`, `fields`
- Pydantic for runtime validation at boundaries

## Dependency Injection
- Module system: Packages + `src/` layout
- Protocols: `@runtime_checkable class PaymentGateway(Protocol): ...`
- DI: `dependency-injector` (containers/providers) or manual
- Boundary enforcement: `import-linter` contracts

## Testing
- Unit: `pytest` + `pytest-asyncio`
- Integration: `testcontainers` (PostgreSQL, Redis)
- Contract: `pact-python` for provider verification
- Property: `hypothesis` for generative testing

## Observability
- Logging: `structlog` (JSON, contextvars, processors)
- Metrics: `prometheus-client` with middleware
- Tracing: `opentelemetry-sdk` + auto-instrumentations

## Security
- Validation: Pydantic models at API boundaries
- Secrets: `pydantic-settings` + `.env` (local), secret manager (prod)
- Deps: `pip-audit`, `pip-licenses`, `safety`
- SAST: `semgrep`, `bandit` (limited), `ruff` for code quality

## Performance
- Profiling: `py-spy`, `pyinstrument`, `cProfile`
- Benchmarks: `pytest-benchmark`
- DB: `sqlalchemy 2.0` async + `asyncpg`, prepared statements
- Cache: `redis-py` async with stampede protection
- Concurrency: `asyncio` + `asyncio.Semaphore` for bounded parallelism

## CI/CD
- Lint: `ruff` (fast, comprehensive)
- Type: `mypy --strict src/`
- Test: `pytest -x --cov=src --cov-fail-under=80`
- Security: `pip-audit`, `pip-licenses --fail-on GPL`, `semgrep`
```

### Example: Rust Adaptation
```markdown
## Type System & Safety
- Strict mode: `cargo clippy -- -D warnings`, `cargo check`
- Null safety: `Option<T>` everywhere, no null
- Generics: Native, monomorphized, zero-cost
- Sum types: `enum Result<T, E> { Ok(T), Err(E) }` - built-in!
- Branded types: `struct UserId(Uuid);` + `impl TryFrom<String>`

## Error Handling
- Result type: Built-in `Result<T, E>` with `?` operator
- Error types: `thiserror` for library errors, `anyhow` for applications
- Fail fast: `unwrap()` only in tests/examples, `expect()` with context

## Dependency Injection
- Module system: Crates + `mod` + visibility (`pub(crate)`, `pub(super)`)
- Traits: `trait Repository { async fn find(&self, id: Id) -> Result<Order>; }`
- DI: Manual composition root, or `di`/`shaku` for complex apps
- Boundary enforcement: Workspace + `cargo deny` for license/ban

## Testing
- Unit: Built-in `#[test]`, `#[cfg(test)]` modules
- Integration: `testcontainers` + `sqlx` for real DB
- Contract: `pact_rust` (emerging)
- Property: `proptest` for generative testing
- Fuzzing: `cargo fuzz` + `libfuzzer`

## Observability
- Logging: `tracing` + `tracing-subscriber` (structured, spans)
- Metrics: `metrics-rs` + `metrics-exporter-prometheus`
- Tracing: `opentelemetry` + `tracing-opentelemetry`

## Security
- Validation: `validator` crate on structs, `serde` with validation
- Secrets: `config` crate + env vars, `secrecy` for zeroizing
- Deps: `cargo audit`, `cargo deny check licenses`
- SAST: `cargo clippy`, `cargo geiger` (unsafe detection)

## Performance
- Profiling: `cargo flamegraph`, `perf`, `pprof-rs`
- Benchmarks: `criterion.rs` (statistical rigor)
- DB: `sqlx` (compile-time checked queries), `deadpool` for pooling
- Cache: `redis-async` + `redis-cluster` with connection pooling
- Zero-cost abstractions: Trust the compiler

## CI/CD
- Lint: `cargo clippy -- -D warnings`
- Type: `cargo check --all-targets`
- Test: `cargo test --all-targets --workspace`
- Security: `cargo audit`, `cargo deny check`, `cargo geiger`
- Build: `cargo build --release --locked`
```

### Example: Java/Kotlin Adaptation
```markdown
## Type System & Safety
- Strict mode: `-Xlint:all`, `Error Prone`, `NullAway` (Java), Kotlin strict mode
- Null safety: Kotlin non-nullable by default, `@Nullable`/`@NotNull` (Java)
- Generics: Reified type parameters (Kotlin), bounded wildcards (Java)
- Sealed classes: `sealed interface Result<T> { data class Ok(val v: T) : Result<T>; data class Err(val e: Error) : Result<T> }`
- Value classes: `value class UserId(val uuid: UUID)` (Kotlin)

## Error Handling
- Result type: Sealed class + exhaustive `when` (Kotlin), `Result<T>` lib (Java)
- Error types: `data class AppError(val code: Code, val message: String, val cause: Throwable?)`
- Checked vs unchecked: Use unchecked for programmer errors, checked for expected failures

## Dependency Injection
- Module system: Gradle modules + `internal`/`api` dependencies
- Interfaces: `interface Repository { suspend fun findById(id: Id): Result<Order> }`
- DI: `Koin` (Kotlin), `Dagger/Hilt` (Java), or manual constructor injection
- Boundary enforcement: `ArchUnit` tests, `import-linter` equivalent

## Testing
- Unit: `JUnit 5` + `MockK`/`Mockito`
- Integration: `Testcontainers` + `Spring`/`Quarkus`/`Micronaut` test support
- Contract: `Pact JVM` for consumer-driven contracts
- Property: `jqwik` (Java), `kotlin-test-property` (Kotlin)

## Observability
- Logging: `Logback`/`Log4j2` + structured JSON (`logstash-logback-encoder`)
- Metrics: `Micrometer` + `Prometheus` registry
- Tracing: `OpenTelemetry Java` + auto-instrumentation agent

## Security
- Validation: `Jakarta Bean Validation` (`@Valid`, `@NotNull`, custom constraints)
- Secrets: `Spring Vault` / `HashiCorp Vault` client, never in code
- Deps: `OWASP Dependency Check`, `License Checker`
- SAST: `SpotBugs` + `Error Prone` + `SonarQube`

## Performance
- Profiling: `Java Flight Recorder (JFR)`, `async-profiler`, `VisualVM`
- Benchmarks: `JMH` (Java Microbenchmark Harness)
- DB: `HikariCP` + `R2DBC` (reactive) or `JDBC` with prepared statements
- Cache: `Caffeine` (local), `Redis` (distributed) with `Spring Cache` abstraction
- Virtual threads: Java 21+ `Executors.newVirtualThreadPerTaskExecutor()`

## CI/CD
- Lint: `SpotBugs`, `Error Prone`, `ktlint`/`detekt` (Kotlin)
- Type: `javac -Xlint:all`, `kotlinc -Xlint`
- Test: `./gradlew test` / `./mvnw test` with coverage (`JaCoCo`)
- Security: `dependency-check`, `license-checker`, `sonarqube`
```

---

## How to Use This Framework

### When Starting a New Task
1. **Detect language(s)** in the codebase
2. **Instantiate the adaptation template** for each language
3. **Apply universal principles** through the language's idioms
4. **Use canonical examples** as reference for tooling/commands

### When Reviewing Code
1. Check: **Are universal principles followed?**
2. Check: **Are language-specific idioms used correctly?**
3. Check: **Are the right tools configured in CI?**

### When Setting Up a New Project
1. Copy the **adaptation template** for your language
2. Fill in the tooling/commands for your ecosystem
3. Add to CI pipeline
4. Share with team as "Engineering Standards"

---

## The Key Insight

> **Universal principles don't change. Language idioms do.**

| Universal Principle | Go Idiom | TypeScript Idiom | Python Idiom | Rust Idiom |
|---------------------|----------|------------------|--------------|------------|
| Secure by Default | `validator` on structs | `zod` schemas | Pydantic models | `validator` crate |
| Explicit over Implicit | Explicit error returns | `Result<T, E>` unions | `Result` dataclass | Built-in `Result<T, E>` |
| Dependency Inversion | Interfaces + `wire` | Interfaces + manual DI | Protocols + `dependency-injector` | Traits + manual DI |
| Fail Fast | `errors.Wrap` + `errors.As` | `throw` + `try/catch` | `raise` + `except*` | `?` operator + `thiserror` |
| Observability | `zerolog` + `promauto` | `pino` + `prom-client` | `structlog` + `prometheus-client` | `tracing` + `metrics-rs` |

**Learn the pattern once. Apply everywhere.**