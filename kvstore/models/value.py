from models.attribute import Attribute


class Value:
    """The object stored against a key: an ordered map of attribute name to Attribute."""

    def __init__(self, attributes: dict[str, Attribute]):
        self._attributes = dict(attributes)

    def attributes(self):
        return self._attributes.values()

    def __getitem__(self, name: str) -> Attribute:
        return self._attributes[name]

    def __contains__(self, name: str) -> bool:
        return name in self._attributes

    def __len__(self) -> int:
        return len(self._attributes)

    def __str__(self) -> str:
        return ", ".join(f"{a.key}: {a.raw}" for a in self._attributes.values())

    def __repr__(self) -> str:
        return f"Value({self})"
