# Standard Library Toolkit

What actually comes up in a 60-minute LLD round.

---

## datetime — every booking/parking/rental problem

```python
from datetime import datetime, timedelta, date, timezone

now   = datetime.now()
fixed = datetime(2026, 9, 7, 16, 0, 0)          # deterministic, for tests
utc   = datetime.now(timezone.utc)

delta = exit_time - entry_time                   # a timedelta
delta.total_seconds()                            # float seconds  <- use this
delta.days, delta.seconds                        # NOT total; .seconds is the remainder
later = now + timedelta(hours=3, minutes=30)

now.weekday()      # Mon=0 ... Sat=5, Sun=6
now.isoformat()
now.strftime("%Y-%m-%d %H:%M")
datetime.strptime("2026-09-07", "%Y-%m-%d")
```

**Trap:** `delta.seconds` is the leftover after whole days, so a 25-hour delta has
`.days == 1, .seconds == 3600`. For total elapsed always use `.total_seconds()`.

**Rounding hours up:**

```python
import math
hours = math.ceil(delta.total_seconds() / 3600)
```

### Make time injectable — this is a senior signal

```python
class ParkingLot:
    def __init__(self, clock=datetime.now):
        self._clock = clock

    def park(self, v):
        return Ticket(entry_time=self._clock())

lot = ParkingLot(clock=lambda: datetime(2026, 9, 7, 10, 0))   # deterministic
```

Alternative (what you did): accept `exit_time=None` and default to `now()`. Both
work; the injected clock also controls *entry* time, which the parameter doesn't.
Either way, **say why**: "so fee calculation is testable without waiting hours."

---

## enum

```python
from enum import Enum, auto, IntEnum

class Status(Enum):
    OPEN = 'open'
    CLOSED = auto()          # auto-assigns

Status.OPEN.value / .name
Status('open')               # by value
list(Status)                 # all members
```

Members are singletons and hashable → ideal dict keys. Compare with `==`, never
`status.OPEN`.

---

## uuid

```python
from uuid import uuid4
str(uuid4())            # '3f2b...'  <- wrap in str()
str(uuid4())[:8]        # short id for readable demo output
```

Alternative for readable ids in a demo: `itertools.count`.

```python
from itertools import count
_ids = count(1)
spot_id = f"S{next(_ids)}"
```

---

## collections

```python
from collections import defaultdict, Counter, deque, OrderedDict, namedtuple

defaultdict(list) / defaultdict(set) / defaultdict(int)
Counter(items).most_common(3)
deque(maxlen=100)
```

`OrderedDict` still has `move_to_end()` and `popitem(last=False)`, which is why it
shows up in hand-rolled LRU caches.

---

## heapq

```python
import heapq
heapq.heappush(h, (dist, spot_id))
dist, spot_id = heapq.heappop(h)
heapq.nsmallest(3, items, key=lambda x: x.score)
```

Min-heap only; negate for max. Great for "nearest spot", "next departure",
"top N".

---

## itertools

```python
from itertools import count, groupby, chain, combinations, product, islice

chain(a, b)                       # flatten two iterables
islice(gen, 10)                   # take first 10 lazily
combinations(items, 2)            # all pairs
product(sizes, floors)            # cartesian product - replaces nested loops
```

`groupby` requires the input to be **sorted by the same key** — common mistake.

---

## functools

```python
from functools import lru_cache, cached_property, reduce, partial

@lru_cache(maxsize=None)
def fib(n): ...

class Report:
    @cached_property
    def total(self): return expensive()

partial(func, arg1)               # pre-bind arguments
```

`@lru_cache` is a one-line memoisation answer if they ask about repeated
computation.

---

## bisect — sorted list operations in O(log n)

```python
import bisect
bisect.insort(sorted_list, x)          # insert keeping order
i = bisect.bisect_left(sorted_list, x) # index where x would go
```

Useful for time-windowed data (rate limiters, leaderboards).

---

## threading — for the concurrency follow-up

You almost certainly won't implement it, but you must be able to *talk* about it.

```python
import threading

lock = threading.Lock()

with lock:                      # only one thread inside at a time
    spot = free[size].pop()

rlock = threading.RLock()       # re-entrant: same thread can acquire twice
sem   = threading.Semaphore(3)  # allow N concurrent
```

**The check-then-act race** — the exact shape of your `_find_spot`:

```python
if free_count > 0:          # thread A and B both see 1
    spot = take_spot()      # both take it -> double allocation
```

The fix is to make check-and-claim a **single atomic operation**:

```python
with self._lock:
    spot = floor.take(size)     # check and claim together
```

Higher-level answers worth naming: optimistic locking with a version number,
a database unique constraint, compare-and-swap, or a single-threaded actor/queue
owning the resource. Also mention that **Python's GIL doesn't save you** — it
protects interpreter internals, not your multi-step business logic.

---

## typing

```python
from typing import Optional, ClassVar, Callable, Iterable, Protocol

Optional[Spot]        # or  Spot | None   (3.10+)
ClassVar[dict]        # class-level, not an instance field
Callable[[int, str], bool]

class Pricing(Protocol):          # structural typing - no inheritance needed
    def calculate_fare(self, ...) -> int: ...
```

`Protocol` is the duck-typed alternative to ABC — nice to mention, ABC is safer to
actually use in an interview.

---

## Testing without a framework

```python
def check(label, fn, expect):
    got = fn()
    print(f"{'PASS' if got == expect else 'FAIL'}  {label}: {got}")

def expect_raises(label, exc, fn):
    try:
        fn(); print(f"FAIL  {label}: no error")
    except exc:
        print(f"PASS  {label}")
```

Twelve lines, no dependencies, and it turns "I hope this works" into evidence. If
`unittest` is allowed and you're fast with it, use it — otherwise this is enough.

```python
import unittest

class TestLot(unittest.TestCase):
    def setUp(self): self.lot = ParkingLot()
    def test_full(self):
        with self.assertRaises(LotFullError):
            ...
# unittest.main()
```
