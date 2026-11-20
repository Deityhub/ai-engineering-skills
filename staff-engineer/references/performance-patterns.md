# Performance Patterns — Staff Engineer Reference

**Language-agnostic performance engineering.** Measure first, optimize second.

---

## Performance Engineering Philosophy

### The Performance Loop
```
1. DEFINE SLOs (latency, throughput, availability, error rate)
   ↓
2. INSTRUMENT (metrics, tracing, profiling, logging)
   ↓
3. BASELINE (current performance under realistic load)
   ↓
4. IDENTIFY BOTTLENECKS (profiling, flame graphs, query analysis)
   ↓
5. OPTIMIZE (algorithmic → architectural → micro)
   ↓
6. VALIDATE (load test, canary, regression detection)
   ↓
7. MONITOR CONTINUOUSLY (alerting on SLO burn rate)
```

### Optimization Hierarchy (Do in Order)
| Level | Impact | Effort | Examples |
|-------|--------|--------|----------|
| **Algorithmic** | 10-1000× | Medium | O(n²) → O(n log n), better data structures |
| **Architectural** | 2-100× | High | Caching, async, read replicas, partitioning |
| **Configuration** | 1.5-10× | Low | Connection pools, thread pools, GC tuning |
| **Micro** | 1.05-2× | High | Loop unrolling, SIMD, branch prediction |

**Rule**: Never micro-optimize before proving algorithmic/architectural fixes insufficient.

---

## Profiling Toolkit (Language-Agnostic)

### Continuous Profiling
```bash
# Production-safe sampling profilers
# Go: pprof (net/http/pprof), Pyroscope
# Java: async-profiler, JFR
# Python: py-spy, Austin, Pyroscope
# Node: 0x, clinic.js, Pyroscope
# Rust: pprof-rs, samply
# .NET: dotnet-trace, PerfView

# Deploy as sidecar or library integration
# Sample rate: 100-1000 Hz (low overhead)
```

### Flame Graph Analysis
```
Flame Graph Reading Guide:
├── Width = CPU time (or memory allocation)
├── X-axis = alphabetical (not temporal)
├── Top frames = leaf functions (actual work)
├── Look for: wide plateaus (hotspots), deep stacks (recursion)
└── Colors: typically package/module (customizable)
```

**Key patterns**:
- **Wide flat top**: Single function dominating (optimize it)
- **Sawtooth**: GC pressure (tune heap, reduce allocations)
- **Deep narrow**: Recursion or middleware chains (flatten)

### Key Metrics by Layer

#### Macro (Business)
| Metric | Target | Measurement |
|--------|--------|-------------|
| Latency p50 | < 100ms | Load balancer / APM |
| Latency p99 | < 500ms | Load balancer / APM |
| Throughput | > X req/s | Counter (rate) |
| Error rate | < 0.1% | Counter (rate) |
| Availability | 99.99% | Uptime checks |

#### Meso (Service)
| Metric | Target | Tool |
|--------|--------|------|
| CPU utilization | 50-70% | `top`, `htop`, `pidstat` |
| Memory RSS | < 80% limit | `pmap`, `valgrind massif` |
| GC pause p99 | < 10ms | Runtime-specific |
| Thread count | Stable | `ps`, runtime metrics |
| Goroutine/Thread leak | Zero | Runtime metrics |

#### Micro (Function)
| Metric | Tool |
|--------|------|
| Cycles/instruction | `perf stat`, `cargo bench` |
| Cache miss rate | `perf stat -e cache-misses` |
| Branch mispredictions | `perf stat -e branch-misses` |
| Allocation rate | Runtime-specific (pprof, JFR, etc.) |

---

## Caching Strategy

### Cache Decision Matrix
```
                    │ Read-heavy    │ Write-heavy    │ Mixed
────────────────────┼───────────────┼────────────────┼─────────────
Strong consistency  │ DB + sync     │ DB             │ DB + CDC
Eventual consistency│ Redis + TTL   │ Async + cache  │ Multi-layer
High throughput     │ CDN + Edge    │ Batch + queue  │ Tiered
```

### Cache Layers
| Layer | Latency | Capacity | Use Case | Invalidation |
|-------|---------|----------|----------|--------------|
| **Client** | 0ms | MB | Optimistic UI, prefetch | SWR/React Query |
| **CDN/Edge** | 1-50ms | GB-TB | Static assets, public APIs | TTL + Purge API |
| **Application** | 0.5-5ms | GB | Computed results, DB queries | Write-through + TTL |
| **Database** | 1-10ms | TB | Materialized views, query cache | Trigger-based |

