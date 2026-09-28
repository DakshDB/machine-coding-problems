"""Driver. The only place that reads input, prints output, and handles errors."""

import sys

from core.commands import CommandProcessor
from core.file_system import FileSystem
from models.errors import FileSystemError

EXIT_COMMAND = "exit"


def run(lines):
    processor = CommandProcessor(FileSystem())
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line == EXIT_COMMAND:
            break
        try:
            output = processor.execute(line)
        except FileSystemError as error:
            yield str(error)
        else:
            if output is not None:
                yield output


if __name__ == "__main__":
    for out in run(sys.stdin):
        print(out)
