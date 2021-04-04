from __future__ import annotations
from itertools import chain
from collections.abc import Collection
from dataclasses import dataclass, field
from typing import Optional

import math


@dataclass
class BinaryTree(Collection):
    value: int
    left: Optional[BinaryTree] = None
    right: Optional[BinaryTree] = None

    _balance_factor: int = field(default=0, init=False, repr=True, compare=False)

    @classmethod
    def new(cls, value) -> BinaryTree:
        return BinaryTree(value)

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

        self.re_balance_if_necessary()

    def remove(self, item: int):
        if item < self.value:
            if self.left is not None:
                if self.left.value == item:
                    self.left = None
                else:
                    self.left.remove(item)

        elif item > self.value:
            if self.right is not None:
                if self.right.value == item:
                    self.right = None
                else:
                    self.right.remove(item)
        else:
            pass

    def compute_balance_factors(self):
        hl = 0 if self.left is None else self.left.height()
        hr = 0 if self.right is None else self.right.height()
        self._balance_factor = hl - hr

    def re_balance_if_necessary(self):
        self.compute_balance_factors()

        if self._balance_factor > 1:  # tree is unbalanced on the left

            if self.left.right is not None:
                new_root = BinaryTree(
                    value=self.left.value,
                    left=self.left.left,
                    right=BinaryTree(
                        value=self.value,
                        left=self.left.right,
                        right=self.right
                    )
                )
            else:
                new_root = BinaryTree(
                    value=self.left.value,
                    left=self.left.left,
                    right=BinaryTree(self.value)
                )

            self.value = new_root.value
            self.left = new_root.left
            self.right = new_root.right

            self.compute_balance_factors()

        elif self._balance_factor < -1:  # tree is unbalanced on the right

            if self.right.left is not None:
                new_root = BinaryTree(
                    value=self.right.value,
                    left=BinaryTree(
                        value=self.value,
                        left=self.left,
                        right=self.right.left
                    ),
                    right=self.right.right
                )
            else:
                new_root = BinaryTree(
                    value=self.right.value,
                    left=BinaryTree(
                        value=self.value,
                        left=self.left,
                        right=None),
                    right=self.right.right
                )

            self.value = new_root.value
            self.left = new_root.left
            self.right = new_root.right

            self.compute_balance_factors()

        else:  # this tree is balanced
            pass


