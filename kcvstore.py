import bisect

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
        self.key_to_cols = {}
        self.key_to_sorted_cols = {}
        self.keycol_to_val = {}

    def set(self, key, col, val):
        """Sets the value at the given key/column."""
        assert isinstance(key, str)
        assert isinstance(col, str)
        assert isinstance(val, str)
        self.key_to_cols.setdefault(key, set())
        self.key_to_sorted_cols.setdefault(key, [])
        if col not in self.key_to_cols[key]:
            self.key_to_cols[key].add(col)
            bisect.insort(self.key_to_sorted_cols[key], col)
        self.keycol_to_val[(key, col)] = val

    def get(self, key, col):
        """Return the value at the specified key/column."""
        return self.keycol_to_val.get((key, col))

    def get_key(self, key):
        """Returns a sorted list of column/value tuples."""
        sorted_cols = self.key_to_sorted_cols.get(key, [])
        return [(c, self.get(key, c)) for c in sorted_cols]

    def get_keys(self):
        """Returns a set containing all of the keys in the store."""
        return set(self.key_to_cols)

    def delete(self, key, col):
        """Removes a column/value from the given key."""
        if (key, col) in self.keycol_to_val:
            del self.keycol_to_val[(key, col)]
            self.key_to_cols[key].remove(col)
            sorted_cols = self.key_to_sorted_cols[key]
            sorted_cols.pop(bisect.bisect_left(sorted_cols, col))

    def delete_key(self, key):
        """Removes all data associated with the given key."""
        if key in self.key_to_cols:
            cols = self.key_to_cols[key]
            del self.key_to_cols[key]
            del self.key_to_sorted_cols[key]
            for col in cols:
                del self.keycol_to_val[(key, col)]
