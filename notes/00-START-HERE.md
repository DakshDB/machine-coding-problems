# Machine Coding Prep — Reading Guide

Built from your two practice sessions (Task Tracker, Parking Lot). Every gotcha in
here is one you actually hit, or one that sits next to something you hit.

## Read in this order

| # | File | Why it's here | Time |
|---|------|---------------|------|
| 09 | `09-your-gaps.md` | **Start here.** Your real mistakes, ranked by how often you repeat them | 15 min |
| 01 | `01-data-structures.md` | You forgot `set` existed and got bitten by `list.remove()` returning `None` | 45 min |
| 02 | `02-idioms-and-syntax.md` | `.items()`, `.get()`, comprehensions, `is None`, truthiness | 30 min |
| 03 | `03-oop.md` | `@classmethod` misuse, class vs instance attrs, ABC without teeth, dunders | 45 min |
| 04 | `04-exceptions.md` | `from shutil import Error` three times; no hierarchy twice | 20 min |
| 06 | `06-complexity.md` | You've never said a complexity out loud. It's a graded metric | 30 min |
| 07 | `07-design-patterns.md` | You skipped Strategy when told to use it | 45 min |
| 05 | `05-stdlib.md` | datetime, enum, uuid, collections, typing | 30 min |
| 08 | `08-playbook.md` | The 60-minute ritual and the talk track | 20 min |
| 10 | `10-drills.md` | Typing exercises to rebuild muscle memory | do these |
| 11 | `11-resources.md` | External links if you want to go deeper | reference |

## If you only have 3 hours

1. `09-your-gaps.md` — all of it (15 min)
2. `01-data-structures.md` — the "Gotchas" section, then the tables (30 min)
3. `06-complexity.md` — memorise the one table (20 min)
4. `07-design-patterns.md` — Strategy, Factory, State only (30 min)
5. `10-drills.md` — Drill 1 and Drill 2, hands on keyboard (60 min)
6. `08-playbook.md` — read twice (20 min)

## If you have 30 minutes before walking in

Read `09-your-gaps.md`, then the "Pre-flight checklist" at the bottom of it.
Nothing else. Don't cram new material on interview day.

## How to use these

Do **not** read passively. For every code block longer than three lines, type it
into a REPL and change one thing to see it break. You are rebuilding motor memory,
not acquiring information — you already know most of this, it just isn't in your
fingers right now.