### Cache Patterns
```python
# 1. Cache-Aside (Lazy Loading)
async def get_user(user_id: str) -> User:
    if cached := await redis.get(f"user:{user_id}"):
        return User.parse_raw(cached)
    user = await db.fetch_user(user_id)
    await redis.setex(f"user:{user_id}", ttl=300, value=user.json())
    return user

# 2. Write-Through (Strong Consistency)
async def update_user(user: User) -> None:
    await db.update_user(user)
    await redis.set(f"user:{user.id}", user.json(), ex=300)

# 3. Write-Behind (High Throughput)
async def update_user_async(user: User) -> None:
    await db.update_user(user)
    await queue.enqueue("cache_update", {"key": f"user:{user.id}", "value": user.json()})

# 4. Cache Stampede Protection
async def get_with_lock(key: str, factory: Callable) -> Any:
    lock = redis.lock(f"lock:{key}", timeout=10)
    async with lock:
        return await get_or_set(key, factory)
```

### Cache Key Design
```
Format: {domain}:{entity}:{id}:{version}:{variant}
Examples:
  user:profile:123:v2:en-US
  product:catalog:category:electronics:v1:mobile
  analytics:dashboard:daily:2024-01-15:v3

Versioning: Increment on schema change (never delete old keys immediately)
```

---

## Concurrency & Parallelism

### Thread Pool Sizing
| Workload Type | Pool Size | Rationale |
|---------------|-----------|-----------|
| CPU-bound | `num_cores` | Context switch overhead |
| I/O-bound | `2 × num_cores` | Overlap I/O wait |
| Mixed | `num_cores + 1` | Balanced |
| Blocking (legacy) | `10-100 × num_cores` | High wait time |

### Backpressure Patterns
```typescript
// 1. Bounded Queue (Reject when full)
const queue = new BoundedQueue<Task>(1000);
queue.enqueue(task); // Throws if full

// 2. Reactive Streams (Project Reactor, RxJS, Kotlin Flow)
Flux.create(sink -> {
    while (!sink.isCancelled()) {
        Task task = queue.take();
        sink.next(process(task));
    }
}).onBackpressureBuffer(1000, dropped -> log.warn("Dropped: {}", dropped));

// 3. Circuit Breaker (Resilience4j, Hystrix, go-breaker)
@CircuitBreaker(name = "external-api", fallbackMethod = "fallback")
public Response callExternal(Request req) { ... }

// 4. Token Bucket Rate Limiting
RateLimiter limiter = RateLimiter.create(100); // 100 permits/sec
limiter.acquire(); // Blocks until permit available
```

### Async/Await Best Practices
```python
# ✅ Parallel I/O (when independent)
results = await asyncio.gather(
    fetch_user(user_id),
    fetch_orders(user_id),
    fetch_recommendations(user_id)
)

# ✅ Bounded concurrency (semaphore)
semaphore = asyncio.Semaphore(10)
async def bounded_fetch(url):
    async with semaphore:
        return await fetch(url)

# ✅ Timeout everything
async with asyncio.timeout(5.0):
    await external_call()

# ❌ Sequential when parallel possible
# ❌ No timeout on external calls
# ❌ Unbounded task creation
```

---

## Database Performance

### Query Optimization Checklist
| Check | Tool | Target |
|-------|------|--------|
| Sequential scans | `EXPLAIN ANALYZE` | Zero on large tables |
| Index usage | `EXPLAIN` | Index scan > 95% |
| Join order | `EXPLAIN` | Smallest result first |
| N+1 queries | ORM logging | Zero in production |
| Connection pooling | PgBouncer stats | 90%+ utilization |

### Index Strategy
```sql
-- ✅ Composite indexes for query patterns
CREATE INDEX idx_orders_user_status_date ON orders(user_id, status, created_at DESC);

-- ✅ Partial indexes for common filters
CREATE INDEX idx_orders_pending ON orders(user_id, created_at) WHERE status = 'pending';

-- ✅ Covering indexes (include columns)
CREATE INDEX idx_orders_covering ON orders(user_id, status) INCLUDE (total, currency);

-- ❌ Single-column indexes on low-cardinality columns
-- ❌ Indexes on frequently updated columns (write amplification)
```

### Connection Pooling
```yaml
# PgBouncer (PostgreSQL)
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 25  # per CPU core
min_pool_size = 5
reserve_pool_size = 5
reserve_pool_timeout = 5

# HikariCP (JVM)
maximumPoolSize = 20  # cores * 2
minimumIdle = 5
connectionTimeout = 30000
idleTimeout = 600000
maxLifetime = 1800000
leakDetectionThreshold = 60000
```

### Read Replicas & Partitioning
```yaml
# Read replica routing
read_replicas:
  - host: replica-1
    weight: 50
    lag_threshold_ms: 100  # Route to primary if lag > 100ms
  - host: replica-2
    weight: 50
    lag_threshold_ms: 100

# Partitioning strategy
partition_by:
  - table: events
    strategy: time_series
    interval: 1 month
    retention: 13 months
  - table: tenants
    strategy: hash
    partitions: 64
```

