# Heaps, Priority Queues and Ordering

The gap the Leaderboard problem exposed. Heaps show up whenever the question is
**"which one is next / smallest / largest"** and you don't want to sort every time.

---

## heapq basics — a min-heap on a plain list

```python
import heapq

h = []
heapq.heappush(h, 5)          # O(log n)
heapq.heappush(h, 1)
smallest = heapq.heappop(h)   # O(log n) -> 1
peek     = h[0]               # O(1), does NOT remove
heapq.heapify(lst)            # O(n), in place — cheaper than n pushes
heapq.heappushpop(h, x)       # push then pop, one operation
heapq.heapreplace(h, x)       # pop then push
len(h)
```

**It is a min-heap only.** For a max-heap, negate:

```python
heapq.heappush(h, -score)
top = -heapq.heappop(h)
```

`h` is an ordinary list. `h[0]` is the smallest, but **the rest is not sorted** —
don't iterate it expecting order.

---

## Tuples: priority plus payload

```python
heapq.heappush(h, (priority, item))
priority, item = heapq.heappop(h)
```

Tuples compare left to right, so ties fall through to the second element. **If the
payload isn't comparable, that raises `TypeError`.** Always add a unique
tiebreaker:

```python
from itertools import count
counter = count()
heapq.heappush(h, (priority, next(counter), some_object))   # counter breaks ties
```

That also makes ordering **stable** — equal priorities come out in insertion order,
which is usually what you want.

---

## The pattern that makes heaps usable: lazy deletion

Heaps have **no decrease-key and no remove-arbitrary-element**. This is the thing
that trips people up on leaderboards and schedulers.

You cannot update an entry in place. Instead: **push the new value and ignore
stale ones when they surface.**

```python
class Leaderboard:
    def __init__(self):
        self._scores = {}                   # player -> current score (truth)
        self._heap = []                     # (-score, player) — may hold stale entries

    def add_score(self, player, points):
        self._scores[player] = self._scores.get(player, 0) + points
        heapq.heappush(self._heap, (-self._scores[player], player))   # O(log n)

    def top(self):
        while self._heap:
            neg, player = self._heap[0]
            if -neg == self._scores.get(player):      # still current?
                return player, -neg
            heapq.heappop(self._heap)                 # stale, discard
        return None
```

**The dict is the source of truth; the heap is a hint.** A heap entry is valid only
if it matches the dict. This is the single most reusable heap idiom — it appears in
Dijkstra, schedulers, leaderboards, and expiry queues.

Cost: the heap can grow to O(total updates) rather than O(players). If that matters,
compact it when stale entries exceed half the heap.

---

## Leaderboard: pick the structure from the operations

There is no single right answer — say this out loud and let them pick.

| Operations asked for | Best structure |
|---|---|
| `top_k` called rarely, k small | `dict` + `heapq.nlargest(k, d.items(), key=...)` — O(n log k) |
| `top_k` called constantly | maintain a heap with lazy deletion, or a sorted structure |
| `rank(player)` — "what position am I?" | needs **order statistics**: sorted list + `bisect`, or a Fenwick/BIT |
| Scores change constantly | dict + lazy-deletion heap |
| Fixed small k (top 10 of a stream) | **bounded min-heap of size k** — see below |

**Top-K of a stream in O(n log k) time and O(k) space** — the classic:

```python
def top_k(stream, k):
    h = []
    for x in stream:
        if len(h) < k:
            heapq.heappush(h, x)
        elif x > h[0]:              # h[0] is the smallest of the current best k
            heapq.heapreplace(h, x)
    return sorted(h, reverse=True)
```

Counter-intuitive but important: **to keep the largest k, you use a MIN-heap**, so
the weakest survivor is always at `h[0]` and cheap to evict.

`heapq.nlargest(k, iterable, key=...)` and `nsmallest` do this for you. Use them
unless asked to implement it.

---

## `rank()` is the hard one — know why

A heap cannot answer "what rank is player X". Neither can a dict. Options:

- **`sorted()` on demand** — O(n log n) per call. Fine if `rank` is rare. Say so.
- **Sorted list + `bisect`** — O(log n) lookup, but O(n) insert. Good for read-heavy.
- **Fenwick tree / BIT over score buckets** — O(log n) both. Mention it; only build
  it if they push.

Saying *"rank needs order statistics, which a heap can't give me — here's the
trade-off"* scores better than silently writing an O(n log n) sort.

---

## bisect — a sorted list with O(log n) search

```python
import bisect
i = bisect.bisect_left(sorted_lst, x)    # leftmost position where x fits
bisect.insort(sorted_lst, x)             # insert keeping order — O(n) due to the shift
```

Search is O(log n); insertion is O(n) because the list shifts. Good when reads
dominate writes. `bisect` also does "find the first element ≥ x", which is how you
answer range and window queries.

---

## When NOT to reach for a heap

- You need the **whole thing sorted** → just `sorted()`.
- You need **arbitrary removal** → dict + lazy deletion, or a different structure.
- You need **k = 1 and updates are rare** → `max()` is O(n) and simpler.
- You need **both ends** → two heaps, or a `SortedList` (not stdlib).

---

## Complexity to quote

| Operation | Cost |
|---|---|
| `heappush` / `heappop` | O(log n) |
| `h[0]` peek | O(1) |
| `heapify(list)` | **O(n)**, not O(n log n) |
| `nlargest(k, n items)` | O(n log k) |
| building by n pushes | O(n log n) — prefer `heapify` |
| space | O(n), plus stale entries under lazy deletion |
