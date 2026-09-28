# Python Data Structures — Working Reference

Everything you need for a machine coding round. Type the snippets; don't just read.

---

## Choosing the right one — decision table

| I need to... | Use | Why |
|---|---|---|
| Look up by id | `dict` | O(1) |
| Check "have I seen this?" | `set` | O(1) `in` |
| Hold a pool of available things and take one | `set` | O(1) `.pop()` |
| Keep insertion order and index into it | `list` | O(1) index |
| Add/remove at **both** ends | `collections.deque` | O(1) both ends |
| Always get the smallest/largest | `heapq` | O(log n) push/pop |
| Count occurrences | `collections.Counter` | built-in |
| Auto-create the value on first access | `collections.defaultdict` | no key checks |
| Group items by a key | `defaultdict(list)` or `defaultdict(set)` | the standard index |
| Fixed record, no behaviour | `dataclass` or `NamedTuple` | free `__init__`/`__repr__` |
| Order matters AND uniqueness matters | `dict.fromkeys()` | dicts keep insertion order |

**The rule that would have saved you 60x:** if you're looping to *find* something,
you wanted a dict or a set.

---

## THE GOTCHAS (read these twice)

### 1. Mutating methods return None

```python
x = [3, 1, 2]
y = x.sort()        # y is None!  x is now [1,2,3]
y = sorted(x)       # y is [1,2,3], x unchanged   <- what you usually want

s = {1, 2}
z = s.add(3)        # z is None

lst = [1, 2, 3]
lst = lst.remove(2) # BUG: lst is now None
lst.remove(2)       # correct
```

Same for `.append()`, `.extend()`, `.insert()`, `.update()`, `.reverse()`,
`.clear()`, `.discard()`.

**Rule: if it changes the object, it returns `None`. Never assign it.**

### 2. Mutable default arguments

```python
def bad(item, into=[]):     # the SAME list on every call, forever
    into.append(item)
    return into

bad(1)   # [1]
bad(2)   # [1, 2]   <- surprise

def good(item, into=None):
    if into is None:
        into = []
    into.append(item)
    return into
```

### 3. Copying is shallow by default

```python
a = [[1, 2], [3, 4]]
b = a[:]              # or list(a), or a.copy()
b[0].append(99)       # a is ALSO changed - inner lists are shared

import copy
c = copy.deepcopy(a)  # fully independent
```

Same trap with dicts: `{**base, 'k': v}` copies the outer dict but shares the
inner values. That's why `{**Task.TRANSITIONS, OPEN: {...}}` is safe (you replace
the whole set) but `Task.TRANSITIONS[OPEN].add(x)` is not (mutates the shared set).

### 4. Iterating while mutating

```python
for t in tasks:
    if done(t):
        tasks.remove(t)     # skips elements, silently wrong

tasks = [t for t in tasks if not done(t)]     # correct
for t in list(tasks):       # or iterate over a copy
    ...
```

Proof it really is silent — removing evens from `[1, 2, 4, 5]`:

```
visited: [1, 2, 5]   <- 4 was never examined
result : [1, 4, 5]   <- 4 survived; the correct answer is [1, 5]
```

No error, no warning. The index advances while the list shrinks under it.

### 5. `set.pop()` is arbitrary, `list.pop()` is the last element

```python
{1,2,3}.pop()       # some element, unspecified which
[1,2,3].pop()       # 3, always
[1,2,3].pop(0)      # 1, but O(n) - use deque.popleft() instead
```

If you need determinism (reproducible tests, "nearest spot"), a set is the wrong
choice — use a heap or a deque and say so out loud.

---

## dict

```python
d = {}
d = dict(a=1, b=2)
d = {k: v for k, v in pairs}                 # comprehension

d['k'] = v                 # set (creates or overwrites)
d['k']                     # KeyError if missing
d.get('k')                 # None if missing
d.get('k', 0)              # default if missing        <- you forgot this one
d.setdefault('k', []).append(x)              # get-or-create in one call

'k' in d                   # O(1) membership - never use `k in d.keys()`
del d['k']                 # KeyError if missing
d.pop('k', None)           # remove and return, safe
d.update(other)            # merge in place
merged = {**a, **b}        # new dict, b wins on conflicts
merged = a | b             # same thing, Python 3.9+

len(d)
d.clear()
```

### Iteration — the one you keep forgetting

```python
for key in d:                   # keys (default!)
for key in d.keys():            # same, explicit
for value in d.values():
for key, value in d.items():    # <- THIS is the one you forget
```

```python
# sorting a dict by value
top = sorted(d.items(), key=lambda kv: kv[1], reverse=True)
# inverting
inv = {v: k for k, v in d.items()}
# filtering
open_only = {k: v for k, v in d.items() if v.status == OPEN}
```

Dicts preserve insertion order (guaranteed since 3.7).

### defaultdict — the index workhorse

