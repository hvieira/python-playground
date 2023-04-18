from functools import reduce

def merge_sort_iterative(l):
    list_size = len(l)
    if list_size <= 1:
        return l
    else:
        mid_point = int(list_size/2)
        left = merge_sort_iterative(l[:mid_point])
        right = merge_sort_iterative(l[mid_point:])

        return _sort_and_merge_iterative(left,right)


def _sort_and_merge_iterative(left, right):
    result = []
    li = 0
    ri = 0
    tuple = (left[li], right[ri])
    while tuple != (None, None):
        l, r = tuple

        if r is None:
            result.append(l)
            li += 1
        elif l is None:
            result.append(r)
            ri += 1
        elif l <= r:
            result.append(l)
            li += 1
        else:
            result.append(r)
            ri += 1
            
        tuple = (left[li] if li < len(left) else None, right[ri] if ri < len(right) else None)

    return result


def merge_sort_recursive(l):
    list_size = len(l)
    if list_size <= 1:
        return l
    else:
        mid_point = int(list_size/2)
        left = merge_sort_iterative(l[:mid_point])
        right = merge_sort_iterative(l[mid_point:])

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
