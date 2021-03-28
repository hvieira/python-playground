from itertools import chain
from collections.abc import Collection


class BinaryTree(Collection):

    def __init__(self, value, left, right):
        self._value = value
        self._left = left
        self._right = right

    def __len__(self):
        size = 1
        if self._left is not None:
            size += len(self._left)

        if self._right is not None:
            size += len(self._right)

        return size

    def __iter__(self):
        if self._left is None:
            left_iter = iter([])
        else:
            left_iter = iter(self._left)

        if self._right is None:
            right_iter = iter([])
        else:
            right_iter = iter(self._right)

        return chain(left_iter, [self._value], right_iter)

    # TODO this is a left depth first search and is not log(n) complexity as one would expect for a balanced binary
    #  tree. Add functionality to create a balanced tree and then fix this
    def __contains__(self, item):
        if item == self._value:
            return True
        elif self._left is not None and item in self._left:
            return True
        elif self._right is not None and item in self._right:
            return True
        else:
            return False

    def sum(self):
        total = self._value

        if self._left is not None:
            total += self._left.sum()

        if self._right is not None:
            total += self._right.sum()

        return total

    def height(self) -> int:
        lh = self._left.height() if self._left is not None else 0
        rh = self._right.height() if self._right is not None else 0

        return max(lh, rh) + 1

    # TODO having the height/level pre-computed would help this
    def __str__(self) -> str:
        return self.as_string(0)

    def as_string(self, level):
        level_str = "  " * level
        res = f"(v={self._value})"

        if self._left is not None:
            res += f"\n{level_str}|-L={self._left.as_string(level + 1)}"

        if self._right is not None:
            res += f"\n{level_str}|-R={self._right.as_string(level + 1)}"

        return res
