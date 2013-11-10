import random
import string
from kcvstore import KeyColumnValueStore


def test_get_keys_after_delete_key():
    sample_size = random.randint(0, len(string.printable))
    keys = random.sample(string.printable, sample_size)
    store = KeyColumnValueStore()
    for key in keys:
        store.set(key, 'col', 'val')
    assert store.get_keys() == set(keys)
    # Now delete keys one-by-one
    remaining_keys = set(keys)
    while remaining_keys:
        delete_me = random.choice(list(remaining_keys))
        store.delete_key(delete_me)
        remaining_keys.remove(delete_me)
        assert store.get_keys() == remaining_keys


def test_get_key_returns_sorted_columns():
    cols = list(string.printable)
    random.shuffle(cols)
    store = KeyColumnValueStore()
    for col in cols:
        store.set('key', col, 'val')
    retrieved_cols = [c for c, v in store.get_key('key')]
    assert retrieved_cols == sorted(cols)


def test_get_set():
    vals = list(string.printable)
    random.shuffle(vals)
    store = KeyColumnValueStore()
    for val in vals:
        store.set('key', 'col', val)
        assert store.get('key', 'col') == val
        assert store.get_key('key') == [('col', val)]
        assert store.get_keys() == {'key'}


def test_get_slice_returns_sorted_columns():
    cols = list(string.printable)
    random.shuffle(cols)
    store = KeyColumnValueStore()
    for col in cols:
        store.set('key', col, 'val')
    slice_ = store.get_slice('key', random.choice(cols), random.choice(cols))
    assert slice_ == sorted(slice_)
