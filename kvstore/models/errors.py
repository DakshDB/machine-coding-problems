class StoreError(Exception):
    """Base for every error raised by the key-value store."""


class DataTypeError(StoreError):
    """An attribute was given a value of a type it was not first seen with."""


class InvalidCommandError(StoreError):
    """A command line could not be parsed."""
