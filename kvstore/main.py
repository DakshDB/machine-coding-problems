"""Driver. The only place that reads input, prints output, and handles exceptions."""

import sys

from core.commands import CommandProcessor
from core.store import KeyValueStore
from models.errors import DataTypeError, StoreError

EXIT_COMMAND = "exit"


def run(lines, store: KeyValueStore = None):
    """Execute command lines, yielding the line of output each one produces."""
    processor = CommandProcessor(store if store is not None else KeyValueStore())

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.lower() == EXIT_COMMAND:
            break

        try:
            output = processor.execute(line)
        except DataTypeError:
            yield "Data Type Error"
        except StoreError as error:
            yield str(error)
        else:
            if output is not None:
                yield output


def main() -> None:
    for output in run(sys.stdin):
        print(output)


if __name__ == "__main__":
    main()
