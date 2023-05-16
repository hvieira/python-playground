from functools import reduce

def merge_sort_iterative(l, comparator):
    list_size = len(l)
    if list_size <= 1:
        return l
    else:
        mid_point = int(list_size/2)
        left = merge_sort_iterative(l[:mid_point], comparator)
        right = merge_sort_iterative(l[mid_point:], comparator)

        return _sort_and_merge_iterative(left,right, comparator)


def _sort_and_merge_iterative(left, right, comparator):
    result = []
    li = 0
    ri = 0
    expected_len = len(left) + len(right)

    while len(result) < expected_len:
        l, r = left[li], right[ri]

        if comparator(l, r) <= 0:
            result.append(l)
            li += 1
            # handle iteration where we have exhausted all left elements. Given that the last left is still "less" than the next right, just get all the remainder right
            if li >= len(left):
                result += right[ri:]
        else:
            result.append(r)
            ri += 1
            # handle iteration where we have exhausted all right elements. Given that the last right is still "less" than the next left, just get all the remainder left
            if ri >= len(right):
                result += left[li:]

    return result


def merge_sort_recursive(l):
    list_size = len(l)
    if list_size <= 1:
        return l
    else:
        mid_point = int(list_size/2)
        left = merge_sort_recursive(l[:mid_point])
        right = merge_sort_recursive(l[mid_point:])

        return _sort_and_merge_recursive(left,right, [])

def _sort_and_merge_recursive(left, right, acc):
    if len(left) == 0:
        return acc + right
    elif len(right) == 0:
        return acc + left
    else:
        if left[0] <= right[0]:
            acc.append(left[0])
            return _sort_and_merge_recursive(left[1:], right, acc)
        else:
            acc.append(right[0])
            return _sort_and_merge_recursive(left, right[1:], acc)
