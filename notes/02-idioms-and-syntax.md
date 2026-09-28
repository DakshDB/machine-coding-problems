# Python Idioms & Syntax Refresher

The things that stop being automatic when you've been away from the keyboard.

---

## Truthiness and None

```python
if x is None:          # identity - ALWAYS use this for None
if x == None:          # works, but wrong idiom; flagged in review
if not x:              # careful! true for None, 0, "", [], {}, set(), False
```

The distinction bites in real code:

```python
count = d.get(key)          # could be 0 or None
if not count:               # WRONG - treats 0 and None the same
if count is None:           # right
```

Falsy values: `None  False  0  0.0  ""  []  {}  set()  ()  range(0)`

```python
if not free_spots:          # idiomatic "empty check" on a collection
if len(free_spots) == 0:    # noisier, same thing
```

---

## Iteration idioms

```python
for i, item in enumerate(items):              # index + value
for i, item in enumerate(items, start=1):     # 1-based

for a, b in zip(xs, ys):                      # parallel, stops at shortest
for k, v in d.items():                        # dict pairs

for x in reversed(items):
for x in sorted(items, key=lambda t: t.created_at):
for x in sorted(items, key=lambda t: (t.priority, t.name)):   # multi-key
```

```python
any(t.status == OPEN for t in tasks)          # short-circuits
all(s.is_occupied for s in spots)
sum(1 for t in tasks if t.is_open)            # count matching
next((t for t in tasks if t.id == tid), None) # first match or None
max(items, key=lambda x: x.score)
min(items, key=lambda x: x.score, default=None)
```

`sum(1 for ... if ...)` is the idiomatic "count where", and it avoids building a
list — you wrote list comprehensions then took `len()` of them, which works but
allocates.

---

## Unpacking

```python
a, b = b, a                      # swap
first, *rest = items
*init, last = items
a, (b, c) = 1, (2, 3)

def f(*args, **kwargs): ...
f(*my_list)
f(**my_dict)

merged = {**defaults, **overrides}
combined = [*a, *b]
```

---

## f-strings (formatting for readable output)

```python
f"{name}"
f"{value:.2f}"          # 2 decimal places
f"{n:>8}"               # right-align width 8
f"{n:<8}"               # left-align
f"{n:^8}"               # centre
f"{n:,}"                # 1,234,567
f"{pct:.1%}"            # 0.85 -> 85.0%
f"{obj!r}"              # repr() instead of str()
f"{x=}"                 # prints "x=5" - great for debugging
```

That last one is the fastest debug print you can type.

---

## Slicing

```python
xs[a:b]        xs[:b]        xs[a:]        xs[:]
xs[::2]        # every 2nd
xs[::-1]       # reversed copy
xs[-3:]        # last 3
```

Slices never raise on out-of-range: `[1,2,3][10:20]` is `[]`.

---

## Ternary and short-circuit

```python
status = "open" if not t.assignee else "assigned"
value = maybe or default          # careful: 0 and "" are falsy
value = maybe if maybe is not None else default    # safer
```

Walrus, for when you'd otherwise call something twice:

```python
if (spot := self._find_spot(v)) is not None:
    return spot
```

---

## Sorting with keys

```python
items.sort(key=lambda x: x.name)                    # in place, returns None
ranked = sorted(items, key=lambda x: -x.score)      # descending
ranked = sorted(items, key=lambda x: (x.floor, x.number))   # tuple = multi-key
ranked = sorted(items, key=lambda x: (-x.score, x.name))    # mixed direction

from operator import attrgetter, itemgetter
sorted(items, key=attrgetter('score'))
sorted(pairs, key=itemgetter(1))
```

Python's sort is **stable** — equal keys keep their original order, so you can
sort twice for a compound ordering.

---

## Type hints (enough to look fluent)

```python
def f(x: int, name: str = "") -> bool: ...

tasks: dict[str, Task] = {}
ids: list[str] = []
free: dict[SpotSize, set[Spot]] = {}
pairs: tuple[int, str] = (1, "a")

from typing import Optional
spot: Optional[Spot] = None          # or:  Spot | None   (3.10+)

from typing import Callable, Iterable, Any
handler: Callable[[str, int], bool]

from typing import ClassVar
class C:
    registry: ClassVar[dict] = {}    # marks it as class-level, not a field
```

You wrote `dict[str, [uuid4]]` — that isn't valid. Inside the brackets you need
**types**, not values: `dict[str, list[str]]`.

Hints are not enforced at runtime. They're for the reader (and the interviewer).

---

## String methods worth remembering

```python
s.strip()  s.lstrip()  s.rstrip()
s.split(",")   s.rsplit(",", 1)   s.splitlines()
",".join(parts)                   # NOT "".join for csv
s.startswith("x")  s.endswith("y")
s.replace(a, b)
s.lower()  s.upper()  s.title()
s.zfill(3)          # "7" -> "007"
s.isdigit()  s.isalpha()
```

---

## Files, context managers, and `with`

```python
with open(path) as f:
    data = f.read()
```

Write your own when a resource needs cleanup (a lock, a transaction):

```python
from contextlib import contextmanager

@contextmanager
def acquired(lock):
    lock.acquire()
    try:
        yield
    finally:
        lock.release()
```

---

## Modules and imports

```python
from models.task import Task, TaskStatus, TaskType     # group them on one line
from models import constants
import math
```

Rules that keep you out of trouble:

- **Never name a module after a stdlib module** (`enum.py`, `types.py`,
  `string.py`, `json.py`). You did this with `models/enum.py`.
- Circular imports: if A imports B and B imports A, split the shared piece into a
  third module (that's what `models/enum.py` and `exceptions.py` are for).
- `__init__.py` is optional in Python 3, but adding empty ones makes packages
  explicit and avoids surprises.
- Import order convention: stdlib, then third-party, then local — blank line
  between groups.

---

## Naming conventions (free marks)

```python
module_name.py        snake_case
ClassName             PascalCase
function_name()       snake_case
variable_name         snake_case
CONSTANT_NAME         UPPER_SNAKE
_private_helper()     leading underscore
__dunder__            reserved, don't invent your own
```

You mixed `taskType` / `entryTime` / `taskBoardPreview` into otherwise
snake_case code, and used `PascalCase` for constants. Costs nothing to fix.

---

## Quick debugging without a debugger

```python
print(f"{spot=} {free=}")           # prints names and values
import pprint; pprint.pprint(obj)
breakpoint()                        # drops into pdb: n=next c=continue p=print q=quit
```

If they ask you to debug live, `breakpoint()` plus `p variable` is enough to look
competent. `assert` is also fine for quick invariant checks while building.
