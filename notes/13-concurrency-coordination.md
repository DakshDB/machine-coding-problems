# Concurrency Coordination

`Lock` protects state. **`Condition` coordinates *waiting*.** That distinction is
the gap the Delayed Task Scheduler exposed.

Rule of thumb: if a thread ever needs to **wait for something to become true**,
you want a `Condition` (or a `Queue`, or an `Event`) — not a lock plus a sleep loop.

---

## The toolkit, in the order you should reach for it

| Need | Use |
|---|---|
| Protect a few lines of shared state | `threading.Lock` |
| Same, but the method may call itself | `threading.RLock` |
| Producer/consumer hand-off | `queue.Queue` — **already thread-safe, use it** |
| Wait until a condition becomes true | `threading.Condition` |
| Wait for a one-time flag | `threading.Event` |
| Limit concurrency to N | `threading.Semaphore(N)` |
| Run tasks on a pool | `concurrent.futures.ThreadPoolExecutor` |

**Reach for `queue.Queue` before hand-rolling anything.** In an interview, saying
*"I'd use `queue.Queue` in production; here's the `Condition` version to show the
mechanism"* is the strongest framing.

---

## Condition — the whole pattern

```python
import threading

cond = threading.Condition()          # wraps its own Lock by default

# waiter
with cond:                            # must hold the lock to wait
    while not predicate():            # ALWAYS a while, never an if
        cond.wait()                   # releases the lock, sleeps, reacquires on wake
    consume()

# notifier
with cond:
    change_state()
    cond.notify()                     # wake one waiter
    # cond.notify_all()               # wake all
```

Three things that are non-negotiable:

1. **You must hold the lock to call `wait()` or `notify()`.** Hence `with cond:`.
2. **`wait()` releases the lock while sleeping** and reacquires before returning.
   That's the whole point — it's not a busy-wait.
3. **Always loop on the predicate, never `if`.** A woken thread is not guaranteed
   the condition still holds — another thread may have consumed it first, and
   spurious wakeups are permitted. `while` re-checks.

`notify()` vs `notify_all()`: use `notify_all()` unless every waiter is waiting for
exactly the same interchangeable thing. Waking one thread that can't proceed while
another could is a classic lost-wakeup bug.

---

## `wait(timeout)` — how delayed scheduling actually works

This is the piece most people miss. `cond.wait(timeout)` sleeps **at most**
`timeout` seconds but returns early if notified. That gives you a scheduler that is
both punctual and responsive:

```python
import heapq, threading, time
from itertools import count

class DelayedScheduler:
    def __init__(self, clock=None, sleeper=None):
        self._cond = threading.Condition()
        self._heap = []                       # (run_at, seq, fn)
        self._seq = count()
        self._stopped = False
        self._clock = clock or time.monotonic

    def schedule(self, fn, delay):
        with self._cond:
            heapq.heappush(self._heap, (self._clock() + delay, next(self._seq), fn))
            self._cond.notify_all()           # a nearer task may have jumped the queue
    def stop(self):
        with self._cond:
            self._stopped = True
            self._cond.notify_all()

    def run(self):                            # the worker loop
        while True:
            with self._cond:
                while not self._stopped and not self._heap:
                    self._cond.wait()                       # nothing to do: sleep
                if self._stopped:
                    return
                run_at, _, fn = self._heap[0]
                now = self._clock()
                if run_at > now:
                    self._cond.wait(run_at - now)           # sleep until due OR notified
                    continue                                # re-check: the heap may have changed
                heapq.heappop(self._heap)
            try:
                fn()                          # run OUTSIDE the lock
            except Exception:
                log_it()                      # one bad task must not kill the loop
```

Four things to point at when you explain it:

- **The heap gives O(log n) "what's next"**, so the loop never scans.
- **`wait(delay)` not `sleep(delay)`** — a newly scheduled earlier task wakes it
  immediately. `sleep` would make it late.
- **`continue` after the timed wait**, never "assume it's due now" — the heap top
  may have changed while you slept.
- **Run the callback outside the lock.** A slow or throwing task must not block
  every other thread. Wrap it in try/except so one bad task can't kill the loop.

---

## Event — a one-shot flag

```python
stop = threading.Event()
stop.set()          # flip it
stop.is_set()
stop.wait()         # block until set
stop.wait(2.0)      # or until timeout; returns whether it was set
```

Ideal for shutdown signals. Once set it stays set — that's the difference from
`Condition`.

---

## Semaphore — bounded concurrency

```python
sem = threading.Semaphore(3)        # at most 3 at once
with sem:
    do_limited_work()

threading.BoundedSemaphore(3)       # raises if released more times than acquired
```

Use for connection pools, rate-limited workers, "only N downloads at a time".

---

## Queue — the one you should usually reach for

```python
from queue import Queue, PriorityQueue, Empty

q = Queue(maxsize=100)              # blocks producers when full = backpressure
q.put(item)                         # blocks if full
q.get()                             # blocks if empty
q.get(timeout=1.0)                  # raises queue.Empty
q.task_done();  q.join()            # wait for all work to finish

pq = PriorityQueue()                # heap-backed, thread-safe
pq.put((priority, seq, item))
```

`Queue` is a `Condition` + `deque` already written and tested. The sentinel-shutdown
idiom:

```python
for _ in workers: q.put(None)       # one poison pill per worker
# in the worker:  item = q.get();  if item is None: break
```

---

## ThreadPoolExecutor

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

with ThreadPoolExecutor(max_workers=4) as pool:
    futures = [pool.submit(work, x) for x in items]
    for f in as_completed(futures):
        result = f.result()         # re-raises the worker's exception here
```

The `with` block joins on exit. **Exceptions inside a worker are silent until you
call `.result()`** — a very common bug.

---

## Threads: lifecycle

```python
t = threading.Thread(target=fn, args=(...), daemon=True)
t.start(); t.join(timeout=5)
```

`daemon=True` means the process can exit without waiting. Convenient for background
loops, but the thread is killed abruptly — prefer an explicit `stop()` and `join()`
when state matters.

---

## The GIL — say this correctly

> "The GIL serialises bytecode execution, so it protects interpreter internals —
> but it does **not** make my multi-step business logic atomic. A read-then-write
> across two bytecodes can still interleave, so I still need a lock. It also means
> threads help with I/O-bound work, not CPU-bound; for CPU-bound I'd reach for
> `multiprocessing`."

`x += 1` is **not** atomic. `dict[k] = v` on its own is, but `if k not in d: d[k] = v`
is not.

---

## The two bugs interviewers look for

**TOCTOU — check and act in separate critical sections:**

```python
with lock:                  # BAD
    if seats_available(): pass
with lock:
    take_seat()
```
```python
with lock:                  # GOOD — one span
    if not seats_available(): raise SoldOut()
    take_seat()
```

**Lost wakeup — notifying before the waiter is waiting**, or using `if` instead of
`while`. Both are fixed by the predicate loop.

Deadlock: acquire multiple locks in a **consistent global order**, or use one lock.
For per-resource locking, say *"per-auction lock rather than one global lock, so
bids on different auctions don't serialise."*