```python
from collections import defaultdict

by_user = defaultdict(list)          # missing key -> new list
by_user['u1'].append(task_id)        # no "if key not in" needed

free = defaultdict(set)              # missing key -> new set
free[size].add(spot)

counts = defaultdict(int)            # missing key -> 0
counts[word] += 1
```

Two traps:
- `defaultdict()` with **no** factory behaves like a plain dict. You wrote this.
- **Reading** a missing key *creates* it. Use `d.get(k, set())` when you only read.

---

## set

The one you forgot exists. Reach for it constantly.

```python
s = set()                 # NOT {} - that's an empty dict
s = {1, 2, 3}
s = set(some_list)        # dedupe

s.add(x)                  # O(1)
s.discard(x)              # O(1), no error if absent    <- prefer this
s.remove(x)               # O(1), KeyError if absent
s.pop()                   # remove and return an arbitrary element
x in s                    # O(1)   <- the whole point
len(s)

a | b     a.union(b)
a & b     a.intersection(b)
a - b     a.difference(b)
a ^ b     a.symmetric_difference(b)
a <= b    a.issubset(b)
```

**Where sets win in LLD problems:**

```python
free_spots[size].pop()                  # take any available resource, O(1)
if plate in self.parked_plates:         # duplicate detection, O(1)
allowed = TRANSITIONS[current]          # state machine legality
if new_status not in allowed: raise
```

`frozenset` is the immutable version — hashable, so it can be a dict key.

---

## list

```python
lst.append(x)          # O(1)
lst.pop()              # O(1) from the end
lst.pop(0)             # O(n)  <- use deque instead
lst.insert(0, x)       # O(n)
x in lst               # O(n)  <- the trap; use a set
lst.remove(x)          # O(n), removes FIRST match, ValueError if absent
lst.index(x)           # O(n), ValueError if absent
lst.sort(key=..., reverse=True)   # in place, returns None
sorted(lst, key=...)              # new list

lst[::-1]     # reversed copy
lst[a:b]      # slice, O(b-a)
```

Comprehensions:

```python
[x*2 for x in xs]
[x for x in xs if cond(x)]
[f(x) if cond(x) else g(x) for x in xs]
[y for x in xss for y in x]                 # flatten (read left to right)
{x.id: x for x in xs}                       # dict comprehension
{x.size for x in xs}                        # set comprehension
(x*2 for x in xs)                           # generator - lazy, no list built
```

---

## deque

```python
from collections import deque
q = deque()
q.append(x)        q.pop()          # right, O(1)
q.appendleft(x)    q.popleft()      # left,  O(1)
q = deque(maxlen=5)                 # ring buffer, drops from the far end
```

Use for: queues, BFS, sliding windows, LRU ordering, "oldest first" pools.

---

## heapq — a min-heap on a plain list

```python
import heapq
h = []
heapq.heappush(h, (priority, item))   # O(log n)
heapq.heappop(h)                      # smallest, O(log n)
h[0]                                  # peek, O(1)
heapq.heapify(lst)                    # O(n), in place
heapq.nsmallest(3, iterable, key=...)
```

Min-heap only. For a max-heap, push `-priority`. Tuples compare left to right, so
`(priority, tiebreaker, item)` works — but make sure `item` is comparable or the
tiebreaker is unique, or you get a `TypeError` on ties.

**LLD uses:** nearest parking spot to the entrance, next elevator stop, priority
queues, rate limiter expiry, "top N" leaderboards.

---

## Counter

```python
from collections import Counter
c = Counter(words)
c.most_common(3)        # [(word, count), ...]
c['missing']            # 0, no KeyError
c.update(more)
```

---

## tuple / NamedTuple / dataclass

```python
from typing import NamedTuple
from dataclasses import dataclass, field

class Point(NamedTuple):        # immutable, hashable, comparable
    x: int
    y: int

@dataclass
class User:                     # mutable, free __init__/__repr__/__eq__
    id: str
    name: str
    tags: list = field(default_factory=list)   # NOT tags: list = []

@dataclass(frozen=True)         # immutable AND hashable -> usable as dict key
class SpotId:
    floor: int
    number: int
```

`field(default_factory=list)` is the dataclass form of the mutable-default fix.

---

## Common index patterns you will need on Monday

```python
# 1. group by  (get_tasks_by_user, spots_by_floor)
by_user = defaultdict(set)
by_user[user_id].add(task_id)

# 2. available pool  (free parking spots)
free = defaultdict(set)
free[size].add(spot)
spot = free[size].pop() if free[size] else None

# 3. uniqueness guard  (duplicate licence plate)
if plate in self.active_plates: raise AlreadyParkedError(...)
self.active_plates.add(plate)

# 4. two-way index  (who owes whom)
balances = defaultdict(lambda: defaultdict(int))
balances[a][b] += amount
balances[b][a] -= amount

# 5. bounded history
recent = deque(maxlen=100)
```

Every one of these is 2-3 lines and turns an O(n) scan into O(1).
