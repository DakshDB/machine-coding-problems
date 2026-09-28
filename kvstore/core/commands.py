from core.store import KeyValueStore
from models.errors import InvalidCommandError


class CommandProcessor:
    """Turns one command line into a store call plus an optional line of output.

    It never prints and never swallows exceptions - the driver does both.
    New commands are added by putting a handler in the registry, not by
    extending an if/elif chain.
    """

    def __init__(self, store: KeyValueStore):
        self._store = store
        self._handlers = {
            "get": self._get,
            "put": self._put,
            "delete": self._delete,
            "search": self._search,
            "keys": self._keys,
        }

    def execute(self, line: str) -> str | None:
        parts = line.split()
        if not parts:
            return None

        name, args = parts[0], parts[1:]
        handler = self._handlers.get(name)
        if handler is None:
            raise InvalidCommandError(f"unknown command '{name}'")
        return handler(args)

    def _get(self, args) -> str:
        key = self._single_key(args, "get")
        value = self._store.get(key)
        return str(value) if value is not None else f"No entry found for {key}"

    def _put(self, args) -> None:
        if len(args) < 3 or len(args) % 2 == 0:
            raise InvalidCommandError("put expects a key then attribute key/value pairs")
        key, rest = args[0], args[1:]
        self._store.put(key, list(zip(rest[::2], rest[1::2])))
        return None

    def _delete(self, args) -> None:
        self._store.delete(self._single_key(args, "delete"))
        return None

    def _search(self, args) -> str:
        if len(args) != 2:
            raise InvalidCommandError("search expects an attribute key and a value")
        return ",".join(self._store.search(args[0], args[1]))

    def _keys(self, args) -> str:
        if args:
            raise InvalidCommandError("keys takes no arguments")
        return ",".join(self._store.keys())

    @staticmethod
    def _single_key(args, command: str) -> str:
        if len(args) != 1:
            raise InvalidCommandError(f"{command} expects exactly one key")
        return args[0]
