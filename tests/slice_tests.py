import string
import unittest
from kcvstore import KeyColumnValueStore


class SliceTests(unittest.TestCase):
    def setUp(self):
        self.store = KeyColumnValueStore()
        for col in string.ascii_lowercase:
            self.store.set('lowercase', col, 'val')
        for col in string.ascii_uppercase:
            self.store.set('uppercase', col, 'val')

    def test_open_slice(self):
        self.assertEqual(self.store.get_slice('lowercase', None, None),
                         [(c, 'val') for c in string.ascii_lowercase])
        self.assertEqual(self.store.get_slice('uppercase', None, None),
                         [(c, 'val') for c in string.ascii_uppercase])

    def test_equal_endpoints(self):
        for c in string.ascii_lowercase:
            self.assertEqual(self.store.get_slice('lowercase', c, c),
                             [(c, 'val')])
        for c in string.ascii_uppercase:
            self.assertEqual(self.store.get_slice('uppercase', c, c),
                             [(c, 'val')])

    def test_start_after_stop(self):
        self.assertEqual(self.store.get_slice('lowercase', 'z', 'a'), [])
        self.assertEqual(self.store.get_slice('uppercase', 'Q', 'B'), [])

    # XXX This behavior was unspecified, but I've written these tests (and the
    # get_slice implementation) with what I thought made sense, by way of
    # analogy with Python's list slices.  Other interpretations would certainly
    # be valid, of course.

    def test_nonexistent_endpoints(self):
        self.assertEqual(self.store.get_slice('lowercase', 'A', 'Z'), [])
        self.assertEqual(self.store.get_slice('uppercase', 'f', 'u'), [])

    def test_nonexistent_stop(self):
        self.assertEqual(self.store.get_slice('lowercase', 'a', 'whatever'),
                         self.store.get_slice('lowercase', 'a', None))
        self.assertEqual(self.store.get_slice('uppercase', 'C', 'AA'),
                         self.store.get_slice('uppercase', 'C', None))

    def test_nonexistent_start(self):
        self.assertEqual(self.store.get_slice('lowercase', 'whatever', 'k'),
                         self.store.get_slice('lowercase', None, 'k'))
        self.assertEqual(self.store.get_slice('uppercase', 'BB', 'Q'),
                         self.store.get_slice('uppercase', None, 'Q'))

    def test_nonexistent_key(self):
        self.assertEqual(self.store.get_slice('mixedcase', 'a', 'Z'), [])
        self.assertEqual(self.store.get_slice('mixedcase', None, 'Z'), [])
        self.assertEqual(self.store.get_slice('mixedcase', 'a', None), [])
        self.assertEqual(self.store.get_slice('mixedcase', None, None), [])
