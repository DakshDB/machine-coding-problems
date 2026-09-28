from models.errors import InvalidOperation

ROOT = "/"


def split(path):
    """'/a/b/' -> ['a', 'b'];  '/' -> []"""
    if not path.startswith(ROOT):
        raise InvalidOperation(f"Path must be absolute: {path}")
    return [part for part in path.split("/") if part]


def normalize(path):
    """Canonical form, so '/docs/' and '/docs' compare equal."""
    return ROOT + "/".join(split(path))


def parent_and_name(path):
    """'/a/b' -> ('/a', 'b'). Raises for the root, which has no parent."""
    parts = split(path)
    if not parts:
        raise InvalidOperation(f"Cannot operate on the root: {normalize(path)}")
    return ROOT + "/".join(parts[:-1]), parts[-1]
