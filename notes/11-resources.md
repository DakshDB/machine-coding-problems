# External Resources

Verified live September 2026. Ranked — don't try to read them all before Monday.

---

## Python reference (use as lookup, not reading)

| Resource | Use it for |
|---|---|
| [Time complexity of built-in types](https://docs.python.org/3/library/time-complexity.html) | **The** authoritative complexity table. Official docs |
| [Python Wiki: TimeComplexity](https://wiki.python.org/moin/TimeComplexity) | Same data, more detail on edge cases |
| [collections docs](https://docs.python.org/3/library/collections.html) | defaultdict, deque, Counter, OrderedDict |
| [dataclasses docs](https://docs.python.org/3/library/dataclasses.html) | `field(default_factory=...)`, frozen, order |
| [enum docs](https://docs.python.org/3/library/enum.html) | auto(), IntEnum, functional API |
| [abc docs](https://docs.python.org/3/library/abc.html) | ABC, abstractmethod |
| [heapq docs](https://docs.python.org/3/library/heapq.html) | priority queues |
| [datetime docs](https://docs.python.org/3/library/datetime.html) | timedelta arithmetic |
| [Python Morsels: Big O](https://www.pythonmorsels.com/time-complexities/) | Friendlier complexity walkthrough |
| [GeeksforGeeks complexity cheat sheet](https://www.geeksforgeeks.org/python/complexity-cheat-sheet-for-python-operations/) | Quick single-page table |

---

## Design patterns

| Resource | Use it for |
|---|---|
| [Refactoring.Guru — Design Patterns in Python](https://refactoring.guru/design-patterns/python) | **Best single resource.** Diagrams + Python code |
| [Strategy in Python](https://refactoring.guru/design-patterns/strategy/python/example) | The one you skipped — read this first |
| [Factory Method in Python](https://refactoring.guru/design-patterns/factory-method/python/example) | Registry/factory variants |
| [Factory comparison](https://refactoring.guru/design-patterns/factory-comparison) | Clears up factory vs abstract factory vs strategy |
| [Pattern catalog](https://refactoring.guru/design-patterns/catalog) | Skim to recognise names |

**Read only:** Strategy, Factory Method, State, Observer, Decorator, Builder.
Skip the rest until after Monday.

---

## LLD / machine coding specific

| Resource | Use it for |
|---|---|
| [workat.tech — Machine Coding](https://workat.tech/machine-coding/) | Round format, expectations, practice problems. Closest to your format |
| [AlgoMaster — Learn LLD from Zero](https://blog.algomaster.io/p/how-to-learn-low-level-design-from-zero) | Roadmap and problem ordering |
| [GitHub: sbvkrishna/low-level-design](https://github.com/sbvkrishna/low-level-design) | Worked solutions in several languages. **Compare after you solve, never before** |
| [InterviewBit LLD questions](https://www.interviewbit.com/low-level-design-interview-questions/) | Oral follow-up questions (SOLID, UML, patterns) |
| [Low Level Design Mastery — top 20 questions](https://www.lowleveldesignmastery.com/blog/low-level-design-interview-questions/) | Problem list to pick practice from |

---

## Honest advice on using these

You have about two days. **Reading solutions is not practice** — the round tests
whether you can produce structure under time pressure, and that only comes from
typing.

Budget roughly:
- **20%** reading (these notes + Refactoring.Guru on Strategy)
- **80%** timed problems and the drills in `10-drills.md`

If you're choosing between reading one more pattern and doing one more timed
problem, **do the problem.**

---

## After Monday

Worth a proper read when you're not under time pressure:

- *Head First Design Patterns* — the standard, genuinely well written
- *Clean Code* (Martin) — chapters 2, 3, 6, 10 only
- *Refactoring* (Fowler) — the catalogue of code smells is the useful half
- Grokking the Low Level Design Interview (educative) — if you want structured drills
