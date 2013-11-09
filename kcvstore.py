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

    def set(self, key, col, val):
        """Sets the value at the given key/column."""
        pass

    def get(self, key, col):
        """Return the value at the specified key/column."""
        pass

    def get_key(self, key):
        """Returns a sorted list of column/value tuples."""
        pass

    def get_keys(self):
        """Returns a set containing all of the keys in the store."""
        pass

    def delete(self, key, col):
        """Removes a column/value from the given key."""
        pass

    def delete_key(self, key):
        """Removes all data associated with the given key."""
        pass
