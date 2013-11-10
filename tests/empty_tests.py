import os
import unittest
from kcvstore import KeyColumnValueStore


class EmptyStoreTests(unittest.TestCase):
    def setUp(self):
        self.empty_store = KeyColumnValueStore()

    def tearDown(self):
        os.remove(self.empty_store.path)

    def test_get(self):
        self.assertEqual(self.empty_store.get('any key', 'any col'), None)

    def test_get_key(self):
        self.assertEqual(self.empty_store.get_key('any key'), [])

    def test_get_keys(self):
        self.assertEqual(self.empty_store.get_keys(), set())

    def test_delete(self):
        try:
            self.empty_store.delete('any key', 'any col')
        except Exception:
            self.fail('Deletion on empty stores should not raise exceptions.')

    def test_delete_key(self):
        try:
            self.empty_store.delete_key('any key')
        except Exception:
            self.fail('Deletion on empty stores should not raise exceptions.')

    def test_get_slice(self):
        slice_ = self.empty_store.get_slice('any key', 'any start', 'any stop')
        self.assertEqual(slice_, [])
