from collections import defaultdict

blist_is_in_the_spirit_of_the_challenge = True

if blist_is_in_the_spirit_of_the_challenge:
    try:
        from blist import sorteddict
        use_bisect = False
    except ImportError:
        import bisect
        use_bisect = True
else:
    import bisect
    use_bisect = True


class KeyColumnValueStore(object):
    """A key/column/value store.

    A key/column/value store is similar to a nested hash table, with the
    following requirements:
    * like a hash table, a key can only occur once
    * within a given key, a column cannot appear more than once, like a hash
      table
    * when querying the contents of a key, a list of column/value tuples are
      returned, sorted by column
    * all keys, columns, and values will be strings of variable length
    * errors shouldn't be raised if a nonexistent key/column is accessed, empty
      lists / None values should be returned

    The implementation is designed with the assumption that reads will be much
    more frequent than writes.
    """

    def __init__(self):
        self.ordered_columns = {}  # key -> list(col)
        if use_bisect:
            self.kcv = defaultdict(lambda: {})  # key -> (col -> val)
        else:
            self.kcv = defaultdict(lambda: sorteddict())

    def _track_column_order(self, key, col):
        """Adds `col` to the ordered list of columns associated with `key`."""
        if use_bisect:
            if col not in self.kcv[key]:
                self.ordered_columns.setdefault(key, [])
                bisect.insort(self.ordered_columns[key], col)

    def set(self, key, col, val):
        """Sets the value at the given key/column."""
        assert all(isinstance(datum, str) for datum in (key, col, val))
        self._track_column_order(key, col)
        self.kcv[key][col] = val

    def get(self, key, col):
        """Return the value at the specified key/column."""
        cv = self.kcv.get(key)
        return None if cv is None else cv.get(col)

    def get_key(self, key):
        """Returns a sorted list of column/value tuples."""
        if use_bisect:
            cols = self.ordered_columns.get(key, [])
        else:
            cols = self.kcv[key]
        return [(c, self.get(key, c)) for c in cols]

    def get_keys(self):
        """Returns a set containing all of the keys in the store."""
        return set(self.kcv.keys())

    def _forget_column_order(self, key, col):
        """Removes `col` from the ordered list of columns of `key`."""
        if use_bisect:
            cols = self.ordered_columns[key]
            cols.pop(bisect.bisect_left(cols, col))

    def delete(self, key, col):
        """Removes a column/value from the given key."""
        if key in self.kcv:
            if col in self.kcv[key]:
                del self.kcv[key][col]
                self._forget_column_order(key, col)

    def delete_key(self, key):
        """Removes all data associated with the given key."""
        if key in self.kcv:
            del self.kcv[key]
            if use_bisect:
                del self.ordered_columns[key]
