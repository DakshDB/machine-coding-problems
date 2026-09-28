from models.errors import InvalidOperation


class CommandProcessor:
    """Parses one line and returns its output. Never prints, never catches.

    New commands are a new entry in the registry, not another elif.
    """

    def __init__(self, file_system):
        self._fs = file_system
        self._handlers = {
            "mkdir": self._mkdir,
            "addFile": self._add_file,
            "ls": self._ls,
            "cat": self._cat,
            "rm": self._rm,
            "mv": self._mv,
            "find": self._find,
        }

    def execute(self, line):
        parts = line.split()
        if not parts:
            return None
        handler = self._handlers.get(parts[0])
        if handler is None:
            raise InvalidOperation(f"Unknown command: {parts[0]}")
        return handler(parts[1:])

    def _mkdir(self, args):
        self._fs.mkdir(self._arg(args, 1, "mkdir")[0])

    def _add_file(self, args):
        if not args:
            raise InvalidOperation("addFile expects a path and content")
        self._fs.add_file(args[0], " ".join(args[1:]))

    def _ls(self, args):
        return ",".join(self._fs.ls(self._arg(args, 1, "ls")[0]))

    def _cat(self, args):
        return self._fs.cat(self._arg(args, 1, "cat")[0])

    def _rm(self, args):
        self._fs.rm(self._arg(args, 1, "rm")[0])

    def _mv(self, args):
        source, destination = self._arg(args, 2, "mv")
        self._fs.mv(source, destination)

    def _find(self, args):
        return ",".join(self._fs.find(self._arg(args, 1, "find")[0]))

    @staticmethod
    def _arg(args, count, command):
        if len(args) != count:
            raise InvalidOperation(f"{command} expects {count} argument(s)")
        return args
