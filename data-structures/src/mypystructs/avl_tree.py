from __future__ import annotations
from itertools import chain
from collections.abc import Collection
from dataclasses import dataclass, field
from typing import Optional, Iterator


@dataclass
class AVLTree(Collection[int]):
    root: Optional[AVLTreeNode] = None

    def __len__(self) -> int:
        if self.root is None:
            return 0
        else:
            return len(self.root)

    def __iter__(self) -> Iterator:
        if self.root is None:
            return iter([])
        else:
            return iter(self.root)

    def __contains__(self, item: object) -> bool:
        if self.root is None:
            return False
        else:
            return item in self.root

    def add(self, item):
        if self.root is None:
            self.root = AVLTreeNode(value=item)
        else:
            self.root.add(item)

    def remove(self, item):
        if self.root is not None:
            if self.root.left is None and self.root.right is None and self.root.value == item:
                self.root = None
            else:
                self.root.remove(item)


@dataclass
class AVLTreeNode(Collection[int]):
    value: int
    left: Optional[AVLTreeNode] = None
    right: Optional[AVLTreeNode] = None

    def __len__(self) -> int:
        print("asking for size")
        size = 1
        if self.left is not None:
            size += len(self.left)

        if self.right is not None:
            size += len(self.right)

        print(f"returning {size}")
        return size

    def __iter__(self) -> Iterator:
        if self.left is None:
            left_iter = iter([])
        else:
            left_iter = iter(self.left)

        if self.right is None:
            right_iter = iter([])
        else:
            right_iter = iter(self.right)

        return chain(left_iter, [self.value], right_iter)

    def __contains__(self, item: object) -> bool:
        if item == self.value:
            return True
        elif self.left is not None and item < self.value:
            return item in self.left
        elif self.right is not None and item > self.value:
            return item in self.right
        else:
            return False

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
        if self.value == item:  # item is already on the tree
            pass
        elif item > self.value:
            self._add_to_right(item)
        else:
            self._add_to_left(item)

        self._rebalance_if_necessary()

    def _add_to_right(self, item):
        if self.right is None:
            self.right = AVLTreeNode(value=item)
        else:
            self.right.add(item)

    def _add_to_left(self, item):
        if self.left is None:
            self.left = AVLTreeNode(value=item)
            self.left._parent = self
        else:
            self.left.add(item)

    def _rebalance_if_necessary(self):
        balance_factor = self._compute_balance_factor()

        if balance_factor > 1:  # tree is unbalanced on the left

            # check if left subtree is right heavy
            if self.left._compute_balance_factor() < 0:
                self._double_left_right_rotate()
            else:
                self._single_rotate_right()

        elif balance_factor < -1:  # tree is unbalanced on the right

            if self.right._compute_balance_factor() > 0:
                self._double_right_left_rotate()
            else:
                self._single_rotate_left()

        else:  # this tree is balanced
            pass

    def _compute_balance_factor(self):
        hl = 0 if self.left is None else self.left.height()
        hr = 0 if self.right is None else self.right.height()
        return hl - hr

    def _single_rotate_left(self):
        new_node = AVLTreeNode(
            value=self.right.value,
            left=AVLTreeNode(
                value=self.value,
                left=self.left,
                right=self.right.left
            ),
            right=self.right.right
        )

        self.value = new_node.value
        self.left = new_node.left
        self.right = new_node.right

    def _single_rotate_right(self):
        new_node = AVLTreeNode(
            value=self.left.value,
            left=self.left.left,
            right=AVLTreeNode(
                value=self.value,
                left=self.left.right,
                right=self.right
            )
        )

        self.value = new_node.value
        self.left = new_node.left
        self.right = new_node.right

    def _double_right_left_rotate(self):
        self.right._single_rotate_right()
        self._single_rotate_left()

    def _double_left_right_rotate(self):
        self.left._single_rotate_left()
        self._single_rotate_right()

    def remove(self, item, parent=None):
        if item == self.value:

            if self.left is not None: # the node to be deleted has a left subtree
                highest_value_node, highest_parent = AVLTreeNode.find_highest_value(self.left, parent=self)

                # the highest node on a left subtree does not have a right subtree, so just rewire parent
                if highest_parent.right is highest_value_node:
                    highest_parent.right = highest_value_node.left
                else:
                    highest_parent.left = highest_value_node.left

                self.value = highest_value_node.value

            elif self.right is not None:  # the node to be deleted does not have a left subtree

                self.value = self.right.value
                self.left = self.right.left
                self.right = self.right.right

            else:  # node to be deleted is a leaf
                AVLTreeNode.delete_node(parent, self)

            self._rebalance_if_necessary()

        elif item < self.value and self.left is not None:
            self.left.remove(item, parent=self)
        elif item > self.value and self.right is not None:
            self.right.remove(item, parent=self)

    @classmethod
    def delete_node(cls, parent: AVLTreeNode, node_to_delete: AVLTreeNode):
        if parent is not None and parent.left is node_to_delete:
            parent.left = None

        elif parent is not None and parent.right is node_to_delete:
            parent.right = None

    @classmethod
    def find_highest_value(cls, node, parent=None) -> tuple[AVLTreeNode, AVLTreeNode]:
        """
        Finds the highest value on the given tree. Guaranteed to not have a right subtree
        :param node: the tree to search
        :param parent: cursor for the parent of the node
        :return: a tuple composed of the highest value node (that has no right subtree) and the parent node
        """
        if node.right is None:
            return node, parent
        else:
            return AVLTreeNode.find_highest_value(node.right, parent=node)


