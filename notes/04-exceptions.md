# Exceptions

The five lines you should write at the start of every machine coding round.

---

## The hierarchy (write this first, every time)

```python
class ParkingError(Exception):
    """base for everything this system raises"""

class LotFullError(ParkingError): pass
class TicketNotFoundError(ParkingError): pass
class DuplicateVehicleError(ParkingError): pass
class InvalidDurationError(ParkingError): pass
```

Why it earns marks:

```python
try:
    lot.park_vehicle(v)
except LotFullError:
    redirect_to_overflow()          # specific recovery
except ParkingError as e:
    log(e)                          # catch-all for MY errors only
```

With `raise Exception("Lot Full")` the caller has to match strings, and a genuine
`TypeError` in your own code gets swallowed by the same `except Exception`.

**You did this correctly in the Task Tracker and then didn't carry it to the
Parking Lot.** Make it the first file you create.

---

## Raising

```python
raise LotFullError(f"no {size.value} spot free on any floor")
raise LotFullError() from None      # suppress the chained cause
raise LotFullError() from original  # explicitly chain a cause
```

`from None` is the polish move when translating a low-level error:

```python
try:
    cls = REGISTRY[task_type]
except KeyError:
    raise UnknownTaskTypeError(f"unsupported: {task_type!r}") from None
```

Without `from None` the caller sees "During handling of the above exception,
another exception occurred" plus a `KeyError` traceback — noise.

---

## try / except / else / finally

```python
try:
    spot = self._allocate(v)
except LotFullError:
    ...                      # ran only on that error
except (A, B) as e:
    ...                      # multiple types
else:
    ...                      # ran only if NO exception - keeps the try block small
finally:
    ...                      # always runs, even on return/raise - cleanup
```

`else` is underused and reads well: put only the risky call in `try`, the
follow-up work in `else`.

---

## Guard clauses beat nesting

```python
# nested
def unpark(self, ticket_id):
    ticket = self.tickets.get(ticket_id)
    if ticket:
        if ticket.spot:
            ...

# flat - preferred
def unpark(self, ticket_id):
    ticket = self.tickets.get(ticket_id)
    if ticket is None:
        raise TicketNotFoundError(ticket_id)
    if ticket.spot is None:
        raise InvalidTicketError(ticket_id)
    ...
```

Validate and bail at the top; the happy path stays at one indent level.

---

## Error messages that help

```python
raise CapacityExceededError(
    f"{user_id} already has {n} tasks in progress, limit is {MAX}")
```

Include: **who**, **what they tried**, **why it failed**, **what's allowed**. A
good message is worth a comment.

---

## Built-ins and when to reuse them

| Exception | Use for |
|---|---|
| `ValueError` | right type, wrong value (negative duration) |
| `TypeError` | wrong type entirely |
| `KeyError` / `IndexError` | missing key/index — usually translate these |
| `NotImplementedError` | abstract method placeholder |

Reusing `ValueError` for input validation is fine and idiomatic. Reserve your
custom hierarchy for **domain rules** — "lot full" is a business fact, not a
Python type error.

---

## Anti-patterns

```python
except:                # bare - catches KeyboardInterrupt and SystemExit too
except Exception:      # too broad unless you re-raise or log
    pass               # silent swallow - the worst thing in this file

raise Exception("...")           # unclassifiable by the caller
from shutil import Error         # this is an OSError. Not your domain error.
```

---

## assert is not error handling

```python
assert x > 0, "must be positive"      # stripped entirely under python -O
```

Fine for internal invariants and quick test scripts. **Never** for validating
input or enforcing business rules.
