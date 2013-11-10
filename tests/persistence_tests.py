import os
import unittest
from kcvstore import KeyColumnValueStore


class PersistenceTests(unittest.TestCase):
    def setUp(self):
        self.store = KeyColumnValueStore()

    def tearDown(self):
        os.remove(self.store.path)

    def test_init_persists(self):
        new_store = KeyColumnValueStore(path=self.store.path)
        self.assertEqual(new_store.get('any key', 'any col'), None)
        self.assertEqual(new_store.get_key('any key'), [])
        self.assertEqual(new_store.get_keys(), set())

    def test_set_persists(self):
        self.store.set('key', 'col', 'val')
        new_store = KeyColumnValueStore(path=self.store.path)
        self.assertEqual(new_store.get('key', 'col'), 'val')

    def test_set_overwrites(self):
        self.store.set('key', 'col', 'val')
        self.store.set('key', 'col', 'new_val')
        new_store = KeyColumnValueStore(path=self.store.path)
        self.assertEqual(new_store.get('key', 'col'), 'new_val')

    def test_delete_persists(self):
        self.store.set('key', 'colA', 'val')
        self.store.set('key', 'colB', 'val')
        self.store.delete('key', 'colA')
        new_store = KeyColumnValueStore(path=self.store.path)
        self.assertEqual(new_store.get_key('key'), [('colB', 'val')])

    def test_delete_key_persists(self):
        self.store.set('keyA', 'col', 'val')
        self.store.set('keyB', 'col', 'val')
        self.store.delete_key('keyB')
        new_store = KeyColumnValueStore(path=self.store.path)
        self.assertEqual(new_store.get_keys(), {'keyA'})
