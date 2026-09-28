import unittest

from core.file_system import FileSystem
from main import run
from models.errors import (
    AlreadyExists,
    InvalidMove,
    InvalidOperation,
    IsADirectory,
    NotADirectory,
    NotFound,
)


class TestFileSystem(unittest.TestCase):
    def setUp(self):
        self.fs = FileSystem()
        self.fs.mkdir("/docs")
        self.fs.mkdir("/docs/work")
        self.fs.add_file("/docs/work/notes.txt", "hello")
        self.fs.add_file("/docs/readme.md", "welcome")

    def test_ls_sorts_children(self):
        self.assertEqual(self.fs.ls("/docs"), ["readme.md", "work"])
        self.assertEqual(self.fs.ls("/"), ["docs"])

    def test_ls_on_a_file_returns_its_name(self):
        self.assertEqual(self.fs.ls("/docs/readme.md"), ["readme.md"])

    def test_cat(self):
        self.assertEqual(self.fs.cat("/docs/work/notes.txt"), "hello")
        with self.assertRaises(IsADirectory):
            self.fs.cat("/docs")

    def test_missing_paths(self):
        for path in ("/nope", "/docs/nope", "/docs/work/nope"):
            with self.subTest(path=path), self.assertRaises(NotFound):
                self.fs.ls(path)

    def test_creating_under_a_file_is_not_a_directory(self):
        with self.assertRaises(NotADirectory):
            self.fs.mkdir("/docs/readme.md/child")

    def test_duplicate_names(self):
        with self.assertRaises(AlreadyExists):
            self.fs.mkdir("/docs")
        with self.assertRaises(AlreadyExists):
            self.fs.add_file("/docs", "x")      # file cannot shadow a directory

    def test_rm_removes_the_whole_subtree(self):
        self.fs.rm("/docs")
        self.assertEqual(self.fs.ls("/"), [])
        self.assertEqual(self.fs.find("notes.txt"), [])

    def test_rm_missing_and_root(self):
        with self.assertRaises(NotFound):
            self.fs.rm("/nope")
        with self.assertRaises(InvalidOperation):
            self.fs.rm("/")

    def test_mv_renames_and_relocates(self):
        self.fs.mv("/docs/work", "/archive")
        self.assertEqual(self.fs.ls("/"), ["archive", "docs"])
        self.assertEqual(self.fs.cat("/archive/notes.txt"), "hello")
        self.assertEqual(self.fs.ls("/docs"), ["readme.md"])

    def test_mv_into_own_subtree_is_rejected(self):
        for destination in ("/docs/inner", "/docs/work/inner", "/docs"):
            with self.subTest(destination=destination):
                with self.assertRaises(InvalidMove):
                    self.fs.mv("/docs", destination)
        self.assertEqual(self.fs.ls("/docs"), ["readme.md", "work"])   # tree untouched

    def test_mv_allows_a_sibling_with_a_shared_prefix(self):
        self.fs.mkdir("/docs2")
        self.fs.mv("/docs", "/docs2/moved")            # /docs2 is NOT under /docs
        self.assertEqual(self.fs.ls("/docs2"), ["moved"])

    def test_mv_validates_before_mutating(self):
        with self.assertRaises(AlreadyExists):
            self.fs.mv("/docs/work", "/docs/readme.md")
        self.assertEqual(self.fs.ls("/docs"), ["readme.md", "work"])   # nothing moved
        with self.assertRaises(NotFound):
            self.fs.mv("/docs/work", "/nowhere/here")
        self.assertEqual(self.fs.ls("/docs"), ["readme.md", "work"])

    def test_find_returns_sorted_absolute_paths(self):
        self.fs.mkdir("/backup")
        self.fs.add_file("/backup/notes.txt", "copy")
        self.assertEqual(self.fs.find("notes.txt"),
                         ["/backup/notes.txt", "/docs/work/notes.txt"])
        self.assertEqual(self.fs.find("work"), ["/docs/work"])
        self.assertEqual(self.fs.find("nothing"), [])

    def test_trailing_slashes_are_equivalent(self):
        self.assertEqual(self.fs.ls("/docs/"), self.fs.ls("/docs"))

    def test_relative_paths_are_rejected(self):
        with self.assertRaises(InvalidOperation):
            self.fs.ls("docs")


class TestDriver(unittest.TestCase):
    def test_errors_become_output_lines(self):
        self.assertEqual(list(run(["cat /nope"])), ["No such file or directory: /nope"])

    def test_unknown_command(self):
        self.assertEqual(list(run(["wat /x"])), ["Unknown command: wat"])

    def test_exit_stops_processing(self):
        self.assertEqual(list(run(["mkdir /a", "exit", "cat /nope"])), [])

    def test_empty_results_print_a_blank_line(self):
        self.assertEqual(list(run(["ls /", "find zzz"])), ["", ""])


if __name__ == "__main__":
    unittest.main(verbosity=2)
