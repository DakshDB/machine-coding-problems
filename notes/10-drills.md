# Drills — Rebuilding Muscle Memory

Type these. Don't read them. No autocomplete, no AI.

---

## Drill 1 — Data structure reps (20 min, do it twice)

In a blank file, from memory, write one line for each:

```
1.  create an empty set
2.  add to a set, remove without raising if absent
3.  test membership in a set
4.  take an arbitrary element out of a set
5.  dict: get with a default
6.  dict: iterate key AND value
7.  dict: get-or-create a list and append to it (two different ways)
8.  defaultdict of sets; add to a missing key
9.  invert a dict with a comprehension
10. sort a list of objects by two fields, one descending
11. count items matching a condition without building a list
12. find the first item matching a condition, or None
13. deque: add and remove from both ends
14. heapq: push a (priority, item) and pop the smallest
15. Counter: three most common
16. flatten a list of lists in one comprehension
17. dataclass with a list field that defaults to empty
18. frozen dataclass usable as a dict key
```

Check against `01-data-structures.md`. Anything you missed, write **five times**.

---

## Drill 2 — The 10-minute skeleton (do until it's automatic)

Set a timer for 10 minutes. From scratch, no reference:

```
models/enums.py       2 enums
models/entities.py    2 entity classes, one a dataclass
models/exceptions.py  base + 3 children
core/service.py       __init__ with 2 dicts (one a defaultdict index),
                      4 method signatures with type hints and complexity comments
main.py               the 8-item edge-case comment block
```

No implementation. Just the skeleton. **Target: under 10 minutes, every time.**
This is the single highest-leverage drill — it buys you 10 extra minutes of
thinking time on Monday.

---

## Drill 3 — Pattern reps (15 min)

From memory, write:

1. A registry factory: enum → class, with an unknown-type error.
2. A base class with a `TRANSITIONS` table and a subclass overriding one row.
3. An ABC strategy with two implementations, injected into a service constructor
   with a default.

Check against `07-design-patterns.md`.

---

## Drill 4 — Narration (do once, it's uncomfortable and worth it)

Record yourself (phone voice memo) solving any small problem for 15 minutes.
Play it back and count:

- Silences longer than 30 seconds → how many?
- Times you explained a **decision** vs narrated syntax?
- Did you state a single complexity?

Most people are shocked at how much they go quiet. One recording fixes it.

---

## Drill 5 — Attack practice (15 min)

Take your **Task Tracker** code. Without looking at my reviews, write down 10 ways
to break it. Then run them.

Then do the same for **Parking Lot**. Compare against my findings. The gap between
your list and mine is exactly what to watch for on Monday.

---

## Drill 6 — Complexity out loud (10 min)

For each method in your parking lot, say aloud, in one sentence:

- what it's O(), in terms of *named* variables
- what it does **not** depend on
- the space you traded for it

If you can't do it fluently for code you wrote yourself, you won't manage it for
code you wrote 40 minutes ago under pressure.

---

## Weekend schedule

**Saturday evening**
- Drill 1 (20 min) → Drill 2 ×3 (30 min) → read `09-your-gaps.md` (15 min)

**Sunday morning**
- Drill 3 (15 min) → **Splitwise, 60 min timed** → 20 min self-attack

**Sunday afternoon**
- Drill 5 (15 min) → **Movie seat booking or LRU cache, 45 min, recorded**
- Drill 4 while doing it

**Sunday evening**
- Drill 6 (10 min) → re-read `08-playbook.md` → sketch Tier-3 problems on paper
- **Write no new code after 9pm**

**Monday morning**
- `09-your-gaps.md` pre-flight checklist only. Set up an empty skeleton folder.
- Rest. No new material.
