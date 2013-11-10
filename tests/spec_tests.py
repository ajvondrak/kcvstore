"""
Test the examples given in the project specification.
"""

import unittest
from kcvstore import KeyColumnValueStore


class LevelOneSpecTests(unittest.TestCase):
    def setUp(self):
        self.store = KeyColumnValueStore()
        self.store.set('a', 'aa', 'x')
        self.store.set('a', 'ab', 'x')
        self.store.set('c', 'cc', 'x')
        self.store.set('c', 'cd', 'x')
        self.store.set('d', 'de', 'x')
        self.store.set('d', 'df', 'x')

    def test_get(self):
        self.assertEqual(self.store.get('a', 'aa'), 'x')

    def test_get_key(self):
        self.assertEqual(self.store.get_key('a'), [('aa', 'x'), ('ab', 'x')])

    def test_nonexistent_get(self):
        self.assertEqual(self.store.get('z', 'yy'), None)

    def test_nonexistent_get_key(self):
        self.assertEqual(self.store.get_key('z'), [])

    def test_get_on_overwritten_value(self):
        self.store.set('a', 'aa', 'y')
        self.assertEqual(self.store.get('a', 'aa'), 'y')

    def test_get_key_on_overwritten_values(self):
        self.store.set('a', 'aa', 'y')
        self.store.set('a', 'ab', 'z')
        self.assertEqual(self.store.get_key('a'), [('aa', 'y'), ('ab', 'z')])

    def test_delete(self):
        self.store.delete('d', 'df')
        self.assertEqual(self.store.get_key('d'), [('de', 'x')])

    def test_delete_key(self):
        self.store.delete_key('c')
        self.assertEqual(self.store.get_key('c'), [])


class LevelTwoSpecTests(unittest.TestCase):
    def setUp(self):
        self.store = KeyColumnValueStore()
        self.store.set('a', 'aa', 'x')
        self.store.set('a', 'ab', 'x')
        self.store.set('a', 'ac', 'x')
        self.store.set('a', 'ad', 'x')
        self.store.set('a', 'ae', 'x')
        self.store.set('a', 'af', 'x')
        self.store.set('a', 'ag', 'x')

    def test_get_slice(self):
        self.assertEqual(self.store.get_slice('a', 'ac', 'ae'),
                         [('ac', 'x'), ('ad', 'x'), ('ae', 'x')])

    def test_get_slice_open_right(self):
        self.assertEqual(self.store.get_slice('a', 'ae', None),
                         [('ae', 'x'), ('af', 'x'), ('ag', 'x')])

    def test_get_slice_open_left(self):
        self.assertEqual(self.store.get_slice('a', None, 'ac'),
                         [('aa', 'x'), ('ab', 'x'), ('ac', 'x')])
