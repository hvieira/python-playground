import itertools

from mergesort import merge_sort_iterative, merge_sort_recursive

int_asc_comparator = lambda l,r: l - r
int_desc_comparator = lambda l,r: r - l

alphabetic_asc_order = lambda l,r: 0 if l <= r else 1

def test_mergesort_iterative_empty_list():
    assert merge_sort_iterative([], int_asc_comparator) == []

def test_mergesort_iterative_single_element_list():
    assert merge_sort_iterative([1], int_asc_comparator) == [1]
    assert merge_sort_iterative([3], int_asc_comparator) == [3]
    assert merge_sort_iterative([11], int_asc_comparator) == [11]
    assert merge_sort_iterative([77], int_asc_comparator) == [77]

def test_mergesort_iterative_two_element_list():
    expected = [1,2]
    for comb in itertools.permutations(expected):
        assert merge_sort_iterative(list(comb), int_asc_comparator) == expected
    
def test_mergesort_iterative_three_element_list():
    expected = [1,2,3]
    for comb in itertools.permutations(expected):
        assert merge_sort_iterative(list(comb), int_asc_comparator) == expected

def test_mergesort_iterative_four_element_list():
    expected = [1,2,3,4]
    for comb in itertools.permutations(expected):
        assert merge_sort_iterative(list(comb), int_asc_comparator) == expected

def test_mergesort_iterative_four_element_list_desc():
    expected = [4,3,2,1]
    for comb in itertools.permutations(expected):
        assert merge_sort_iterative(list(comb), int_desc_comparator) == expected


def test_mergesort_iterative_strings():
    assert merge_sort_iterative(["a", "b", "ab", "ba", "c"], alphabetic_asc_order) == ['a', 'ab', 'b', 'ba', 'c']


def test_mergesort_iterative_large_list():
    input = [0 for _ in range(0,10000)]
    assert merge_sort_iterative(input, int_asc_comparator) == input

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