from core import path as pathlib
from models.errors import (
    AlreadyExists,
    InvalidMove,
    IsADirectory,
    NotADirectory,
    NotFound,
)
from models.node import Directory, File


class FileSystem:
    """An in-memory tree of directories and files, addressed by absolute path.

    Complexity, where D is the depth of a path and N the number of nodes:
        mkdir / add_file / cat / rm / mv   O(D)
        ls                                 O(D + C log C) for C children
        find                               O(N)
    """

    def __init__(self):
        self._root = Directory("")

    def mkdir(self, path):
        parent, name = self._parent_directory(path)
        self._reject_existing(parent, name, path)
        parent.children[name] = Directory(name)

    def add_file(self, path, content):
        parent, name = self._parent_directory(path)
        self._reject_existing(parent, name, path)
        parent.children[name] = File(name, content)

    def ls(self, path):
        node = self._resolve(path)
        return sorted(node.children) if node.is_directory else [node.name]

    def cat(self, path):
        node = self._resolve(path)
        if node.is_directory:
            raise IsADirectory(pathlib.normalize(path))
        return node.content

    def rm(self, path):
        parent, name = self._parent_directory(path)
        if name not in parent.children:
            raise NotFound(pathlib.normalize(path))
        del parent.children[name]      # dropping the reference drops the whole subtree

    def mv(self, source, destination):
        source_path = pathlib.normalize(source)
        destination_path = pathlib.normalize(destination)

        # Validate everything before touching the tree.
        node = self._resolve(source_path)
        if destination_path == source_path or destination_path.startswith(source_path + "/"):
            raise InvalidMove(source_path)
        target_parent, new_name = self._parent_directory(destination_path)
        self._reject_existing(target_parent, new_name, destination_path)
        source_parent, old_name = self._parent_directory(source_path)

        del source_parent.children[old_name]
        node.name = new_name
        target_parent.children[new_name] = node

    def find(self, name):
        matches, stack = [], [(self._root, "")]
        while stack:                                    # iterative: no recursion limit
            node, prefix = stack.pop()
            if not node.is_directory:
                continue
            for child_name, child in node.children.items():
                child_path = f"{prefix}/{child_name}"
                if child_name == name:
                    matches.append(child_path)
                stack.append((child, child_path))
        return sorted(matches)

    def _resolve(self, path):
        """Walk a path to its node. Every command goes through here."""
        node, walked = self._root, ""
        for part in pathlib.split(path):
            if not node.is_directory:
                raise NotADirectory(walked)
            walked = f"{walked}/{part}"
            node = node.children.get(part)
            if node is None:
                raise NotFound(walked)
        return node

    def _parent_directory(self, path):
        """The directory that should contain `path`, plus the final name."""
        parent_path, name = pathlib.parent_and_name(path)
        node = self._resolve(parent_path)``
        if not node.is_directory:
            raise NotADirectory(parent_path)
        return node, name

    @staticmethod
    def _reject_existing(parent, name, path):
        if name in parent.children:
            raise AlreadyExists(pathlib.normalize(path))
