from blist import sorteddict
from collections import defaultdict


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

    def __init__(self):
        self.kcv = defaultdict(lambda: sorteddict())

    def set(self, key, col, val):
        """Sets the value at the given key/column.

        In the average case, requires O(log(c)**2) operations, where c is the
        number of columns associated with the key."""
        assert all(isinstance(datum, str) for datum in (key, col, val))
        self.kcv[key][col] = val

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
        return list(self.kcv[key].items())

    def get_keys(self):
        """Returns a set containing all of the keys in the store.

        Requires O(k) operations, where k is the number of keys stored."""
        # It'd be easy to make this O(1) by having an extra slot, self.keys =
        # set(), that we add to & remove from in methods like self.set and
        # self.delete_key.  However, just returning self.keys would present a
        # mutable structure to the outside, which is asking for trouble, and
        # copying the value would be O(k) anyway (I think).  So, this
        # implementation does just as well.
        return set(self.kcv.keys())

    def delete(self, key, col):
        """Removes a column/value from the given key.

        In the average case, requires O(log(c)) operations, where c is the
        number of columns associated with the key."""
        if key in self.kcv and col in self.kcv[key]:
            del self.kcv[key][col]

    def delete_key(self, key):
        """Removes all data associated with the given key.

        In the average case, requires O(1) operations."""
        if key in self.kcv:
            del self.kcv[key]
