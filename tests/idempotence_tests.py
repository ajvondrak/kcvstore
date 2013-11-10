"""
These are regression tests due to the discovery of some issues using
collections.defaultdict in the KeyColumnValueStore which made some methods
populate the store with new keys erroneously.
"""

import os
import unittest
from kcvstore import KeyColumnValueStore


class GetterTests(unittest.TestCase):
    def setUp(self):
        self.store = KeyColumnValueStore()

    def tearDown(self):
        os.remove(self.store.path)

    # {get} x {get, get_key, get_keys, get_slice}

    def test_get_get(self):
        self.assertEqual(self.store.get('key', 'col'), None)
        self.assertEqual(self.store.get('key', 'col'), None)

    def test_get_get_key(self):
        self.assertEqual(self.store.get('key', 'col'), None)
        self.assertEqual(self.store.get_key('key'), [])

    def test_get_get_keys(self):
        self.assertEqual(self.store.get('key', 'col'), None)
        self.assertEqual(self.store.get_keys(), set())

    def test_get_get_slice(self):
        self.assertEqual(self.store.get('key', 'col'), None)
        self.assertEqual(self.store.get_slice('key', 'col', None), [])

    # {get_key} x {get, get_key, get_keys, get_slice}

    def test_get_key_get(self):
        self.assertEqual(self.store.get_key('key'), [])
        self.assertEqual(self.store.get('key', 'col'), None)

    def test_get_key_get_key(self):
        self.assertEqual(self.store.get_key('key'), [])
        self.assertEqual(self.store.get_key('key'), [])

    def test_get_key_get_keys(self):
        self.assertEqual(self.store.get_key('key'), [])
        self.assertEqual(self.store.get_keys(), set())

    def test_get_key_get_slice(self):
        self.assertEqual(self.store.get_key('key'), [])
        self.assertEqual(self.store.get_slice('key', 'col', None), [])

    # {get_keys} x {get, get_key, get_keys, get_slice}

    def test_get_keys_get(self):
        self.assertEqual(self.store.get_keys(), set())
        self.assertEqual(self.store.get('key', 'col'), None)

    def test_get_keys_get_key(self):
        self.assertEqual(self.store.get_keys(), set())
        self.assertEqual(self.store.get_key('key'), [])

    def test_get_keys_get_keys(self):
        self.assertEqual(self.store.get_keys(), set())
        self.assertEqual(self.store.get_keys(), set())

    def test_get_keys_get_slice(self):
        self.assertEqual(self.store.get_keys(), set())
        self.assertEqual(self.store.get_slice('key', 'col', None), [])

    # {get_slice} x {get, get_key, get_keys, get_slice}

    def test_get_slice_get(self):
        self.assertEqual(self.store.get_slice('key', 'col', None), [])
        self.assertEqual(self.store.get('key', 'col'), None)

    def test_get_slice_get_key(self):
        self.assertEqual(self.store.get_slice('key', 'col', None), [])
        self.assertEqual(self.store.get_key('key'), [])

    def test_get_slice_get_keys(self):
        self.assertEqual(self.store.get_slice('key', 'col', None), [])
        self.assertEqual(self.store.get_keys(), set())

    def test_get_slice_get_slice(self):
        self.assertEqual(self.store.get_slice('key', 'col', None), [])
        self.assertEqual(self.store.get_slice('key', 'col', None), [])


class DeleteMissingKeyTests(unittest.TestCase):
    def setUp(self):
        self.store = KeyColumnValueStore()

    def tearDown(self):
        os.remove(self.store.path)

    def test_delete_get_keys(self):
        self.store.delete('key', 'col')
        self.assertEqual(self.store.get_keys(), set())

    def test_delete_key_get_keys(self):
        self.store.delete_key('key')
        self.assertEqual(self.store.get_keys(), set())
