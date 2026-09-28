class Node:
    """A named entry in the tree. `is_directory` avoids isinstance checks at call sites."""

    is_directory = False

    def __init__(self, name):
        self.name = name


class File(Node):
    def __init__(self, name, content=""):
        super().__init__(name)
        self.content = content


class Directory(Node):
    is_directory = True

    def __init__(self, name):
        super().__init__(name)
        self.children = {}          # name -> Node
