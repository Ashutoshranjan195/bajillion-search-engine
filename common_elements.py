"""
common_elements.py
===================
A small, self-contained utility module that provides the `common()`
helper function used by the Bajillion Search Engine to implement its
Boolean AND search.

CS106A note: this is written using only basic loops and lists (no set
operations), in the spirit of the course's "build it yourself"
philosophy, but is still O(n*m) clean and correct for the small inputs
this assignment uses.
"""


def common(list1, list2):
    """
    Return a new list containing every element that appears in BOTH
    list1 and list2, with duplicates removed, preserving the order in
    which the elements first appear in list1.

    >>> common(['a', 'b', 'c'], ['b', 'c', 'd'])
    ['b', 'c']
    >>> common(['a', 'b', 'a'], ['a', 'c'])
    ['a']
    >>> common(['a', 'b'], ['c', 'd'])
    []
    >>> common([], ['a', 'b'])
    []
    >>> common(['x', 'y', 'z'], ['x', 'y', 'z'])
    ['x', 'y', 'z']
    """
    result = []
    for item in list1:
        if item in list2 and item not in result:
            result.append(item)
    return result


if __name__ == "__main__":
    # Running this file directly executes the doctests above and
    # prints a verbose report -- a quick way to sanity-check the
    # helper in isolation.
    import doctest
    doctest.testmod(verbose=True)
