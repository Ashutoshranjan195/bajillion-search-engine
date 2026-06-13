"""
File: common_elements.py
------------------------
CS106A Assignment 6: Bajillion Search Engine

This module provides a utility function to find
common elements between two lists. Used by the
search engine to intersect result sets when
performing Boolean AND queries.
"""


def common(list1, list2):
    """
    Returns a new list containing the unique elements
    that appear in BOTH list1 and list2.

    The returned list contains no duplicates, and the
    order follows the order of first appearance in list1.

    Parameters:
        list1 (list): The first list of elements.
        list2 (list): The second list of elements.

    Returns:
        list: A new list of elements present in both inputs.

    >>> common(['a', 'b', 'c'], ['b', 'c', 'd'])
    ['b', 'c']
    >>> common([1, 2, 2, 3], [2, 2, 3, 4])
    [2, 3]
    >>> common(['x'], ['y'])
    []
    """
    result = []
    seen = set()  # Track elements already added to avoid duplicates

    for element in list1:
        # Add element if it exists in list2 and hasn't been added yet
        if element in list2 and element not in seen:
            result.append(element)
            seen.add(element)

    return result
