from __future__ import annotations
from itertools import chain
from collections.abc import Collection
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class BinaryTree(Collection):
    value: int
    left: Optional[BinaryTree] = None
    right: Optional[BinaryTree] = None

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

    def __contains__(self, item) -> bool:
        if item == self.value:
            return True
        elif self.left is not None and item in self.left:
            return True
        elif self.right is not None and item in self.right:
            return True
        else:
            return False

    def add(self, item: int):
        if self.value == item:
            pass
        elif item > self.value:
            if self.right is None:
                self.right = BinaryTree(item)
            else:
                self.right.add(item)
        else:
            if self.left is None:
                self.left = BinaryTree(item)
            else:
                self.left.add(item)