---

## Frontend Performance (Web)

### Core Web Vitals
| Metric | Good | Needs Improvement | Poor |
|--------|------|-------------------|------|
| **LCP** (Largest Contentful Paint) | ≤ 2.5s | 2.5-4s | > 4s |
| **INP** (Interaction to Next Paint) | ≤ 200ms | 200-500ms | > 500ms |
| **CLS** (Cumulative Layout Shift) | ≤ 0.1 | 0.1-0.25 | > 0.25 |

### Optimization Checklist
```typescript
// 1. Code splitting (route-level + component-level)
const HeavyComponent = lazy(() => import('./HeavyComponent'));

// 2. Tree shaking (ESM + sideEffects: false in package.json)
// 3. Bundle analysis
// webpack-bundle-analyzer, vite-bundle-visualizer, source-map-explorer

// 4. Resource hints
<link rel="preload" as="script" href="/critical.js">
<link rel="prefetch" href="/next-page.js">
<link rel="preconnect" href="https://api.example.com">

// 5. Image optimization
<picture>
  <source srcset="/img.avif" type="image/avif">
  <source srcset="/img.webp" type="image/webp">
  <img src="/img.jpg" width="800" height="600" loading="lazy" alt="...">
</picture>

// 6. Font optimization
// - Subset fonts (unicode-range)
// - font-display: swap
// - Preload critical fonts
<link rel="preload" as="font" href="/font.woff2" crossorigin>

// 7. Service Worker (Workbox)
precacheManifest: [
  {url: '/', revision: '1'},
  {url: '/app.js', revision: 'abc123'},
]
```

### Budget Enforcement
```yaml
# .github/workflows/perf-budget.yml
jobs:
  bundle-size:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci && npm run build
      - name: Check budgets
        run: |
          # JS budget: 170KB gzipped
          size=$(gzip -c dist/app.js | wc -c)
          [[ $size -le 174080 ]] || exit 1
          
          # CSS budget: 50KB gzipped
          size=$(gzip -c dist/app.css | wc -c)
          [[ $size -le 51200 ]] || exit 1
```

---

## Load Testing & Validation

### Test Types
| Type | Purpose | Tool | Frequency |
|------|---------|------|-----------|
| **Smoke** | Basic functionality | k6, Artillery | Every PR |
| **Load** | Expected traffic | k6, Locust, JMeter | Nightly |
| **Stress** | Breaking point | k6, Locust | Weekly |
| **Soak** | Stability over time | k6, Locust | Pre-release |
| **Spike** | Sudden traffic surge | k6 | Pre-release |

### k6 Example
```javascript
// load-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 100 },  // Ramp up
    { duration: '5m', target: 100 },  // Steady state
    { duration: '2m', target: 200 },  // Stress
    { duration: '5m', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(99)<500'],  // p99 < 500ms
    http_req_failed: ['rate<0.01'],    // Error rate < 1%
  },
};

export default function() {
  const res = http.get('https://api.example.com/users/123');
  check(res, {
    'status 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });
  sleep(1);
}
```

---

## Performance Budgets (Enforce in CI)

```yaml
# perf-budget.yaml
service: "api-gateway"
budgets:
  latency:
    p50: 50ms
    p95: 200ms
    p99: 500ms
  throughput:
    min_rps: 1000
  errors:
    max_rate: 0.1%
  resources:
    cpu_max: 70%
    memory_max: 80%
    connections_max: 80%

# Validate in CI
python scripts/profile-performance.py --budget perf-budget.yaml --fail-on breach
```

---

## Continuous Performance Regression Detection

```bash
# Compare current vs baseline
python scripts/profile-performance.py \
  --baseline benchmarks/baseline.json \
  --current benchmarks/current.json \
  --threshold 5%  # Fail if >5% regression
```

**Store baselines per release tag** in `benchmarks/v1.2.3.json`.

---

## Language-Specific Profiling Commands

| Language | CPU Profile | Memory Profile | Flame Graph |
|----------|-------------|----------------|-------------|
| Go | `go tool pprof -http=:8080 profile.pb.gz` | `go tool pprof -alloc_space` | `go tool pprof -flame` |
| Java | `async-profiler -d 60 -f profile.jfr` | `JFR` + JMC | `async-profiler -f flame.html` |
| Python | `py-spy record -o profile.svg --pid 123` | `memray run -- python app.py` | `py-spy flame -o flame.svg` |
| Node | `node --inspect` + Chrome DevTools | `node --inspect` + heap snapshot | `0x app.js` |
| Rust | `cargo flamegraph` | `cargo profiler` + `pprof` | `cargo flamegraph` |
| .NET | `dotnet-trace collect` | `dotnet-gcdump` | `dotnet-trace convert` |