class FileSystemError(Exception):
    """Base for every error the file system raises. The driver prints str(error)."""


class NotFound(FileSystemError):
    def __init__(self, path):
        super().__init__(f"No such file or directory: {path}")


class AlreadyExists(FileSystemError):
    def __init__(self, path):
        super().__init__(f"Already exists: {path}")


class NotADirectory(FileSystemError):
    def __init__(self, path):
        super().__init__(f"Not a directory: {path}")


class IsADirectory(FileSystemError):
    def __init__(self, path):
        super().__init__(f"Is a directory: {path}")


class InvalidMove(FileSystemError):
    def __init__(self, source):
        super().__init__(f"Invalid move: {source} into its own subtree")


class InvalidOperation(FileSystemError):
    pass
