from threading import RLock

from core.schema import SchemaRegistry
from models.attribute import coerce
from models.errors import DataTypeError
from models.value import Value


class KeyValueStore:
    """Thread-safe in-memory key-value store with an inverted index for search.

    Complexity, where A is the attribute count of one value:
        get     O(1)
        put     O(A)   validate, re-index the replaced value, index the new one
        delete  O(A)
        search  O(1) lookup + O(M log M) to sort the M matching keys
        keys    O(N log N) to sort N keys
    """

    def __init__(self):
        self._lock = RLock()
        self._values: dict[str, Value] = {}
        self._schema = SchemaRegistry()
        self._index: dict[tuple[str, object], set[str]] = {}

    def get(self, key: str) -> Value | None:
        with self._lock:
            return self._values.get(key)

    def put(self, key: str, attribute_pairs) -> None:
        with self._lock:
            # Validate first: this raises before a single byte of state changes.
            attributes, new_types = self._schema.resolve(attribute_pairs)

            replaced = self._values.get(key)
            if replaced is not None:
                self._unindex(key, replaced)

            self._schema.commit(new_types)
            value = Value(attributes)
            self._values[key] = value
            self._index_value(key, value)

    def delete(self, key: str) -> bool:
        with self._lock:
            value = self._values.pop(key, None)
            if value is None:
                return False
            self._unindex(key, value)
            return True

    def search(self, attribute_key: str, attribute_value: str) -> list[str]:
        with self._lock:
            attribute_type = self._schema.type_of(attribute_key)
            if attribute_type is None:
                return []
            try:
                needle = coerce(attribute_value, attribute_type)
            except DataTypeError:
                return []
            return sorted(self._index.get((attribute_key, needle), ()))

    def keys(self) -> list[str]:
        with self._lock:
            return sorted(self._values)

    def _index_value(self, key: str, value: Value) -> None:
        for attribute in value.attributes():
            self._index.setdefault((attribute.key, attribute.value), set()).add(key)

    def _unindex(self, key: str, value: Value) -> None:
        for attribute in value.attributes():
            index_key = (attribute.key, attribute.value)
            bucket = self._index.get(index_key)
            if bucket is None:
                continue
            bucket.discard(key)
            if not bucket:
                del self._index[index_key]
