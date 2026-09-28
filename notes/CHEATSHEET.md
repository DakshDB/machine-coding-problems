# Machine Coding — Final Card

## The clock

| Min | Do |
|---|---|
| 0–5 | Restate. 3 assumptions out loud. 1–2 scoping questions. Then stop asking. |
| 5–10 | enums → entities → **exceptions** → skeleton |
| 10–15 | Method signatures + edge-case block. **Say complexity as you type each signature.** |
| 15–45 | Implement. Narrate decisions, not syntax. |
| 45–55 | **Stop building. Run the edge-case list.** Fix what breaks. |
| 55–60 | Complexities, assumptions, known gaps, concurrency answer. |

Behind at 35? Cut a feature and **say you're cutting it**. Deliberate scope cuts score; silent overruns don't.

---

## Your 6 traps (from 8 problems)

1. **Check the actual rule, not a proxy.** Auction: you checked `UserType`, the rule was *ownership*. Re-read each stated rule and ask "am I checking this, or something that resembles it?"
2. **Validate before you mutate.** Vending set `DISPENSING` before validating the code → machine bricked. Cache evicted before checking if the key existed. Guards go **above** the state change.
3. **Every exception class you define must actually be raised.** `BookNotFound`, `InvalidDenomination`, `SellerCantBuy`, `BidShouldBeGreaterThanLastBid` — all written, none raised. Four times.
4. **Status that depends on time is derived, not stored.** Don't keep both a flag and the timestamp it's computed from.
5. **Every input parameter must be stored.** `item_name` was accepted and dropped on the floor.
6. **Delete unrecognised imports before the first run.** `shutil.Error`, `shutil.ExecError`, `warnings.catch_warnings`, `ast.Expr`, `asyncio.Server`. Five times. 20 seconds.

---

## Skeleton (type from memory, ~8 min)

```
models/enums.py        NOT enum.py
models/entities.py
models/exceptions.py   one root, 4-5 children — write FIRST
core/<policy>.py       the strategy, if there is one
core/service.py        orchestration, guards, indexes
main.py                only file with print()
```

---

## Snippets

**Exceptions — one root**
```python
class ShopError(Exception): pass
class NotFoundError(ShopError): pass
class CapacityError(ShopError): pass
```
```python
try:    x = self.items[k]
except KeyError:
    raise NotFoundError(f"no item {k}") from None
```

**Strategy — ABC, instance, wide signature**
```python
class Pricing(ABC):
    @abstractmethod
    def price(self, order, at: datetime) -> int: ...   # pass the OBJECT, not one field

class Service:
    def __init__(self, pricing: Pricing = None):
        self.pricing = pricing or StandardPricing()     # NO () on the param
```
Test: name the 2nd and 3rd implementation. Can the signature express them?

**Registry — never if/elif on a type**
```python
REGISTRY = {Type.A: ClassA, Type.B: ClassB}
cls = REGISTRY.get(t)
if cls is None: raise UnknownTypeError(f"unsupported: {t!r}")
```

**Transition table — base holds algorithm, subclass overrides data**
```python
class Task(ABC):
    TRANSITIONS = {OPEN: {IN_PROGRESS, DELAYED}, IN_PROGRESS: {RESOLVED}, RESOLVED: set()}
    def update(self, new):
        if new == self.status: return
        allowed = self.TRANSITIONS[self.status]
        if new not in allowed: raise InvalidTransitionError(...)
        self.status = new

class Bug(Task):
    TRANSITIONS = {**Task.TRANSITIONS, OPEN: {IN_PROGRESS, RESOLVED, DELAYED}}
```
⚠ `{**Base.T, k: v}` builds a NEW dict. Never `Base.T[k].add(x)`.

**Indexes — must return the thing you act on**
```python
by_user = defaultdict(set)        # by_user[uid].add(task_id)
free    = defaultdict(set)        # spot = free[size].pop()  O(1), len() IS the count
seen    = set()                   # duplicate guard
lst.remove(x)                     # STATEMENT. never `lst = lst.remove(x)`
d.get(k, set())                   # on READ paths — defaultdict read creates keys
return list(self._internal)       # never hand back the live collection
```

**Clock**
```python
def __init__(self, clock=datetime.now): self._clock = clock
# test:  Service(clock=lambda: datetime(2026,9,7,10,0))
```

**Lock — one span over check AND act**
```python
with self._lock:
    if not self._valid(x): raise ...
    self._mutate(x)
```
Two separate `with` blocks = TOCTOU. Per-resource lock beats one global lock.

**Test helper**
```python
def ok(l, c): print(f"{'PASS' if c else 'FAIL'}  {l}")
def raises(l, exc, fn):
    try: fn(); print(f"FAIL  {l}: no error")
    except exc: print(f"PASS  {l}")
```

---

## Edge cases (write at min 10, run at min 45)

```
1. resource full / none available
2. duplicate entry (same id twice)
3. unknown id
4. double release / double confirm / double return
5. operation on an unassigned or unowned entity
6. zero / negative / boundary values
7. limit boundary: n-1, n, n+1
8. state fully restored after a create→release cycle
```

---

## Complexity

| | list | deque | set | dict |
|---|---|---|---|---|
| `x in c` | **O(n)** | O(n) | **O(1)** | **O(1)** |
| append/add | O(1)* | O(1) | O(1) | O(1) |
| pop(0)/popleft | **O(n)** | **O(1)** | — | — |
| remove by value | **O(n)** | O(n) | **O(1)** | **O(1)** |

heapq push/pop O(log n), peek O(1). `s += x` in a loop is O(n²) → `"".join(parts)`.

**A block's complexity is its slowest part.** A fast guard in front of a slow loop is still slow.

---

## Say these

> "O(k) in that user's items, not O(N) total — O(1) extra space per assignment buys it."

> "Two paths reach this state change, so the guard lives in one helper. Otherwise one becomes a bypass."

> "Dict not if/elif — adding a type is a data change, and unknowns fail loudly."

> "The spec says this policy changes, so the core takes the interface, not the implementation."

> "I'm assuming X. Not building Y — I'd add it, out of scope for these operations."

> "The race is between the check and the write; one lock spanning both fixes it. The GIL doesn't help — it protects interpreter state, not my multi-step logic."

---

## Close (minute 55)

> "Working and tested: [list]. Verified edge cases: [list]. Complexities: [one line each].
> Deliberately not built: [list] — here's what I'd add first.
> If multi-threaded, the race is at [exact line], fixed with [approach]."

**Naming your own gaps first is the strongest close available.**

---

## Last 60 seconds

Working and explained beats clever and silent. Never quiet >30s — "give me twenty seconds to think about the data model" is fine. Debugging out loud is a **positive** signal: state the hypothesis, then check it.
