# Observer / Event Bus

The pattern for **"when X happens, also do Y"** — without X knowing anything about Y.

Triggers in a problem statement: *notify, alert, audit log, webhook, subscribe,
when an order ships also…, send an email when…, invalidate the cache when…*

---

## The one idea: invert the dependency

Without it, your core logic accumulates side effects:

```python
def confirm_order(self, order):          # BAD
    order.status = CONFIRMED
    send_email(order)                    # core now depends on email
    send_sms(order)                      # ...and sms
    write_audit_log(order)               # ...and audit
    update_analytics(order)              # every new feature edits this method
```

With it, the core announces a fact and stops caring:

```python
def confirm_order(self, order):          # GOOD
    order.status = CONFIRMED
    self.bus.publish("order.confirmed", order)
```

Adding SMS becomes a **subscription**, not an edit to `confirm_order`. That's
Open/Closed, and it's the sentence to say out loud.

---

## Plain Observer

```python
class Subject:
    def __init__(self):
        self._observers = []

    def attach(self, observer):   self._observers.append(observer)
    def detach(self, observer):   self._observers.remove(observer)

    def notify(self, event):
        for o in list(self._observers):        # copy — see re-entrancy below
            o.update(event)
```

Fine when there's one kind of event. The moment you have several, you want topics.

---

## Event bus — topic-based pub/sub

```python
from collections import defaultdict

class EventBus:
    def __init__(self):
        self._subs = defaultdict(list)

    def subscribe(self, topic, handler):
        self._subs[topic].append(handler)
        return lambda: self._subs[topic].remove(handler)   # unsubscribe token

    def publish(self, topic, payload):
        for handler in list(self._subs.get(topic, [])):    # copy!
            try:
                handler(payload)
            except Exception:
                log_it()                    # isolate: one bad handler must not
                                            # break the others or the publisher
```

Three non-obvious details, and each is a question they'll ask:

**1. Error isolation.** Without the try/except, one throwing subscriber kills the
publish loop — later subscribers never run, and the exception surfaces inside
`confirm_order`, which is exactly the coupling you were removing.

**2. Iterate over a copy.** A handler that subscribes or unsubscribes during
dispatch mutates the list you're iterating. Same trap as `list.remove()` inside a
`for` — silently skipped handlers.

**3. Return an unsubscribe token.** Handlers held in a list are **strong
references**, so a subscriber can never be garbage collected. Long-lived buses leak
unless subscribers can detach. (`weakref.WeakMethod` is the alternative — mention
it, don't build it under time pressure.)

---

## Sync vs async dispatch

| | Synchronous | Asynchronous |
|---|---|---|
| Publisher waits | yes | no |
| Slow handler | blocks the publisher | doesn't |
| Handler throws | caught, logged | caught in the worker |
| Ordering | guaranteed | only per-worker |
| Complexity | trivial | needs a queue + workers |

Synchronous is the right default. **Say why you chose it**, and name the upgrade
path: *"if a handler does I/O I'd hand off to a bounded queue and a worker pool so
a slow email provider can't stall order confirmation."*

---

## The composition — this is the real architecture

Your two gaps join here. **"Design a notification service"** is exactly:

```
domain logic  --publish-->  EventBus  --enqueue-->  bounded Queue  --> WorkerPool
   (fast)                  (routing)                (backpressure)     (slow I/O)
```

```python
class AsyncEventBus:
    def __init__(self, pool, bus):
        self._pool, self._bus = pool, bus

    def publish(self, topic, payload):
        for handler in list(self._bus._subs.get(topic, [])):
            self._pool.submit(handler, payload)     # returns immediately
```

- The **bus** decides *who* cares (routing).
- The **queue** decides *how much* backlog is tolerable (backpressure).
- The **pool** decides *how many* run at once (concurrency).

Three separate concerns, three separate objects. When they ask "how would you scale
this", you point at the seam rather than rewriting.

---

## Ordering, delivery, replay

- **Ordering:** synchronous dispatch preserves subscription order. Async does not,
  unless you shard by key onto a single worker (e.g. all events for one `order_id`
  go to the same worker).
- **Delivery:** in-memory buses are at-most-once — a crash loses events. At-least-once
  needs persistence plus acks, and therefore **idempotent handlers**.
- **Replay / event sourcing:** if you keep the event log, you can rebuild state.
  Worth a sentence; never build it in 60 minutes.

---

## Observer vs the neighbours

| Pattern | Difference |
|---|---|
| **Observer** | subject holds its observers; usually one event type |
| **Event bus** | central broker, topics, publisher and subscriber don't know each other |
| **Chain of responsibility** | passes along until *one* handler consumes it; observer notifies *all* |
| **Mediator** | coordinates two-way interaction; observer is one-way broadcast |
| **Callback / hook** | a single function, not a list; no routing |

---

## What they'll ask

- *A handler throws?* → isolated in try/except, logged, others still run.
- *A handler is slow?* → sync blocks the publisher; hand off to a queue + pool.
- *A handler subscribes during publish?* → iterate over a copy.
- *Memory leak?* → strong refs; return an unsubscribe token or use weak refs.
- *Ordering guarantees?* → sync preserves it; async needs key-based sharding.
- *Event lost on crash?* → in-memory is at-most-once; persistence + acks for more.
- *Infinite loop?* → a handler that publishes the topic it handles; cap depth or forbid it.

---

## Where it shows up

Notification service · order/state-change side effects · audit logging · cache
invalidation · stock price alerts · chat and presence · webhook delivery ·
UI data binding · metrics and analytics collection
