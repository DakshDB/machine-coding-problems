# LLD / Machine Coding — Master Cheatsheet

Recognition → data structure → boilerplate. Jump to the section you need.

**[0. Clock](#0-the-clock) · [1. Recognition](#1-recognition--phrase--mechanism) · [2. Structure choice](#2-data-structure-choice) · [3. Mechanisms](#3-the-mechanisms) · [4. Syntax](#4-syntax-quick-reference) · [5. Edge cases](#5-edge-case-checklists) · [6. Complexity](#6-complexity) · [7. What to say](#7-lines-to-say) · [8. My traps](#8-my-6-traps)**

---

## 0. The clock

| Min | Do |
|---|---|
| 0–5 | Restate. 3 assumptions **out loud**. 1–2 scoping questions, then stop. |
| 5–10 | enums → entities → **exceptions** → package skeleton |
| 10–15 | Method signatures + edge-case comment block. Say complexity as you type each. |
| 15–45 | Implement. Narrate decisions, not syntax. |
| 45–55 | **Stop building. Run the edge cases.** |
| 55–60 | Complexities, assumptions, known gaps, concurrency answer. |

Behind at 35? Cut a feature and **say you're cutting it**.

**Skeleton, always:**
```
models/enums.py       NOT enum.py (shadows stdlib)
models/entities.py
models/exceptions.py  one root + 4-5 children — WRITE FIRST
core/<policy>.py      the strategy, if there is one
core/service.py       orchestration, guards, indexes
main.py               the only file with print()
```

---

## 1. Recognition — phrase → mechanism

| The problem says… | You need |
|---|---|
| "find/get X by id", "list all X for user Y" | **dict index + secondary index** (§3.1) |
| "assign a free X", "which spot/seat/slot" | **free-pool of sets** (§3.2) |
| "status", "lifecycle", "can't go from A to B" | **transition table** (§3.3) |
| "swappable", "configurable", "policy changes", "different rules for" | **strategy, injected** (§3.4) |
| "types of X", "three kinds of" | **registry dict** (§3.5) |
| "at most N", "limit", "quota", "capacity" | **counter + guard helper** (§3.6) |
| "expires", "hold for 5 minutes", "TTL", "timeout" | **derived expiry + injected clock** (§3.7) |
| "N per minute", "rate limit", "in the last hour" | **fixed / sliding window** (§3.8) |
| "run after X seconds", "scheduled", "delayed", "cron" | **heap + Condition.wait(timeout)** (§3.9) |
| "top K", "leaderboard", "highest/nearest/next" | **heap + lazy deletion** (§3.10) |
| "cache", "evict", "least recently used" | **OrderedDict / dict+DLL** (§3.11) |
| "concurrent", "simultaneous", "thread-safe", "race" | **one lock over check-and-act** (§3.12) |
| "queue of work", "workers", "process in background" | **bounded Queue + worker pool** (§3.13) |
| "notify", "when X happens also Y", "alert", "audit" | **event bus** (§3.14) |
| "payment", "refund", "balance", "change", "split" | **transactional invariants** (§3.15) |
| "who owes whom", "settle up" | **nested dict balance map** (§3.15) |

**If two apply, they compose.** Notification service = event bus + queue + pool. Scheduler = heap + Condition. Booking = pool + expiry + lock.

---

## 2. Data structure choice

| Need | Use | Why |
|---|---|---|
| Lookup by id | `dict` | O(1) |
| "have I seen this?" | `set` | O(1) `in` |
| Pool of available things, take any | `set` | O(1) `.pop()` |
| Group by key | `defaultdict(set/list)` | the index workhorse |
| Order + index access | `list` | O(1) index |
| Add/remove both ends | `deque` | O(1) both |
| Fixed-size recent history | `deque(maxlen=n)` | auto-drops |
| Smallest/largest/next-due | `heapq` | O(log n) |
| Recency order + O(1) move | `OrderedDict` | `move_to_end`, `popitem` |
| Sorted, search-heavy | `list` + `bisect` | O(log n) search |
| Counting | `Counter` | `.most_common(k)` |
| Record, no behaviour | `@dataclass` | free init/repr/eq |
| Immutable + hashable key | `@dataclass(frozen=True)` | usable in sets |
| Thread-safe hand-off | `queue.Queue` | already correct |

**Rule:** if you're looping to *find* something, you wanted a dict or a set.
**Rule:** an index must return the thing you act on, not a count.

---

## 3. THE MECHANISMS

### 3.1 Entity store + indexes

**When:** every problem. **Structure:** `dict[id, Entity]` + `defaultdict(set)` per lookup axis.

```python
class Service:
    def __init__(self):
        self.items: dict[str, Item] = {}                    # id -> entity
        self.by_owner: dict[str, set[str]] = defaultdict(set)  # owner -> item ids

    def _get(self, item_id: str) -> Item:                   # ALWAYS have this
        item = self.items.get(item_id)
        if item is None:
            raise ItemNotFound(f"no item {item_id}")
        return item

    def assign(self, item_id, new_owner):
        item = self._get(item_id)
        if item.owner:
            self.by_owner[item.owner].discard(item_id)      # remove from OLD
        item.owner = new_owner
        self.by_owner[new_owner].add(item_id)               # add to NEW

    def get_by_owner(self, owner_id) -> list[Item]:
        return [self.items[i] for i in self.by_owner.get(owner_id, set())]
```

- Reassignment must update **both sides**. This is where indexes break.
- `.get(k, set())` on read paths — `defaultdict` reads create keys.
- Return a list/copy, never the live set.
- **Complexity:** O(1) get, O(k) by_owner where k = that owner's items, O(N) space.

---

### 3.2 Resource pool allocation

**When:** parking spot, seat, table, room, worker. **Structure:** `dict[category, set[Resource]]` holding the **free** ones only.

```python
class Floor:
    def __init__(self):
        self.free: dict[Size, set[Spot]] = {s: set() for s in Size}

    def take(self, size) -> Spot | None:
        pool = self.free[size]
        if not pool: return None
        spot = pool.pop()            # O(1), arbitrary element
        spot.occupied = True
        return spot

    def release(self, spot):
        spot.occupied = False
        self.free[spot.size].add(spot)

    def free_count(self, size): return len(self.free[size])   # count IS len()
```

- **The set holds only free items** — so `len()` is the count and can't drift. Never keep a separate counter.
- Smallest-fit: iterate compatible sizes in order, take the first that has any.
- `set.pop()` is arbitrary. Need "nearest"? Use a heap keyed on distance. **Say this.**
- **Complexity:** O(sizes × floors) = O(1) in configuration constants, not data size.

---

### 3.3 State machine (transition table)

**When:** order/task/ticket/booking status, vending machine, elevator doors.

```python
class Task(ABC):
    TRANSITIONS = {
        Status.OPEN:        {Status.IN_PROGRESS, Status.DELAYED},
        Status.IN_PROGRESS: {Status.RESOLVED, Status.DELAYED},
        Status.DELAYED:     {Status.OPEN, Status.IN_PROGRESS},
        Status.RESOLVED:    set(),                      # terminal
    }
    def update_status(self, new):
        if new == self.status: return                   # idempotent no-op
        allowed = self.TRANSITIONS[self.status]
        if new not in allowed:
            raise InvalidTransition(
                f"{type(self).__name__}: {self.status.value} -> {new.value}; "
                f"allowed: {sorted(s.value for s in allowed) or 'none'}")
        self.status = new

class BugTask(Task):
    TRANSITIONS = {**Task.TRANSITIONS,                  # NEW dict
                   Status.OPEN: {Status.IN_PROGRESS, Status.RESOLVED, Status.DELAYED}}
```

- Base holds the **algorithm**, subclass overrides the **data**. `self.TRANSITIONS` resolves via MRO.
- ⚠ `{**Base.T, k: v}` builds a new dict. **Never** `Base.T[k].add(x)` — mutates the shared table.
- You get rules free: terminal states, no illegal jumps.
- Same-state → no-op keeps it idempotent.

---

### 3.4 Strategy (pluggable policy)

**When:** "swappable", "configurable", "policy changes", "students pay half", "different rules for X and Y".

```python
class PricingStrategy(ABC):
    @abstractmethod
    def price(self, order, at: datetime) -> int: ...     # pass the OBJECT, not one field

class StandardPricing(PricingStrategy):
    def __init__(self, per_unit=50, cap=500):            # configurable
        self.per_unit, self.cap = per_unit, cap
    def price(self, order, at): ...

class StudentPricing(StandardPricing):
    def __init__(self): super().__init__(per_unit=25)

class WeekendPricing(PricingStrategy):                   # composes another
    def __init__(self, base, mult=1.5): self.base, self.mult = base, mult
    def price(self, order, at):
        return round(self.base.price(order, at) * self.mult)

class Service:
    def __init__(self, pricing: PricingStrategy = None):
        self.pricing = pricing or StandardPricing()      # NO () on the param!
```

**Three separate mistakes to avoid:**
1. Not an ABC → base is instantiable, `pass` body silently returns `None`.
2. `= StandardPricing` then `pricing()` → you can only pass a class, never a configured instance.
3. **Signature too narrow** → name implementations #2 and #3 *before* fixing the signature. If `StudentPricing` can't be expressed, widen it now.

**One implementation is scaffolding; two is a design.** Write the second.

---

### 3.5 Registry / factory

**When:** "three types of task", "vehicle types", any `if type == A ... elif type == B`.

```python
REGISTRY: dict[TaskType, type[Task]] = {
    TaskType.FEATURE: FeatureTask,
    TaskType.BUG:     BugTask,
    TaskType.STORY:   StoryTask,
}

def create_task(self, task_type, title, creator) -> Task:
    cls = REGISTRY.get(task_type)
    if cls is None:
        raise UnknownTaskType(f"unsupported: {task_type!r}")
    task = cls(id=str(uuid4()), title=title, creator=creator)
    self.tasks[task.id] = task
    return task
```

- Adding a type = adding a **row**, not editing code (Open/Closed).
- No branch to get wrong. `elif t.STORY:` is attribute access, always truthy — the classic bug.
- Unknown types fail **loudly** instead of falling through.
- Advanced (mention, don't build): `__init_subclass__` self-registration.

---

### 3.6 Capacity / quota limits

**When:** "max 3 in progress", "at most 5 books", "10 requests per minute".

```python
def _check_capacity(self, user_id, ignore_id=None):
    n = 0
    for item_id in self.by_user.get(user_id, set()):
        if item_id == ignore_id:            # exclude the item being updated
            continue
        if self.items[item_id].status == Status.ACTIVE:
            n += 1
    if n >= MAX_PER_USER:
        raise CapacityExceeded(
            f"{user_id} already has {n}, limit is {MAX_PER_USER}")
```

- **`ignore_id` is the off-by-one fix** — re-setting an already-active item must not count against itself.
- **Guard every path that reaches the state.** Assign *and* status-change both create an active item; a guard on only one is a bypass.
- `>` vs `>=` — re-read the spec wording ("more than 100" ≠ `>= 100`).

---

### 3.7 Expiry / TTL

**When:** seat hold, session, cache entry, reservation, OTP.

```python
class Service:
    def __init__(self, clock=datetime.now):     # INJECT the clock
        self._clock = clock

    def is_active(self, hold) -> bool:          # DERIVED, never stored
        return (hold.status == HoldStatus.ACTIVE
                and self._clock() < hold.expires_at)

    def available(self, show_id):
        return [s for s in self.all_seats(show_id) if self._is_free(s)]
```

```python
class FakeClock:                                 # in main.py
    def __init__(self, now): self.now = now
    def __call__(self): return self.now
    def advance(self, **kw): self.now += timedelta(**kw)

clock = FakeClock(datetime(2026, 9, 7, 10, 0))
svc = Service(clock=clock)
h = svc.hold_seats(...)
clock.advance(minutes=6)
assert not svc.is_active(h)                      # instant, no sleep()
```

- **Availability is derived from `(status, expires_at)`. Never also store an `is_free` flag** — two sources of truth drift.
- Lazy expiry (compute on read) beats a background sweeper for an interview. Say the trade-off: lazy = no thread, but memory isn't reclaimed until touched.
- ⚠ Never mutate a dict while iterating it to expire entries → `RuntimeError`. Iterate `list(d.items())`.

---

### 3.8 Sliding / fixed windows

**When:** rate limiting, "N per minute", "requests in the last hour".

```python
def allow_fixed(self, bucket, now, limit):      # cheap, 2x burst at the boundary
    key = now.replace(second=0, microsecond=0)
    if bucket.window != key:
        bucket.window, bucket.count = key, 0
    if bucket.count >= limit: return False
    bucket.count += 1
    return True

def allow_sliding(self, dq, now, limit):        # accurate, O(k) memory per client
    cutoff = now - timedelta(minutes=1)
    while dq and dq[0] <= cutoff:               # deque, prune from the left
        dq.popleft()
    if len(dq) >= limit: return False
    dq.append(now)
    return True

def allow_token_bucket(self, b, now, capacity, rate):   # controlled bursts
    elapsed = (now - b.last).total_seconds()
    b.tokens = min(capacity, b.tokens + elapsed * rate)
    b.last = now
    if b.tokens < 1: return False
    b.tokens -= 1
    return True
```

- **Prune as you go** or the log grows forever.
- Fixed-window's flaw: 10 requests at 10:00:59 + 10 at 10:01:00 = 20 in one second. That's the follow-up question.
- Idle clients still hold memory → evict on a timer or with an LRU.

---

### 3.9 Scheduling — delayed / periodic tasks

**When:** "run after N seconds", "retry with backoff", "scheduled job", "cron".

```python
class Scheduler:
    def __init__(self, clock=time.monotonic):
        self._cond = threading.Condition()
        self._heap = []                 # (run_at, seq, fn)
        self._seq = count()
        self._stopped = False
        self._clock = clock

    def schedule(self, fn, delay):
        with self._cond:
            heapq.heappush(self._heap, (self._clock() + delay, next(self._seq), fn))
            self._cond.notify_all()     # a nearer task may have jumped the queue

    def stop(self):
        with self._cond:
            self._stopped = True
            self._cond.notify_all()

    def run(self):
        while True:
            with self._cond:
                while not self._stopped and not self._heap:
                    self._cond.wait()                  # idle
                if self._stopped: return
                run_at, _, fn = self._heap[0]
                now = self._clock()
                if run_at > now:
                    self._cond.wait(run_at - now)      # sleep until due OR notified
                    continue                           # RE-CHECK, heap may have changed
                heapq.heappop(self._heap)
            try: fn()                                  # OUTSIDE the lock
            except Exception: log_it()
```

Four load-bearing details:
1. Heap → O(log n) "what's next", never a scan.
2. **`cond.wait(delay)` not `sleep(delay)`** — a newly scheduled earlier task wakes it instantly.
3. **`continue` after the timed wait** — never assume it's due; the top may have changed.
4. **Run the callback outside the lock**, in try/except — one bad task must not kill the loop.

Periodic: re-schedule at the end of `fn`, or push `(now + interval)` back on.

---

### 3.10 Priority / top-K / leaderboard

**When:** "top 10", "highest bid", "nearest", "next to expire", "most X".

Heaps have **no decrease-key and no arbitrary removal.** That's the whole difficulty.

```python
# LAZY DELETION — dict is truth, heap is a hint
class Leaderboard:
    def __init__(self):
        self._scores = {}                        # player -> score  (TRUTH)
        self._heap = []                          # (-score, player) (may be stale)

    def add_score(self, player, pts):
        self._scores[player] = self._scores.get(player, 0) + pts
        heapq.heappush(self._heap, (-self._scores[player], player))

    def top(self):
        while self._heap:
            neg, player = self._heap[0]
            if -neg == self._scores.get(player):  # still current?
                return player, -neg
            heapq.heappop(self._heap)             # stale, discard
        return None
```

```python
# TOP-K OF A STREAM — a MIN-heap of size k, O(n log k) time, O(k) space
h = []
for x in stream:
    if len(h) < k: heapq.heappush(h, x)
    elif x > h[0]: heapq.heapreplace(h, x)       # h[0] = weakest survivor
```

- Counter-intuitive: **to keep the largest k, use a min-heap.**
- Always add a tiebreaker: `(priority, next(counter), obj)` — otherwise `TypeError` on ties.
- **`rank(player)` needs order statistics** — a heap can't. Options: `sorted()` per call O(n log n) / sorted list + `bisect` / Fenwick tree. **Name the trade-off out loud.**
- Max-heap = push `-value`.

---

### 3.11 Cache / eviction

**When:** "cache", "evict", "LRU/LFU/FIFO", "bounded memory".

```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity):
        if capacity <= 0: raise InvalidCapacity()
        self.capacity = capacity                       # PER INSTANCE, not a constant
        self._d: OrderedDict[str, Entry] = OrderedDict()

    def get(self, key):
        entry = self._d.get(key)
        if entry is None: return MISS
        self._d.move_to_end(key)                       # O(1) refresh recency
        return entry.value

    def put(self, key, value):
        if key in self._d:                             # EXISTING key: no eviction
            self._d[key].value = value
            self._d.move_to_end(key)
            return
        if len(self._d) >= self.capacity:
            self._d.popitem(last=False)                # O(1) evict oldest
        self._d[key] = Entry(key, value)
```

- **`OrderedDict` is a C hash map + doubly-linked list** — that's the answer to "why not a plain list". Hand-roll a DLL only if you need extra per-node metadata.
- **`put` on an existing key must not evict.** Check membership *before* the capacity check.
- FIFO = same, minus `move_to_end` in `get`. LFU = min-heap on frequency + lazy deletion, or a freq→OrderedDict bucket map.
- ⚠ For FIFO, `put` on an existing key must **not** `move_to_end` — insertion order is the rule.

---

### 3.12 Locking & atomicity

**When:** "concurrent", "simultaneous", "thread-safe", "two users at once".

```python
class Service:
    def __init__(self):
        self._lock = threading.RLock()          # RLock: safe to nest

    def place_bid(self, buyer_id, auction_id, amount) -> bool:
        with self._lock:                        # ONE span over check AND act
            auction = self._get(auction_id)
            if auction.seller_id == buyer_id: raise SellerCantBid()
            if not self._is_active(auction):    raise AuctionClosed()
            if amount <= auction.highest:       return False
            auction.highest = amount            # compare-and-set together
            auction.winner = buyer_id
            return True
```

- **TOCTOU is the bug they hunt.** Two `with self._lock:` blocks = a race between them. One span.
- **Per-resource lock** beats one global lock: `self._locks[auction_id]` so different auctions don't serialise. Say this even if you build the simple version.
- Deadlock: acquire multiple locks in a **consistent global order**.
- **The GIL does not save you:** it protects interpreter internals, not multi-step logic. `x += 1` is not atomic.
- Test it: barrier + N threads, assert the final value equals the true max.

---

### 3.13 Pools, queues, backpressure

**When:** "workers", "background processing", "queue of jobs", "N at a time".

```python
class WorkerPool:
    def __init__(self, n=4, maxsize=100):
        self._q = Queue(maxsize=maxsize)                     # BOUNDED
        self._threads = [threading.Thread(target=self._run, daemon=True)
                         for _ in range(n)]
        for t in self._threads: t.start()

    def submit(self, fn, *args): self._q.put((fn, args))     # blocks when full

    def _run(self):
        while True:
            item = self._q.get()
            try:
                if item is None: return                      # poison pill
                fn, args = item; fn(*args)
            except Exception: log_it()                       # worker must survive
            finally: self._q.task_done()                     # or join() hangs

    def shutdown(self, wait=True):
        if wait: self._q.join()                              # drain
        for _ in self._threads: self._q.put(None)            # ONE pill per worker
        for t in self._threads: t.join()
```

- **Unbounded queue = memory leak.** Full-queue policy is a decision: block / drop / reject. Name it.
- `task_done()` in `finally`, try/except round the task, one pill **per** worker.
- ⚠ An `Event` does **not** wake a thread blocked in `q.get()`. Use pills, or `q.get(timeout=0.5)` in a loop.
- `Semaphore(n)` limits **concurrency**; a bounded queue limits **backlog**. Usually you want both.
- `ThreadPoolExecutor`: exceptions are silent until `.result()`, and its queue is **unbounded**.

**Object pool (connections):**
```python
@contextmanager
def acquire(self, timeout=None):
    conn = self._pool.get(timeout=timeout)
    try:    yield conn
    finally: self._pool.put(conn)          # ALWAYS returned, even on exception
```

---

### 3.14 Observer / event bus

**When:** "notify", "alert", "audit log", "when X happens also do Y", "webhook".

```python
class EventBus:
    def __init__(self):
        self._subs = defaultdict(list)

    def subscribe(self, topic, handler):
        self._subs[topic].append(handler)
        return lambda: self._subs[topic].remove(handler)     # unsubscribe token

    def publish(self, topic, payload):
        for handler in list(self._subs.get(topic, [])):      # iterate a COPY
            try: handler(payload)
            except Exception: log_it()                       # isolate failures
```

```python
def confirm_order(self, order):
    order.status = Status.CONFIRMED
    self.bus.publish("order.confirmed", order)   # core doesn't know about email/sms
```

- **Error isolation** — one throwing subscriber must not break the others *or* the publisher.
- **Iterate a copy** — a handler that subscribes during dispatch mutates the list.
- **Return an unsubscribe token** — handlers are strong refs, so buses leak without detach.
- Sync by default (ordering guaranteed, trivial). Name the upgrade: hand off to a queue + pool so a slow handler can't stall the publisher.
- **Composition:** `bus (who cares) → bounded queue (how much backlog) → pool (how many at once)` = a notification service.

---

### 3.15 Money & transactional invariants

**When:** payments, refunds, change, splits, balances, bids.

```python
def purchase(self, code, inserted):
    # 1. VALIDATE EVERYTHING FIRST — no mutation yet
    product = self._get_product(code)
    if self.stock[code] <= 0:        return Fail("out of stock")
    if inserted < product.price:     return Fail("insufficient")
    change_coins = self._make_change(inserted - product.price)   # pure, no mutation
    if change_coins is None:         return Fail("cannot make change")
    # 2. ONLY NOW MUTATE — all-or-nothing
    self.stock[code] -= 1
    self._float.deduct(change_coins)
    self._float.add(inserted)
    return Ok(product, change_coins)
```

- **Validate → then mutate.** Every failure path must leave stock, float and state exactly as they were.
- **Invariant to test:** `float_after == float_before + price` on success, `float_after == float_before` on failure. Randomize 200 runs.
- **Never floats for money** — int paise/cents, or `Decimal`.
- Greedy change-making **fails with a limited float** even when a solution exists (float = one ₹50 + three ₹20s, need ₹60: greedy takes 50 and is stuck; 20×3 works). Fallback = small DP/backtrack.
- **Splitwise balances:** `balances[a][b] += amount; balances[b][a] -= amount` in a `defaultdict(lambda: defaultdict(int))`. Maintain incrementally — never recompute from all expenses.
- Rounding: ₹100 split 3 ways — decide who gets the extra paisa and **say so**.

---

## 4. Syntax quick reference

### Enums & exceptions (write first, every time)
```python
from enum import Enum
class Status(Enum):
    OPEN = 'open'
# Status.OPEN.value -> 'open'   Status.OPEN.name -> 'OPEN'
# Status('open') -> lookup by value    list(Status) -> all members
# compare with ==, NEVER `if x.OPEN:` (attribute access, always truthy)

class ShopError(Exception): pass          # ONE root
class NotFound(ShopError): pass
class CapacityExceeded(ShopError): pass

try:    x = self.d[k]
except KeyError:
    raise NotFound(f"no item {k}") from None      # `from None` kills the chain
```

### Entities
```python
from dataclasses import dataclass, field
@dataclass
class User:
    id: str
    name: str
    tags: list[str] = field(default_factory=list)   # NEVER `= []`

@dataclass(frozen=True)          # immutable + hashable -> usable as a dict key
class SpotKey:
    floor: int
    number: int
```

### ABC
```python
from abc import ABC, abstractmethod
class Policy(ABC):
    @abstractmethod
    def apply(self, x) -> int: ...      # `pass` body = a real method returning None!

    @property
    @abstractmethod
    def kind(self) -> Kind: ...         # a subclass CLASS ATTRIBUTE satisfies this
```
ABC with **no** `@abstractmethod` is still instantiable. `Base()` → `TypeError` only when abstract methods remain.

### Collections
```python
from collections import defaultdict, deque, Counter, OrderedDict
d = defaultdict(set); d[k].add(x)      # write
d.get(k, set())                        # READ (defaultdict reads create keys!)
dq = deque(maxlen=100); dq.appendleft(x); dq.popleft()
Counter(items).most_common(3)
od.move_to_end(k); od.popitem(last=False)

lst.remove(x)          # STATEMENT — mutating methods return None
sorted(lst, key=lambda t: (-t.score, t.name))     # multi-key, mixed direction
next((x for x in xs if p(x)), None)               # first match or None
sum(1 for x in xs if p(x))                        # count without a list
for k, v in d.items(): ...
```

### heapq
```python
import heapq
from itertools import count
seq = count()
heapq.heappush(h, (priority, next(seq), obj))     # tiebreaker!
p, _, obj = heapq.heappop(h)
h[0]                          # peek, O(1)
heapq.heapify(lst)            # O(n)
heapq.heapreplace(h, x)       # pop then push
heapq.nlargest(k, xs, key=...)
# max-heap: push -value
```

### datetime
```python
from datetime import datetime, timedelta
delta = t2 - t1
delta.total_seconds()          # USE THIS. `.seconds` is the remainder after days!
now + timedelta(minutes=5, hours=1)
now.replace(second=0, microsecond=0)      # bucket to the minute
now.weekday()                  # Mon=0 .. Sat=5, Sun=6
math.ceil(delta.total_seconds() / 3600)   # hours, rounded up
```

### threading
```python
import threading
lock = threading.Lock() / RLock()
with lock: ...

cond = threading.Condition()
with cond:
    while not predicate():     # WHILE, never if
        cond.wait()            # releases the lock while sleeping
with cond:
    change(); cond.notify_all()

cond.wait(timeout)             # returns early if notified — the scheduler trick
threading.Event()              # .set() .is_set() .wait(t) — one-shot flag
threading.Semaphore(3) / BoundedSemaphore(3)

from queue import Queue, Empty, Full
q = Queue(maxsize=100)
q.put(x) / q.put_nowait(x) / q.get(timeout=1) / q.task_done() / q.join()

from concurrent.futures import ThreadPoolExecutor, as_completed
with ThreadPoolExecutor(max_workers=4) as pool:
    for f in as_completed([pool.submit(fn, x) for x in xs]):
        f.result()             # exceptions surface HERE, silent otherwise
```

### Test harness (12 lines — write it, don't skip it)
```python
P = F = 0
def ok(label, cond):
    global P, F
    if cond: P += 1; print(f"PASS  {label}")
    else:    F += 1; print(f"FAIL  {label}")
def raises(label, exc, fn):
    try: fn(); ok(label, False)
    except exc: ok(label, True)
# ... at the end:
print(f"{P} passed, {F} failed")
```

---

## 5. Edge case checklists

### Universal — write these at minute 10
```
1.  resource full / none available
2.  duplicate entry (same id/plate/key twice)
3.  unknown id (get, update, delete)
4.  double release / double confirm / double return
5.  operation on an unassigned or unowned entity
6.  zero / negative / empty-list inputs
7.  limit boundary: n-1, n, n+1
8.  state fully restored after a create→release cycle
```

### Per-archetype additions
| Archetype | Also test |
|---|---|
| Allocation | smallest-fit correct; fallback to a larger size; release returns to the right pool |
| State machine | every illegal transition; terminal state; same-state no-op |
| Capacity | own item doesn't count against itself; freeing a slot re-enables |
| Expiry | exactly at the boundary; expired item is invisible everywhere, not just on write |
| Rate limit | first request ever; exact limit; window rollover; burst→idle→burst |
| Cache | put on existing key when full (must not evict); capacity 1; capacity 0 rejected |
| Money | exact payment; change impossible → full refund, nothing moved; conservation invariant |
| Concurrency | N threads on a barrier; final value == true max; no lost update |
| Scheduler | earlier task scheduled after a later one; a throwing task; stop() while idle |
| Event bus | a handler throws; a handler subscribes during publish; unsubscribe |

---

## 6. Complexity

| | list | deque | set | dict | heap |
|---|---|---|---|---|---|
| `x in c` | **O(n)** | O(n) | **O(1)** | **O(1)** | O(n) |
| append / add / push | O(1)* | O(1) | O(1) | O(1) | O(log n) |
| pop from end | O(1) | O(1) | O(1) arb. | — | — |
| pop from front / min | **O(n)** | **O(1)** | — | — | **O(log n)** |
| peek min | O(n) | O(1) | — | — | **O(1)** |
| remove by value | **O(n)** | O(n) | **O(1)** | **O(1)** | **not supported** |
| index access | **O(1)** | O(n) | — | — | — |

\* amortised. `heapify` is **O(n)**. `nlargest(k)` is O(n log k). `s += x` in a loop is O(n²) → `"".join(parts)`.
`OrderedDict.move_to_end` / `popitem` = O(1).

**A block's complexity is its slowest part.** An O(1) guard in front of an O(n) loop is still O(n).

---

## 7. Lines to say

**Complexity (as you type each signature):**
> "O(k) in that user's items, not O(N) total — O(1) extra space per assignment buys it."
> "O(sizes × floors) — configuration constants, so it doesn't grow with the data."

**Design:**
> "Dict not if/elif — adding a type is a data change, and unknowns fail loudly."
> "The spec says this policy changes, so the core takes the interface, not the implementation."
> "Base class holds the algorithm, subclass overrides the table — it resolves through the MRO."
> "Two paths reach this state change, so the guard lives in one helper. Otherwise one becomes a bypass."
> "Availability is derived from status and expiry — I'm not storing a second flag that can drift."

**Concurrency:**
> "One lock spanning check and act — two separate blocks would be a TOCTOU race."
> "Per-auction lock rather than one global, so bids on different items don't serialise."
> "The GIL protects interpreter state, not my multi-step logic — `x += 1` still needs a lock."
> "I'm bounding the queue so a fast producer blocks instead of exhausting memory. That's backpressure."

**Scoping:**
> "I'm assuming X — tell me if that's wrong."
> "Not building Y. I'd add it, but it's out of scope for these operations."
> "This is O(n) today; I'd swap in a heap if we cared about nearest-first. Flagging it, moving on."

**Close (minute 55):**
> "Working and tested: … Verified edge cases: … Complexities: … Deliberately not built: … If multi-threaded, the race is at *this line*, fixed with *this*."

Naming your own gaps first is the strongest close available.

---

## 8. My 6 traps

1. **Check the actual rule, not a proxy.** Auction: I checked `UserType`; the rule was *ownership*. Re-read each stated rule: "am I checking this, or something that resembles it?"
2. **Validate before you mutate.** Vending set `DISPENSING` before validating → machine bricked. Cache evicted before checking if the key existed. Guards go **above** the state change.
3. **Every exception class I define must actually be raised.** Four written-but-never-raised across four problems.
4. **Time-dependent status is derived, never stored.**
5. **Every input parameter must be stored.** `item_name` was accepted and dropped on the floor.
6. **Delete unrecognised imports before the first run.** `shutil.Error`, `asyncio.Server`… five times. Twenty seconds.

**Plus:** `list.remove()` returns `None` — never assign it. `defaultdict` reads create keys. Never return the live internal collection.
