# OOP in Python — What LLD Rounds Actually Test

---

## Class vs instance attributes (you got this wrong)

```python
class TaskCore:
    tasks = {}                 # CLASS attribute - ONE dict shared by all instances

a, b = TaskCore(), TaskCore()
a.tasks['x'] = 1
b.tasks                        # {'x': 1}  <- leaked
```

```python
class TaskCore:
    MAX_IN_PROGRESS = 3        # fine: immutable, genuinely shared config

    def __init__(self):
        self.tasks = {}        # correct: per-instance mutable state
```

**Rule: mutable + per-object → `__init__`. Immutable config → class body.**

The subtlety that makes class attributes *useful* is lookup order: Python checks
the instance, then the class, then base classes. That's exactly what makes the
transition-table pattern work.

---

## method / classmethod / staticmethod

```python
class C:
    def instance_method(self):        # needs an object; first arg is self
        ...

    @classmethod
    def from_config(cls, cfg):        # first arg is CLS; alternate constructor
        return cls(cfg['a'])

    @staticmethod
    def helper(x):                    # no self, no cls; just namespaced
        return x * 2
```

You wrote `@classmethod def create_task(self, ...)` — that runs, because the
decorator passes the class in whatever you name the first parameter, but it reads
as confusion. `@classmethod` is for alternate constructors and registry access;
normal behaviour is an instance method.

---

## Inheritance and `super()`

```python
class Task:
    def __init__(self, id, title):
        self.id = id
        self.title = title

class BugTask(Task):
    def __init__(self, id, title, severity):
        super().__init__(id, title)      # always call it
        self.severity = severity
```

**MRO (method resolution order)** — how Python finds an attribute:

```python
BugTask.__mro__     # (BugTask, Task, object)
```

It checks the actual class first, then walks up. This is *why* a base-class method
that reads `self.TRANSITIONS` automatically picks up a subclass's override. Say
that sentence in the interview; it shows you know why the pattern works.

### Real inheritance vs decorative inheritance

```python
# decorative - subclasses add nothing but a label
class BugTask(Task):
    def __init__(self, ...):
        super().__init__(...)
        self.task_type = TaskType.BUG

# real - base holds the algorithm, subclasses supply the data
class Task(ABC):
    TRANSITIONS = {OPEN: {IN_PROGRESS, DELAYED}, ...}

    def update_status(self, new):
        if new not in self.TRANSITIONS[self.status]:
            raise InvalidTransitionError(...)
        self.status = new

class BugTask(Task):
    task_type = TaskType.BUG
    TRANSITIONS = {**Task.TRANSITIONS, OPEN: {IN_PROGRESS, RESOLVED, DELAYED}}
```

**Prefer composition when the thing varies independently** — pricing isn't a *kind
of* parking lot, so it's an injected object, not a subclass.

---

## Abstract base classes

```python
from abc import ABC, abstractmethod

class Task(ABC):
    @property
    @abstractmethod
    def task_type(self) -> TaskType: ...

    @abstractmethod
    def calculate(self) -> int: ...
```

```python
Task()          # TypeError: Can't instantiate abstract class
```

**`ABC` with no `@abstractmethod` is not abstract** — the class stays perfectly
instantiable. You did this; add at least one abstract member or it's decoration.

A plain class attribute in a subclass satisfies an abstract property:

```python
class BugTask(Task):
    task_type = TaskType.BUG    # this is enough
```

---

## Dunder methods worth knowing

```python
class Spot:
    def __init__(self, id, size):
        self.id, self.size = id, size

    def __repr__(self):                     # ALWAYS write this - debugging gold
        return f"Spot(id={self.id!r}, size={self.size.value})"

    def __eq__(self, other):
        if not isinstance(other, Spot):
            return NotImplemented
        return self.id == other.id

    def __hash__(self):                     # REQUIRED if you define __eq__
        return hash(self.id)                # and want set/dict membership

    def __lt__(self, other):                # enables sorted() and heapq
        return self.id < other.id
```

**The trap:** defining `__eq__` sets `__hash__` to `None`, making your objects
unhashable — they can no longer go in a `set` or be dict keys. If you put objects
in a set (like free parking spots), either define both or define neither and rely
on identity hashing.

Others: `__str__` (user-facing), `__len__`, `__contains__` (`in`), `__iter__`,
`__getitem__`, `__call__`, `__enter__`/`__exit__` (context manager).

---

## dataclasses — free boilerplate

```python
from dataclasses import dataclass, field

@dataclass
class User:
    id: str
    name: str
    email: str = ""
    tags: list[str] = field(default_factory=list)   # never `= []`

@dataclass(frozen=True)     # immutable + hashable -> usable in sets/dict keys
class SpotKey:
    floor: int
    number: int

@dataclass(order=True)      # adds __lt__ etc for sorting
class Priority:
    rank: int
```

Gives you `__init__`, `__repr__`, `__eq__` free. Use for entities with no
behaviour (User, Vehicle, Ticket). Use a normal class when there's real logic.

---

## Properties

```python
class Ticket:
    @property
    def is_active(self) -> bool:
        return self.exit_time is None

    @property
    def duration(self):
        return (self.exit_time or datetime.now()) - self.entry_time
```

Computed attributes with no parentheses at the call site. Prefer them over
`get_x()` for simple derived values.

---

## Enums

```python
from enum import Enum, auto

class TaskStatus(Enum):
    OPEN = 'open'
    IN_PROGRESS = 'in_progress'

TaskStatus.OPEN                 # <TaskStatus.OPEN: 'open'>
TaskStatus.OPEN.value           # 'open'
TaskStatus.OPEN.name            # 'OPEN'
TaskStatus('open')              # lookup by value
list(TaskStatus)                # iterate all members
```

**The bug you wrote:**

```python
if task_type.STORY:              # attribute access on the member. ALWAYS True.
if task_type == TaskType.STORY:  # comparison - what you meant
```

Enum members are singletons, so `is` also works. They're hashable, which makes
them perfect dict keys — which is the whole basis of the registry and transition
table patterns.

`auto()` assigns values for you when the value doesn't matter. `IntEnum` compares
with ints if you need ordering.

---

## SOLID — say these words, they're the vocabulary of the round

| | Meaning | In your code |
|---|---|---|
| **S**ingle responsibility | one reason to change | pricing left `ParkingLotCore` and became its own class |
| **O**pen/closed | extend without editing | registry dict: add a type = add a row |
| **L**iskov substitution | subclass must honour the base contract | `BugTask` widens allowed transitions, never breaks `update_status` |
| **I**nterface segregation | small focused interfaces | `PricingStrategy` has exactly one method |
| **D**ependency inversion | depend on abstractions | core takes `PricingStrategy`, not `SlabPricing` |

You don't need to lecture. One well-placed sentence — *"I'm injecting the strategy
so the core depends on the interface, not the concrete pricing"* — is worth more
than reciting all five.

---

## Composition over inheritance — how to decide

Ask: **"is-a" or "has-a"?**

- A `BugTask` **is a** `Task` → inheritance.
- A `ParkingLot` **has a** pricing policy → composition (inject it).

If you find yourself writing a subclass that only overrides one method to change a
constant or a rule, you probably wanted data (a table) or an injected object.
