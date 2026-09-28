import re
from dataclasses import dataclass
from enum import Enum

from models.errors import DataTypeError


class AttributeType(Enum):
    BOOLEAN = "boolean"
    INTEGER = "integer"
    DOUBLE = "double"
    STRING = "string"


_BOOLEAN_LITERALS = {"true", "false"}
_INTEGER_RE = re.compile(r"^[+-]?\d+$")
_DOUBLE_RE = re.compile(r"^[+-]?(?:\d+\.\d*|\.\d+)(?:[eE][+-]?\d+)?$|^[+-]?\d+[eE][+-]?\d+$")

_PARSERS = {
    AttributeType.BOOLEAN: lambda raw: raw.lower() == "true",
    AttributeType.INTEGER: int,
    AttributeType.DOUBLE: float,
    AttributeType.STRING: str,
}


def infer_type(raw: str) -> AttributeType:
    """The type a raw token looks like, checked most specific first."""
    if raw.lower() in _BOOLEAN_LITERALS:
        return AttributeType.BOOLEAN
    if _INTEGER_RE.match(raw):
        return AttributeType.INTEGER
    if _DOUBLE_RE.match(raw):
        return AttributeType.DOUBLE
    return AttributeType.STRING


def parse(raw: str, attribute_type: AttributeType):
    return _PARSERS[attribute_type](raw)


def coerce(raw: str, attribute_type: AttributeType):
    """Read raw as attribute_type, raising DataTypeError when it does not fit."""
    if attribute_type is AttributeType.BOOLEAN and raw.lower() not in _BOOLEAN_LITERALS:
        raise DataTypeError(f"'{raw}' is not a boolean")
    try:
        return _PARSERS[attribute_type](raw)
    except ValueError:
        raise DataTypeError(f"'{raw}' is not {attribute_type.value}") from None


@dataclass(frozen=True)
class Attribute:
    """One attribute of a stored value.

    `raw` is kept alongside `value` so output reproduces the input exactly
    (30000.00 prints as 30000.00), while comparisons use the typed value.
    """

    key: str
    raw: str
    value: object
    type: AttributeType
