import threading
import unittest

from core.commands import CommandProcessor
from core.store import KeyValueStore
from main import run
from models.errors import DataTypeError, InvalidCommandError


def pairs(*flat):
    return list(zip(flat[::2], flat[1::2]))


class TestValueFormatting(unittest.TestCase):
    def test_to_string_preserves_input_form_and_order(self):
        store = KeyValueStore()
        store.put("k", pairs("title", "SDE", "price", "30000.00", "ok", "false", "n", "30"))
        self.assertEqual(str(store.get("k")), "title: SDE, price: 30000.00, ok: false, n: 30")

    def test_missing_key_returns_none(self):
        self.assertIsNone(KeyValueStore().get("nope"))


class TestTypeFixing(unittest.TestCase):
    def setUp(self):
        self.store = KeyValueStore()
        self.store.put("a", pairs("age", "30", "price", "10.50", "active", "true"))

    def test_conflicting_type_raises(self):
        for attribute, bad in (("age", "abc"), ("price", "4000"), ("active", "yes")):
            with self.subTest(attribute=attribute):
                with self.assertRaises(DataTypeError):
                    self.store.put("b", pairs(attribute, bad))

    def test_same_type_is_accepted(self):
        self.store.put("b", pairs("age", "41", "price", "0.5", "active", "false"))
        self.assertEqual(self.store.get("b")["age"].value, 41)

    def test_conflict_inside_one_batch_raises(self):
        with self.assertRaises(DataTypeError):
            self.store.put("b", pairs("size", "10", "size", "big"))


class TestPutIsAtomic(unittest.TestCase):
    """A rejected put must leave no data AND no newly registered attribute type."""

    def setUp(self):
        self.store = KeyValueStore()
        self.store.put("a", pairs("age", "30"))

    def test_rejected_put_stores_nothing(self):
        with self.assertRaises(DataTypeError):
            self.store.put("b", pairs("age", "abc"))
        self.assertIsNone(self.store.get("b"))
        self.assertEqual(self.store.keys(), ["a"])

    def test_rejected_put_does_not_register_new_attribute_types(self):
        with self.assertRaises(DataTypeError):
            self.store.put("b", pairs("brand_new", "5", "age", "abc"))
        # brand_new must still be unclaimed, so a string is legal for it now
        self.store.put("c", pairs("brand_new", "hello"))
        self.assertEqual(str(self.store.get("c")), "brand_new: hello")


class TestSearchIndex(unittest.TestCase):
    def setUp(self):
        self.store = KeyValueStore()
        self.store.put("k1", pairs("colour", "red", "size", "10"))
        self.store.put("k2", pairs("colour", "red", "size", "20"))
        self.store.put("k3", pairs("colour", "blue", "size", "10"))

    def test_search_returns_sorted_matches(self):
        self.assertEqual(self.store.search("colour", "red"), ["k1", "k2"])
        self.assertEqual(self.store.search("size", "10"), ["k1", "k3"])

    def test_replacing_a_key_clears_its_old_index_entries(self):
        self.store.put("k1", pairs("colour", "green", "size", "10"))
        self.assertEqual(self.store.search("colour", "red"), ["k2"])
        self.assertEqual(self.store.search("colour", "green"), ["k1"])

    def test_delete_clears_index_entries(self):
        self.assertTrue(self.store.delete("k1"))
        self.assertEqual(self.store.search("colour", "red"), ["k2"])
        self.assertFalse(self.store.delete("k1"))

    def test_search_unknown_attribute_or_value_is_empty(self):
        self.assertEqual(self.store.search("nothing", "red"), [])
        self.assertEqual(self.store.search("colour", "purple"), [])
        self.assertEqual(self.store.search("size", "not_a_number"), [])

    def test_search_coerces_the_query_to_the_registered_type(self):
        self.store.put("k4", pairs("rate", "10.00"))
        self.assertEqual(self.store.search("rate", "10.0"), ["k4"])

    def test_keys_are_sorted(self):
        self.assertEqual(self.store.keys(), ["k1", "k2", "k3"])


class TestCommandParsing(unittest.TestCase):
    def test_processor_raises_on_malformed_commands(self):
        processor = CommandProcessor(KeyValueStore())
        for line in ("put k a", "put k", "get", "get a b", "keys extra", "search only", "wat"):
            with self.subTest(line=line):
                with self.assertRaises(InvalidCommandError):
                    processor.execute(line)

    def test_driver_turns_those_into_output_instead_of_crashing(self):
        self.assertEqual(list(run(["wat"])), ["unknown command 'wat'"])

    def test_driver_reports_data_type_error(self):
        out = list(run(["put a age 30", "put b age abc", "get b"]))
        self.assertEqual(out, ["Data Type Error", "No entry found for b"])

    def test_exit_stops_processing(self):
        self.assertEqual(list(run(["keys", "exit", "put x y 1"])), [""])


class TestThreadSafety(unittest.TestCase):
    def test_concurrent_writers_leave_consistent_state(self):
        store = KeyValueStore()
        store.put("seed", pairs("n", "0"))
        errors = []

        def worker(worker_id):
            try:
                for i in range(200):
                    key = f"k{worker_id}_{i}"
                    store.put(key, pairs("owner", str(worker_id), "n", str(i)))
                    store.get(key)
                    store.search("owner", str(worker_id))
                    if i % 2:
                        store.delete(key)
            except Exception as error:                # noqa: BLE001 - surfaced below
                errors.append(error)

        threads = [threading.Thread(target=worker, args=(w,)) for w in range(8)]
        for t in threads: t.start()
        for t in threads: t.join()

        self.assertEqual(errors, [])
        self.assertEqual(len(store.keys()), 8 * 100 + 1)
        for worker_id in range(8):
            found = store.search("owner", str(worker_id))
            self.assertEqual(len(found), 100)
            self.assertTrue(all(store.get(k) is not None for k in found))


if __name__ == "__main__":
    unittest.main(verbosity=2)
