# Complexity — And How to Say It Out Loud

"Explaining time and space complexities" is an explicit grading metric and you
have never once articulated one. Fix that here.

---

## The table to memorise

| Operation | list | deque | set | dict |
|---|---|---|---|---|
| index `x[i]` | **O(1)** | O(n) | — | — |
| `x in c` | **O(n)** | O(n) | **O(1)** | **O(1)** (key) |
| append / add | O(1)* | O(1) | O(1) | O(1) |
| appendleft | O(n) | **O(1)** | — | — |
| pop() end | O(1) | O(1) | O(1) arbitrary | — |
| pop(0) / popleft | **O(n)** | **O(1)** | — | — |
| insert(i, x) | O(n) | O(n) | — | — |
| remove / discard by value | **O(n)** | O(n) | **O(1)** | **O(1)** |
| len | O(1) | O(1) | O(1) | O(1) |
| iterate | O(n) | O(n) | O(n) | O(n) |
| sort | O(n log n) | — | — | — |
| min / max | O(n) | O(n) | O(n) | O(n) |
| copy | O(n) | O(n) | O(n) | O(n) |

\* amortised — occasional resize is O(n)

**heapq:** push O(log n), pop O(log n), peek `h[0]` O(1), `heapify` O(n).

**Sets:** union O(len(a)+len(b)), intersection O(min(len(a),len(b))).

**Strings are immutable** — `s += x` in a loop is O(n²). Build a list and
`"".join(parts)`.

Dict/set are **average** case; worst case is O(n) under adversarial hash
collisions. Say "amortised O(1)" and you sound precise.

---

## The two lines you must be able to say

> "`park_vehicle` is O(S × F) where S is the number of spot sizes and F is floors
> — both configuration constants, so it's effectively O(1). It does not depend on
> how many spots or vehicles exist."

> "I'm spending O(1) extra space per assignment on the index to buy an O(k)
> lookup instead of O(N), where k is that user's task count."

Notice the shape: **name the variable, say what it depends on, say what it does
NOT depend on, and state the trade.**

---

## The mistake you made twice

You had an O(1) counter check wrapping an O(n) scan:

```python
if self.free_count(floor, size) > 0:            # O(1)
    for spot in self.all_spots[floor][size]:    # O(n)  <- this dominates
        if not spot.is_occupied:
            return spot
```

**The complexity of a block is its slowest part.** A fast guard in front of a slow
loop is still slow. When you state a complexity, find the innermost loop and start
there, then work outwards.

Measured: 3.7µs at 100 cars → 221µs at 20,000. That's the 60x you didn't predict.

---

## Space complexity — don't forget to mention it

For every index you add, say what it costs:

- `dict[user_id, set[task_id]]` → **O(T)** total, where T is tasks (each id
  appears once). Not O(U × T).
- `dict[size, set[spot]]` → **O(S)** total, S = number of spots.
- Storing *references* to existing objects is cheap — you're not copying them.

> "The index is O(T) additional space — one entry per task — in exchange for
> turning an O(N) scan into an O(1) lookup."

---

## Amortised vs worst case

`list.append` is O(1) *amortised*: most appends are constant, but when capacity
runs out the list reallocates and copies (O(n)). Averaged over many appends it's
O(1). Same idea for dict/set growth.

Use the word — it signals you know the difference between typical and worst case.

---

## Common patterns and their cost

| Pattern | Complexity |
|---|---|
| Single loop over n | O(n) |
| Nested loop over n | O(n²) |
| Loop with a set lookup inside | O(n) — the lookup is free |
| Loop with a **list** `in` inside | O(n²) — the classic hidden trap |
| Binary search / heap op | O(log n) |
| Sorting then scanning | O(n log n) |
| Building a dict index, then n lookups | O(n) build + O(n) lookups = O(n) |

**The single most common interview improvement:** replace a `list` membership
test with a `set` and go from O(n²) to O(n).

---

## Talking about it during the round

Say the complexity **as you write the signature**, not at the end:

> "`get_tasks_by_user` — I want this O(1) in the number of total tasks, so I'll
> keep a `user_id → set of task ids` index and pay for it on every assignment."

Then when they ask at the end, you're repeating yourself, not deriving it under
pressure.

If you knowingly ship something slow, **say so before they find it**:

> "This is O(n) right now. I'd replace the list with a heap keyed on distance if
> we cared about nearest-spot allocation — flagging it, moving on for time."

That converts a finding *against* you into evidence you were in control.
