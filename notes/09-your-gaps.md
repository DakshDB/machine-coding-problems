# Your Gap Log

Taken from the actual code you wrote in the Task Tracker and Parking Lot sessions.
Ordered by how much each one costs you.

---

## Theme A — Imports on autopilot (3 occurrences, all sessions)

```python
from shutil import Error          # task tracker
from shutil import ExecError      # parking lot
from warnings import catch_warnings
from ast import Expr
```

You accepted an IDE autocomplete without reading it. `shutil.Error` is an
`OSError` subclass for file operations — raising it for "task not found" is
semantically wrong, and a reviewer reads it as carelessness.

**Fix:** before you run your code the first time, look at your import block and
delete anything you don't recognise. Twenty seconds, every time.

---

## Theme B — Your index answers the wrong question (2 occurrences)

Session 1: no index at all, `get_tasks` scanned every task.
Session 2: you built `free_medium = 4` (a **count**), then still scanned the list
to find *which* spot was free. 60x slowdown as the lot filled.

The question `park_vehicle` asks is *"which one is free"*, not *"how many"*.

**Fix — the rule:** an index must return the thing you're about to act on. If you
have to loop after consulting it, it isn't an index yet.

```python
free: dict[Size, set[Spot]] = {...}   # holds the spots themselves
spot = free[size].pop()               # O(1), and len() is the count for free
```

Bonus: the count stops being a separate fact you maintain, so it can't drift.

---

## Theme C — Mutating methods return None

This caused your single worst bug.

```python
self.user_tasks[uid] = self.user_tasks[uid].remove(task_id)   # sets it to None!
```

`list.remove()`, `.append()`, `.sort()`, `.add()`, `.update()`, `dict.update()`
all mutate in place and return `None`. Never assign their result.

```python
self.user_tasks[uid].remove(task_id)    # correct: statement, not assignment
self.user_tasks[uid].discard(task_id)   # better: no KeyError if absent
```

The blast radius: the index went to `None`, `get_tasks` returned `[]`, and the
capacity limit silently stopped working — a user ended up with 6 in-progress
tasks against a limit of 3. **A broken index does not crash. It lies.**

---

## Theme D — None-safety on optional fields

```python
user_tasks = self.get_tasks(task.assignee)   # assignee can be None -> AttributeError
task.assignee.name                            # same
```

**Fix:** any field that can be `None` gets a guard at the top of the method that
uses it. Decide the rule out loud: "starting an unassigned task is an error."

---

## Theme E — Enum comparison vs attribute access

```python
elif taskType.STORY:              # attribute access. ALWAYS truthy. Never compares.
elif taskType == TaskType.STORY:  # what you meant
```

Invisible with three types because STORY was last. Add a fourth and it silently
mislabels everything. Better still: don't write the branch at all — use a dict
(see Theme I).

---

## Theme F — Class attributes vs instance attributes

```python
class TaskCore:
    tasks: dict = {}              # ONE dict shared by every instance, forever

    @classmethod
    def create_task(self, ...):   # @classmethod's first arg is cls, not self
```

Mutable class attributes are shared state. Two `TaskCore()` objects saw each
other's tasks.

**Fix:** anything mutable and per-object goes in `__init__`. Use `@classmethod`
only for alternate constructors, and name its first parameter `cls`.

---

## Theme G — No exception hierarchy (both sessions)

```python
raise Exception("Parking Spot Not Found")
```

Callers can't distinguish "lot full" from "ticket not found" without matching on
strings. You built a proper hierarchy in the Task Tracker rewrite and then didn't
carry it to the Parking Lot.

**Fix — five lines, write them every time:**

```python
class ParkingError(Exception): pass
class LotFullError(ParkingError): pass
class TicketNotFoundError(ParkingError): pass
```

---

## Theme H — Naming conventions drift

`taskType`, `taskBoardPreview`, `entryTime` (camelCase) mixed with snake_case.
`ParkingFloors`, `SpotsEachFloor` for constants (should be `UPPER_SNAKE`).
`models/enum.py` shadows the stdlib module name.
`_find_spot` mutates state — a "find" that allocates is a naming lie.

Cheap points. Interviewers notice consistency because it's free to get right.

---

## Theme I — You don't reach for the abstraction unprompted

I told you Strategy was the pattern to practise. You wrote `_calculate_fare` as a
private method reading a module-level dict — the exact thing the constraint said
not to do.

**The tell to watch for:** if a method *computes* a policy rather than
*delegating* it, and the spec says the policy will change, you want an injected
object.

```python
def __init__(self, pricing: PricingStrategy = None):
    self.pricing = pricing or SlabPricing()
```

**Trigger phrases in a problem statement** that mean "inject a strategy":
"swappable", "configurable", "management changes this often", "different rules
for X and Y", "without modifying existing code", "pluggable".

---

## Theme J — Smaller repeats

| Slip | Fix |
|---|---|
| `if x == None` | `if x is None` |
| `uuid4()` stored raw | `str(uuid4())` |
| `dict[str, [uuid4]]` | `dict[str, list[str]]` — that wasn't valid typing syntax |
| `defaultdict()` with no factory | `defaultdict(set)` — bare one is just a dict |
| `ABC` with no `@abstractmethod` | the class is still instantiable; add one |
| `self.tasks[id] = task` after mutating | no-op, objects are references |
| `f'free_{size.value}'` as a dict key | nest the dict or make a small class |
| `print()` inside core logic | return data; print only in `main.py` |
| No tests | 10 asserts beats 20 prints |

---

## Pre-flight checklist — read this 5 minutes before you start coding

1. Delete unrecognised imports before the first run.
2. Every mutable collection goes in `__init__`, never on the class body.
3. Exception hierarchy first — 5 lines, before any logic.
4. Ask of every index: *does this return the thing I act on, or just a number?*
5. Never assign the result of a mutating method.
6. Guard every `Optional` field before dereferencing it.
7. Type-switch on an enum? Make it a dict, not `if/elif`.
8. Policy that the spec says will change? Inject it.
9. `is None`, not `== None`. snake_case. `UPPER_SNAKE` for constants.
10. Write the edge-case list **before** the logic. Run it at minute 45.
