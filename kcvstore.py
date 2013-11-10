blist_is_in_the_spirit_of_the_challenge = True

if blist_is_in_the_spirit_of_the_challenge:
    try:
        from blist import sorteddict
        use_blist = True
    except ImportError:
        import bisect
        use_blist = False
else:
    import bisect
    use_blist = False


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

    if use_blist:

        def __init__(self):
            self.kcv = {}

        def set(self, key, col, val):
            """Sets the value at the given key/column."""
            assert all(isinstance(datum, str) for datum in (key, col, val))
            self.kcv.setdefault(key, sorteddict())[col] = val

        def get(self, key, col):
            """Return the value at the specified key/column."""
            cv = self.kcv.get(key)
            return None if cv is None else cv.get(col)

        def get_key(self, key):
            """Returns a sorted list of column/value tuples."""
            cv = self.kcv.get(key)
            return [] if cv is None else list(cv.items())

        def get_keys(self):
            """Returns a set containing all of the keys in the store."""
            return set(self.kcv.keys())

        def delete(self, key, col):
            """Removes a column/value from the given key."""
            if key in self.kcv:
                if col in self.kcv[key]:
                    del self.kcv[key][col]

        def delete_key(self, key):
            """Removes all data associated with the given key."""
            if key in self.kcv:
                del self.kcv[key]

    else:

        def __init__(self):
            self.columns = {}  # key -> set(col)
            self.ordered = {}  # key -> list(col)
            self.value = {}    # (key, col) -> val

        def set(self, key, col, val):
            """Sets the value at the given key/column."""
            assert all(isinstance(datum, str) for datum in (key, col, val))
            self.columns.setdefault(key, set())
            self.ordered.setdefault(key, [])
            if col not in self.columns[key]:
                self.columns[key].add(col)
                bisect.insort(self.ordered[key], col)
            self.value[(key, col)] = val

        def get(self, key, col):
            """Return the value at the specified key/column."""
            return self.value.get((key, col))

        def get_key(self, key):
            """Returns a sorted list of column/value tuples."""
            return [(c, self.get(key, c)) for c in self.ordered.get(key, [])]

        def get_keys(self):
            """Returns a set containing all of the keys in the store."""
            return set(self.columns.iterkeys())

        def delete(self, key, col):
            """Removes a column/value from the given key."""
            if (key, col) in self.value:
                del self.value[(key, col)]
                self.columns[key].remove(col)
                sorted_cols = self.ordered[key]
                sorted_cols.pop(bisect.bisect_left(sorted_cols, col))

        def delete_key(self, key):
            """Removes all data associated with the given key."""
            if key in self.columns:
                cols = self.columns[key]
                del self.columns[key]
                del self.ordered[key]
                for col in cols:
                    del self.value[(key, col)]