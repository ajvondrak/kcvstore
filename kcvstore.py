import os
import pickle
from blist import sorteddict
from tempfile import NamedTemporaryFile


# I've made the executive decision that the 3rd party blist module is within
# the spirit of this coding challenge.  To understand why, I'll compare the
# following code to commit a81ea9, which included a small bit of extra code to
# handle "a world without blist".  We'll see that it's largely the same as what
# I have now.  (Except that blist is a tad more efficient.)
#
# The basic design I had for the KeyColumnValueStore noticed that the only
# particular requirement separating it from a plain nested hash table was the
# get_key method, which returns a list of columns in sorted order.  To this
# end, I only needed to track two things:
#
# * a nested hash table (Python dictionaries) for all the data, obviously
#
# * the order of columns associated with each key, using a hash table from keys
#   to a sorted sequence of columns (every time you insert a new column, you'd
#   have to "insort" into this sequence)
#
# The question is: what data structure do we use for the sorted sequence?  I
# didn't want the overhead of writing my own ordered tree, so the naive way to
# do this is with a regular Python list.  We can insort into a list using the
# bisect module, which is all well and good: there are only O(log n)
# comparisons to find where to insert into a list of size n.  But the actual
# *insertion* would still be O(n).  Python lists are dynamic arrays underneath,
# so insertion into the middle means we have to shift the indices of all the
# elements to the right of the insertion point.
#
# On the other hand, the instructions clearly said data structure libraries
# were OK.  Enter blist, with its sortedset class.  It handles the ordered tree
# structure for me, with the properly logarithmic insertion methods and so on.
# The code is just as simple as if I'd used regular Python lists with the
# bisect module (it's just more efficient with blist).  So, I think using blist
# is in the spirit of the problem here.
#
# However, this "dictionary + sorted set of keys" bookkeeping turns out to be a
# problem so easy to solve (if you already have a sorted set) that the blist
# module already *has* a sorteddict class.  Since I'm using blist anyway, why
# not make the tiny conceptual leap to just represent the KeyColumnValueStore
# as a dict from keys to sorteddicts?  While it makes the code fairly trivial
# to implement, it's not really any more "trivial" than the blist-based code
# from before would've been.  In my mind, the "dict + sorted set" approach
# would be OK (as I said above).  Though the sorteddict class just "solves the
# problem for me" (in one view), it's not without thought: it's basically a
# shorter way to do what I already would've done.
#
# This shortness is, of course, thoroughly negated by my long-winded comment.


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

    def __init__(self, path=None):
        self.kcv = {}
        self._create_log_file(path)

    # XXX Loads of issues with this naive persistence strategy.  I won't be
    # fixing them.

    def _create_log_file(self, path):
        if path is None:
            with NamedTemporaryFile(delete=False) as tmp:
                self.path = tmp.name
        else:
            self.path = os.path.expandvars(os.path.expanduser(path))
        if os.path.isfile(self.path) and os.stat(self.path).st_size:
            self._load()
        else:
            self._persist()  # will create the file if it doesn't exist

    def _load(self):
        """Reads the existing key/column/value structure from disk."""
        with open(self.path, 'r') as log:
            self.kcv = pickle.load(log)

    def _persist(self):
        """Persists the current key/column/value structure to disk."""
        with open(self.path, 'w') as log:
            pickle.dump(self.kcv, log)

    def set(self, key, col, val):
        """Sets the value at the given key/column.

        In the average case, requires O(log(c)**2) operations, where c is the
        number of columns associated with the key."""
        assert all(isinstance(datum, str) for datum in (key, col, val))
        self.kcv.setdefault(key, sorteddict())[col] = val
        self._persist()

    def get(self, key, col):
        """Return the value at the specified key/column, or None if no such
        value exists.

        In the average case, requires O(1) operations."""
        cv = self.kcv.get(key)
        return None if cv is None else cv.get(col)

    def get_key(self, key):
        """Returns a sorted list of column/value tuples.

        Requires O(c) operations, where c is the number of columns associated
        with the key."""
        return list(self.kcv.get(key, sorteddict()).items())

    def get_keys(self):
        """Returns a set containing all of the keys in the store.

        Requires O(k) operations, where k is the number of keys stored."""
        # It'd be easy to make this O(1) by having an extra slot, self.keys =
        # set(), that we add to & remove from in methods like self.set and
        # self.delete_key.  However, just returning self.keys would present a
        # mutable structure to the outside, which is asking for trouble, and
        # copying the value would be O(k) anyway (I think).  So, this
        # implementation does just as well.
        return set(self.kcv.iterkeys())

    def delete(self, key, col):
        """Removes a column/value from the given key.

        In the average case, requires O(log(c)) operations, where c is the
        number of columns associated with the key."""
        if key in self.kcv and col in self.kcv[key]:
            del self.kcv[key][col]
            self._persist()

    def delete_key(self, key):
        """Removes all data associated with the given key.

        In the average case, requires O(1) operations."""
        if key in self.kcv:
            del self.kcv[key]
            self._persist()

    def get_slice(self, key, start, stop):
        """Returns a sorted list of column/value tuples where the column values
        are between the start and stop values, inclusive of the start and stop
        values.  Start and/or stop can be None values, leaving the slice open
        ended in that direction.

        In the average case, requires O(log(c)**2 + s) operations, where c is
        the number of columns associated with the key and s is the length of
        the slice.  Thus, for large slices, this approaches O(c)."""
        # sorteddict.keys()  - O(1), returns sortedset in Python 2
        # x not in sortedset - O(log(c)**2)
        # len(sortedset)     - O(1)
        # sortedset.bisect_* - O(log(c)**2)
        # sortedset[i:j]     - O(log(c))
        # self.get           - O(1)
        # list comprehension - O(s), since O(1) self.get for each slice item
        cols = self.kcv.get(key, sorteddict()).keys()
        start_missing = start not in cols
        stop_missing = stop not in cols
        if start_missing and stop_missing and not (start is stop is None):
            return []
        start_index = 0 if start_missing else cols.bisect_left(start)
        stop_index = len(cols) if stop_missing else cols.bisect_right(stop)
        return [(c, self.get(key, c)) for c in cols[start_index:stop_index]]
