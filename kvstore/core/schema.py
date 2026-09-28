from models.attribute import Attribute, AttributeType, infer_type, parse
from models.errors import DataTypeError


class SchemaRegistry:
    """Remembers the type each attribute was first seen with; that type is then fixed.

    Validation is split from commit so a rejected `put` leaves nothing behind -
    neither data nor a newly registered type.
    """

    def __init__(self):
        self._types: dict[str, AttributeType] = {}

    def type_of(self, attribute_key: str) -> AttributeType | None:
        return self._types.get(attribute_key)

    def resolve(self, pairs) -> tuple[dict[str, Attribute], dict[str, AttributeType]]:
        """Validate a whole batch without mutating anything.

        Returns the attributes to store and the types this batch would newly
        register. Raises DataTypeError on the first conflict.
        """
        attributes: dict[str, Attribute] = {}
        new_types: dict[str, AttributeType] = {}

        for attribute_key, raw in pairs:
            inferred = infer_type(raw)
            known = self._types.get(attribute_key, new_types.get(attribute_key))

            if known is None:
                known = inferred
                new_types[attribute_key] = inferred
            elif known is not inferred:
                raise DataTypeError(
                    f"attribute '{attribute_key}' is {known.value}, "
                    f"got {inferred.value} ('{raw}')"
                )

            attributes[attribute_key] = Attribute(attribute_key, raw, parse(raw, known), known)

        return attributes, new_types

    def commit(self, new_types: dict[str, AttributeType]) -> None:
        self._types.update(new_types)
