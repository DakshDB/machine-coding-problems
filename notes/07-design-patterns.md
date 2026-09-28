# Design Patterns for Machine Coding

You need maybe six. Know these cold; recognise the rest.

**The meta-rule you keep missing:** when logic is really a *lookup*, make it a
lookup. Transition rules → dict. Type dispatch → dict. Both times the `if/elif`
chain was the bug.

---

## 1. Strategy — the one you skipped

**When:** a policy that the spec says will change. Pricing, splitting, eviction,
allocation, matching, discounting, ranking.

**Trigger words:** "swappable", "configurable", "different rules for X and Y",
"management changes this often", "without modifying existing code", "pluggable".

```python
class PricingStrategy(ABC):
    @abstractmethod
    def calculate_fare(self, vehicle_type, entry, exit) -> int: ...

class SlabPricing(PricingStrategy):
    def calculate_fare(self, vehicle_type, entry, exit): ...

class FlatRatePricing(PricingStrategy):
    def __init__(self, rate): self.rate = rate
    def calculate_fare(self, vehicle_type, entry, exit): ...

class ParkingLot:
    def __init__(self, pricing: PricingStrategy = None):
        self.pricing = pricing or SlabPricing()      # injected, with a default

    def unpark(self, ticket_id, exit_time):
        ...
        return self.pricing.calculate_fare(...)      # delegates, never computes
```

**The tell that you need it:** a method *computes* a policy instead of
*delegating* it. Ask: "could I construct this with a different policy and change
nothing else?"

**Strategies compose** — this is worth showing:

```python
class WeekendPricing(PricingStrategy):
    def __init__(self, base, multiplier=1.5):
        self.base, self.multiplier = base, multiplier
    def calculate_fare(self, *args):
        return round(self.base.calculate_fare(*args) * self.multiplier)

WeekendPricing(SlabPricing(), 1.5)      # wraps any other strategy
```

Keep strategies **pure** — pass timestamps in, don't let them call `datetime.now()`.

---

## 2. Factory / Registry — replaces if/elif type switches

```python
TASK_REGISTRY = {
    TaskType.FEATURE: FeatureTask,
    TaskType.BUG:     BugTask,
    TaskType.STORY:   StoryTask,
}

def create_task(self, task_type, title, creator):
    cls = TASK_REGISTRY.get(task_type)
    if cls is None:
        raise UnknownTaskTypeError(f"unsupported: {task_type!r}")
    task = cls(id=str(uuid4()), title=title, creator=creator)
    self.tasks[task.id] = task
    return task
```

Adding a type is a **data change**, not a code change (Open/Closed). And there's
no branch to get wrong — which is exactly how `elif task_type.STORY:` slipped past
you.

Advanced (mention, don't build under time pressure) — self-registration:

```python
class Task(ABC):
    registry: ClassVar[dict] = {}
    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)
        Task.registry[cls.task_type] = cls
```

---

## 3. State machine via transition table

**When:** anything with a lifecycle. Task status, order status, ticket, booking,
vending machine, elevator doors.

```python
class Task(ABC):
    TRANSITIONS = {
        OPEN:        {IN_PROGRESS, DELAYED},
        IN_PROGRESS: {RESOLVED, DELAYED},
        DELAYED:     {OPEN, IN_PROGRESS},
        RESOLVED:    set(),                 # terminal
    }

    def update_status(self, new):
        if new == self.status:
            return                          # idempotent
        allowed = self.TRANSITIONS[self.status]
        if new not in allowed:
            raise InvalidTransitionError(
                f"{type(self).__name__}: {self.status.value} -> {new.value}; "
                f"allowed: {sorted(s.value for s in allowed) or 'none'}")
        self.status = new

class BugTask(Task):
    TRANSITIONS = {**Task.TRANSITIONS, OPEN: {IN_PROGRESS, RESOLVED, DELAYED}}
```

Base holds the **algorithm**; subclasses override the **data**. `self.TRANSITIONS`
resolves through the MRO, so the base method automatically reads the subclass's
table.

You get rules for free that you never wrote — `RESOLVED → OPEN` is blocked because
`RESOLVED`'s set is empty.

⚠ Use `{**Base.TABLE, key: new_set}` to build a **new** dict. Never
`Base.TABLE[key].add(x)` — that mutates the shared base table.

---

## 4. Observer — notifications and decoupled side effects

**When:** "notify", "alert", "when X happens, also do Y", "audit log", "webhook".

```python
class EventBus:
    def __init__(self):
        self._subs = defaultdict(list)

    def subscribe(self, event, handler):
        self._subs[event].append(handler)

    def publish(self, event, payload):
        for handler in self._subs[event]:
            handler(payload)

bus.subscribe("task_assigned", send_email)
bus.subscribe("task_assigned", write_audit_log)
```

Core logic publishes; it doesn't know who listens. Lets you add notifications
without touching business logic.

---

## 5. Repository — separate storage from logic

```python
class TaskRepository:
    def __init__(self):
        self._tasks: dict[str, Task] = {}
        self._by_user: dict[str, set[str]] = defaultdict(set)

    def save(self, task): ...
    def get(self, task_id): ...
    def find_by_user(self, user_id): ...
```

Your service does business rules; the repo does storage and indexes. Makes "how
would you swap in a real database?" a one-sentence answer.

---

## 6. Singleton — know it, usually don't use it

```python
class Config:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

In Python, a module-level object is already a singleton. **Mention it, prefer
dependency injection** — a hidden global is exactly what made your class-level
`tasks = {}` bug possible.

---

## Also worth recognising

| Pattern | One line | Shows up in |
|---|---|---|
| **Builder** | step-by-step construction of a complex object | pizza/burger orders, query builders |
| **Decorator** | wrap to add behaviour | `WeekendPricing`, middleware, rate limits |
| **Command** | encapsulate an action as an object | undo/redo, job queues |
| **Chain of responsibility** | pass along until someone handles it | logging levels, approval flows, middleware |
| **Adapter** | make an incompatible interface fit | payment gateways, third-party APIs |
| **Template method** | base defines skeleton, subclass fills steps | the transition table is a cousin |

---

## Choosing under time pressure

```
Type → class mapping?            registry dict
Lifecycle / status rules?        transition table
Policy that will change?         strategy, injected
"When X, also do Y"?             observer
Storage + indexes?               repository
Complex multi-step construction? builder
```

**Don't over-pattern.** Two well-chosen patterns beat six forced ones. If you use
one, say *why* in a sentence — the reasoning is what's graded, not the name.

---

## Anti-patterns interviewers watch for

- God class doing everything (split by responsibility)
- `if/elif` chains on a type or enum (registry / polymorphism)
- Booleans that encode state (`is_open`, `is_done`, `is_cancelled` → one enum)
- Deep inheritance to vary one value (data or composition instead)
- Business logic mixed with I/O and printing (keep core pure)
- Subclasses that override nothing
