from __future__ import annotations
from itertools import chain
from collections.abc import Collection
from dataclasses import dataclass
from typing import Optional


@dataclass
class BinaryTree(Collection):

    value: int
    left: Optional[BinaryTree]
    right: Optional[BinaryTree]

    def __len__(self) -> int:
        size = 1
        if self.left is not None:
            size += len(self.left)

        if self.right is not None:
            size += len(self.right)

        return size

    def __iter__(self) -> iter:
        if self.left is None:
            left_iter = iter([])
        else:
            left_iter = iter(self.left)

        if self.right is None:
            right_iter = iter([])
        else:
            right_iter = iter(self.right)

        return chain(left_iter, [self.value], right_iter)

    # TODO this is a left depth first search and is not log(n) complexity as one would expect for a balanced binary
    #  tree. Add functionality to create a balanced tree and then fix this
    def __contains__(self, item) -> bool:
        if item == self.value:
            return True
        elif self.left is not None and item in self.left:
            return True
        elif self.right is not None and item in self.right:
            return True
        else:
            return False

    def sum(self) -> int:
        total = self.value

        if self.left is not None:
            total += self.left.sum()

        if self.right is not None:
            total += self.right.sum()

        return total

    def height(self) -> int:
        lh = self.left.height() if self.left is not None else 0
        rh = self.right.height() if self.right is not None else 0

        return max(lh, rh) + 1

    def as_pretty_string(self, level=0):
        level_str = "  " * level
        res = f"(v={self.value})"

        if self.left is not None:
            res += f"\n{level_str}|-L={self.left.as_pretty_string(level + 1)}"

        if self.right is not None:
            res += f"\n{level_str}|-R={self.right.as_pretty_string(level + 1)}"

        return res
