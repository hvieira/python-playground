import itertools

from mergesort import merge_sort_iterative, merge_sort_recursive


def test_mergesort_iterative_empty_list():
    assert merge_sort_iterative([]) == []

def test_mergesort_iterative_single_element_list():
    assert merge_sort_iterative([1]) == [1]
    assert merge_sort_iterative([3]) == [3]
    assert merge_sort_iterative([11]) == [11]
    assert merge_sort_iterative([77]) == [77]

def test_mergesort_iterative_two_element_list():
    expected = [1,2]
    for comb in itertools.permutations(expected):
        assert merge_sort_iterative(list(comb)) == expected
    
def test_mergesort_iterative_three_element_list():
    expected = [1,2,3]
    for comb in itertools.permutations(expected):
        assert merge_sort_iterative(list(comb)) == expected

def test_mergesort_iterative_four_element_list():
    expected = [1,2,3,4]
    for comb in itertools.permutations(expected):
        assert merge_sort_iterative(list(comb)) == expected


def test_mergesort_iterative_large_list():
    input = [0 for _ in range(0,10000)]
    assert merge_sort_iterative(input) == input

# recursive 
def test_mergesort_recursive_empty_list():
    assert merge_sort_recursive([]) == []

def test_mergesort_recursive_single_element_list():
    assert merge_sort_recursive([1]) == [1]
    assert merge_sort_recursive([3]) == [3]
    assert merge_sort_recursive([11]) == [11]
    assert merge_sort_recursive([77]) == [77]

def test_mergesort_recursive_two_element_list():
    expected = [1,2]
    for comb in itertools.permutations(expected):
        assert merge_sort_recursive(list(comb)) == expected
    
def test_mergesort_recursive_three_element_list():
    expected = [1,2,3]
    for comb in itertools.permutations(expected):
        assert merge_sort_recursive(list(comb)) == expected

def test_mergesort_iterative_four_element_list():
    expected = [1,2,3,4]
    for comb in itertools.permutations(expected):
        assert merge_sort_recursive(list(comb)) == expected

# does not work with recursion out of the box in python and internet searches point to things like
# """
# No, and it never will since Guido van Rossum prefers to be able to have proper tracebacks:
# """
# there might be some workaround, like 
# https://dev.to/apoorvtyagi/tail-recursion-in-python-2og0
# https://www.geeksforgeeks.org/tail-recursion-in-python-without-introspection/
# http://baruchel.github.io/blog/python/2013/12/03/tail-recursion-in-python/ 

# def test_mergesort_recursive_large_list():
#     input = [0 for _ in range(0,10000)]
#     assert merge_sort_recursive(input) == input