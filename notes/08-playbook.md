# The 60-Minute Playbook

---

## Clock

| Minutes | What | Notes |
|---|---|---|
| **0–5** | Clarify. State 3 assumptions. Ask 1–2 scoping questions | out loud, before typing |
| **5–10** | Enums, entities, exception hierarchy | muscle memory, go fast |
| **10–20** | Method signatures + **edge-case comment block** | say complexity as you type each signature |
| **20–45** | Implement | narrate decisions, not syntax |
| **45–55** | **Run your edge-case list.** Fix what breaks | the part you skip — don't |
| **55–60** | State what you'd add next, and known limitations | converts gaps into judgement |

If you're behind at minute 45, **stop implementing and start testing anyway**.
Working code with 4 of 6 features beats 6 broken ones.

---

## Opening script (memorise the shape)

> "Let me restate: [one sentence]. I'll assume [A], [B], [C] — tell me if any of
> those are wrong. One question: [scoping question]. I'll start with the entities
> and enums, then the service layer, then edge cases. Everything in memory,
> single-threaded, and I'll flag where concurrency would matter."

Good scoping questions:
- "Should I handle persistence, or is in-memory fine?" (always in-memory)
- "Do you want a CLI, or is a `main` that exercises the API enough?"
- "Is X in scope, or should I leave a hook for it?"

Then **stop asking and start building.** Two questions maximum.

---

## File skeleton — same every time

```
models/
    enums.py          # NOT enum.py
    entities.py       # dataclasses / simple classes
    exceptions.py     # 5 lines, write first
strategy/ (or core/)
    pricing.py        # the pluggable policy, if there is one
core/
    service.py        # orchestration, guards, indexes
main.py               # demo + edge cases; ONLY file with print()
```

Say it as you create it: *"I'm separating models, strategy and service so the core
has no I/O and stays testable."*

---

## The edge-case block — write this BEFORE the logic

At the top of `main.py`, at minute 10:

```python
# EDGE CASES TO VERIFY
# 1. resource full
# 2. duplicate entry (same id/plate twice)
# 3. unknown id
# 4. double release / double exit
# 5. operation on an unassigned/unowned entity
# 6. zero / negative / boundary duration
# 7. limit boundary: n-1, n, n+1
# 8. state restored correctly after a full create->release cycle
```

Those eight generalise to almost every LLD problem. At minute 45 you turn each
into a call. **This single habit is the biggest score you're leaving on the table.**

---

## What to say while typing

Narrate **decisions**, not syntax. Nobody wants "now I'm writing a for loop."

| Moment | Say |
|---|---|
| Choosing a structure | "Set, because I need O(1) membership and I never need order." |
| Adding an index | "This is O(T) extra space to make lookup O(1) instead of O(N)." |
| Writing a signature | "This will be O(S×F) — configuration constants, not data size." |
| Adding a guard | "Two paths reach this state change, so the check goes in one helper." |
| Using a dict over if/elif | "Registry, so adding a type is a data change and unknowns fail loudly." |
| Injecting a policy | "The spec says pricing changes, so the core takes the interface." |
| Cutting scope | "Not building a user registry — I'd add it, out of scope for these ops." |
| Hitting a bug | "Let me trace this — I expect X here, printing to confirm." |

**Debugging out loud is a positive signal, not a negative one.** State your
hypothesis before you print. "The count is wrong, so either the increment or the
decrement is off — checking the release path first."

---

## Silence rules

- Never go quiet for more than ~30 seconds.
- If you need to think: *"Give me twenty seconds to think about the data model."*
  That's fine. Silent staring isn't.
- If stuck: say what you're stuck on. They'll often unblock you, and asking well
  is graded better than flailing.

---

## Closing script (minute 55)

> "Working: [list]. Verified edge cases: [list]. Complexities: [one line each].
> Known gaps I'd fix next: [2–3 items]. If this went multi-threaded, the race is
> at [exact place], and I'd fix it with [approach]."

Naming your own gaps first is the strongest close available. It's the difference
between "missed it" and "prioritised it."

---

## Scoring your own practice runs

| | Very good | Good | Weak |
|---|---|---|---|
| Runs | first try | after 1 fix | crashes on demo |
| Edge cases | 8 handled + tested | 4–5 handled | happy path only |
| Complexity | stated proactively | answered when asked | vague |
| Patterns | 2 used, justified | 1 used | if/elif everywhere |
| Communication | continuous | prompted | silent |
| Structure | clean modules, pure core | some mixing | one file |

Aim for the left column in 3 of 6 categories, and no "weak" anywhere.

---

## Ten minutes before the round

1. New folder, `models/ core/ main.py` skeleton ready.
2. Editor font size up. Close Slack, email, everything.
3. Water. Paper and pen next to you for the entity sketch.
4. Read `09-your-gaps.md` pre-flight checklist. Nothing else.
5. Remind yourself: **working and explained beats clever and silent.**
