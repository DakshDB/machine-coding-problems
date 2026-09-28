# Bounded Concurrency: Pools, Queues, Backpressure

The family of problems where work arrives faster than you can do it. Job
schedulers, notification dispatchers, crawlers, download managers, connection
pools, order pipelines.

---

## The one idea: backpressure

**An unbounded queue is a memory leak with extra steps.** If producers are faster
than consumers and nothing pushes back, the queue grows until the process dies.

A bounded queue makes the producer *wait*, which propagates the slowdown back to
the source where it can be handled. Say this sentence in the room:

> "I'm bounding the queue so a fast producer blocks instead of exhausting memory —
> that's backpressure. If blocking isn't acceptable I'd drop, or reject with a
> 429, but silently unbounded is not an option."

The three policies when the queue is full — **block, drop, or reject** — are a real
design decision. Name which one you picked and why.

```python
q.put(item)                     # blocks — backpressure
q.put(item, timeout=1.0)        # blocks, then raises queue.Full — reject
q.put_nowait(item)              # raises immediately — drop or reject
```

---

## Worker pool — the canonical shape

```python
from queue import Queue, Empty
import threading

class WorkerPool:
    def __init__(self, n_workers=4, maxsize=100):
        self._q = Queue(maxsize=maxsize)          # bounded
        self._threads = [
            threading.Thread(target=self._run, daemon=True) for _ in range(n_workers)
        ]
        for t in self._threads:
            t.start()

    def submit(self, fn, *args):
        self._q.put((fn, args))                   # blocks when full

    def _run(self):
        while True:
            item = self._q.get()
            try:
                if item is None:                  # poison pill
                    return
                fn, args = item
                fn(*args)
            except Exception:
                pass                              # a bad task must not kill the worker
            finally:
                self._q.task_done()

    def shutdown(self, wait=True):
        if wait:
            self._q.join()                        # drain what's queued
        for _ in self._threads:
            self._q.put(None)                     # one pill per worker
        for t in self._threads:
            t.join()
```

Four things worth pointing at:

1. **`task_done()` in a `finally`.** Miss it and `q.join()` hangs forever.
2. **try/except around the task.** One exception otherwise kills a worker
   permanently, and your pool silently shrinks to zero.
3. **One poison pill per worker.** A single `None` only stops one thread.
4. **`q.join()` before the pills** if you want "finish what's queued"; skip it for
   "stop now".

---

## Shutdown: poison pill vs Event

| | Poison pill | `threading.Event` |
|---|---|---|
| Drains queued work | yes, naturally | no, needs care |
| Wakes a blocked `q.get()` | yes — the pill *is* an item | **no** — `get()` blocks forever |
| Good for | worker pools | loops that poll or `wait(timeout)` |

The trap: an `Event` alone does **not** wake a thread parked in `q.get()`. Either
use pills, or `q.get(timeout=0.5)` in a loop that re-checks the event.

```python
while not self._stop.is_set():
    try:
        item = self._q.get(timeout=0.5)
    except Empty:
        continue
```

---

## Semaphore — capping concurrency

`Semaphore(n)` is a counter, not a queue. Use it when the *work* is already
running on its own threads and you only want N in flight at once.

```python
sem = threading.Semaphore(3)
with sem:                        # at most 3 threads inside
    call_rate_limited_api()
```

`BoundedSemaphore(n)` additionally raises if you release more than you acquired —
which catches double-release bugs. Prefer it.

**Semaphore vs bounded Queue:** a semaphore limits *concurrency*; a bounded queue
limits *backlog*. Real systems usually want both — a queue in front, a pool
behind.

---

## Object pool (connections, DB handles)

```python
from contextlib import contextmanager
from queue import Queue

class ConnectionPool:
    def __init__(self, factory, size=5):
        self._pool = Queue(maxsize=size)
        for _ in range(size):
            self._pool.put(factory())

    @contextmanager
    def acquire(self, timeout=None):
        conn = self._pool.get(timeout=timeout)     # blocks until one is free
        try:
            yield conn
        finally:
            self._pool.put(conn)                   # ALWAYS returned, even on error
```

The `finally` is the whole pattern — a connection leaked on an exception path
shrinks the pool until it deadlocks. A `Queue` gives you the blocking acquire for
free; hand-rolling this with a list plus a `Condition` is a common interview ask.

---

## ThreadPoolExecutor

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

with ThreadPoolExecutor(max_workers=4) as pool:
    futures = {pool.submit(work, x): x for x in items}
    for f in as_completed(futures):
        try:
            result = f.result()          # re-raises the worker's exception HERE
        except Exception as e:
            log(futures[f], e)
```

Gotchas:
- **Exceptions are silent until `.result()`.** A `submit` you never await hides the
  error completely.
- Its internal queue is **unbounded** — `submit` never blocks. If you need
  backpressure, gate submissions with a semaphore or use your own bounded queue.
- The `with` block joins on exit; `shutdown(wait=False)` doesn't cancel running work.
- `pool.map` returns results **in input order** and re-raises on iteration;
  `as_completed` gives them as they finish.

---

## What they'll ask

| Question | Answer shape |
|---|---|
| Queue fills up? | block / drop / reject — I chose X because Y |
| A worker throws? | try/except inside the loop; the worker survives, the task is logged |
| A worker dies anyway? | supervisor re-spawns, or use an executor that does it |
| Clean shutdown? | drain with `join()`, then one poison pill per worker |
| Task must not be lost? | at-least-once: ack after success, re-queue on failure — implies idempotent tasks |
| Duplicate work? | at-most-once vs at-least-once; exactly-once needs dedup keys |
| Sizing the pool? | I/O-bound → many more than cores; CPU-bound → ~cores, and the GIL means `multiprocessing` |
| Retry? | bounded retries with backoff, then a dead-letter queue |

---

## Where it shows up

Notification dispatch · web crawler · job/task scheduler · order processing ·
log shipper · image thumbnailing · connection pooling · bulk import ·
rate-limited API client
