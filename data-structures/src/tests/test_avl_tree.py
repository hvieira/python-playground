import pytest

from typing import Iterable

from mypystructs.avl_tree import AVLTree, AVLTreeNode


def tree_from_values(items: Iterable[int]) -> AVLTree:
    tree = AVLTree()
    for item in items:
        tree.add(item)

    return tree


class TestAVLTree:

    @pytest.mark.parametrize(
        "tree, element_in_not_tree",
        list(map(lambda num: (tree_from_values([1]), num), [-1, -2, 0, 10, 1000, -1000]))
    )
    def test_contains_false(self, tree, element_in_not_tree):
        assert element_in_not_tree not in tree

    @pytest.mark.parametrize(
        "tree, element_in_tree",
        list(map(lambda num: (tree_from_values(range(1, 8 + 1)), num), range(1, 8 + 1)))
    )
    def test_contains_true(self, tree, element_in_tree):
        assert element_in_tree in tree

    @pytest.mark.parametrize(
        "tree, expected_size",
        [
            (AVLTree(), 0),
            (tree_from_values([-1]), 1),
            (tree_from_values([10, 30, 70]), 3),
            (tree_from_values([10, 20, 30, 50, 80]), 5),
        ]
    )
    def test_tree_size(self, tree, expected_size):
        assert len(tree) == expected_size

    def test_iterator(self):
        tree = tree_from_values(range(1, 8 + 1))
        expected_order = list(range(1, 8 + 1))
        gotten_elements = []
        for element in tree:
            gotten_elements.append(element)

        assert gotten_elements == expected_order

    def test_add_higher_values_keeps_tree_balanced_left_rotation(self):
        tree = AVLTree()

        tree.add(1)
        tree.add(2)
        tree.add(3)
        assert tree == AVLTree(
            root=AVLTreeNode(
                value=2,
                left=AVLTreeNode(value=1),
                right=AVLTreeNode(value=3)
            )
        )

        tree.add(4)
        tree.add(5)
        assert tree == AVLTree(
            root=AVLTreeNode(
                value=2,
                left=AVLTreeNode(1),
                right=AVLTreeNode(
                    value=4,
                    left=AVLTreeNode(3),
                    right=AVLTreeNode(5)
                )
            )
        )

        tree.add(6)
        assert tree == AVLTree(
            root=AVLTreeNode(
                value=4,
                left=AVLTreeNode(
                    value=2,
                    left=AVLTreeNode(1),
                    right=AVLTreeNode(3)
                ),
                right=AVLTreeNode(
                    value=5,
                    right=AVLTreeNode(6)
                )
            )
        )

    def test_add_left_leaf_on_right_subtree_keeps_tree_balanced(self):
        tree = tree_from_values([5, 1, 9, 7])
        assert tree == AVLTree(
            root=AVLTreeNode(
                value=5,
                left=AVLTreeNode(1),
                right=AVLTreeNode(
                    value=9,
                    left=AVLTreeNode(7)
                )
            )
        )

        tree.add(6)
        assert tree == AVLTree(
            root=AVLTreeNode(
                value=5,
                left=AVLTreeNode(1),
                right=AVLTreeNode(
                    value=7,
                    left=AVLTreeNode(6),
                    right=AVLTreeNode(9)
                )
            )
        )

    def test_add_left_leaf_on_left_subtree_keeps_tree_balanced(self):
        tree = AVLTree()

        tree.add(10)
        tree.add(9)
        tree.add(8)
        assert tree == AVLTree(
            root=AVLTreeNode(
                value=9,
                left=AVLTreeNode(value=8),
                right=AVLTreeNode(value=10)
            )
        )

        tree.add(7)
        tree.add(6)
        assert tree == AVLTree(
            root=AVLTreeNode(
                value=9,
                left=AVLTreeNode(
                    value=7,
                    left=AVLTreeNode(6),
                    right=AVLTreeNode(8)
                ),
                right=AVLTreeNode(value=10)
            )
        )

        tree.add(5)
        assert tree == AVLTree(
            root=AVLTreeNode(
                value=7,
                left=AVLTreeNode(
                    value=6,
                    left=AVLTreeNode(5)
                ),
                right=AVLTreeNode(
                    value=9,
                    left=AVLTreeNode(8),
                    right=AVLTreeNode(10)
                )
            )
        )

    @pytest.mark.parametrize(
        "initial_tree, item_to_add, expected_tree",
        [
            (
                AVLTree(
                    root=AVLTreeNode(
                        value=5,
                        right=AVLTreeNode(
                            value=8
                        )
                    )
                ),
                6,
                AVLTree(
                    root=AVLTreeNode(
                        value=6,
                        left=AVLTreeNode(value=5),
                        right=AVLTreeNode(value=8)
                    )
                )
            )
        ]

    )
    def test_right_left_rotation(self, initial_tree, item_to_add, expected_tree):
        initial_tree.add(item_to_add)
        assert initial_tree == expected_tree

    @pytest.mark.parametrize(
        "initial_tree, item_to_add, expected_tree",
        [
            (
                    AVLTree(
                        root=AVLTreeNode(
                            value=8,
                            left=AVLTreeNode(
                                value=5
                            )
                        )
                    ),
                    6,
                    AVLTree(
                        root=AVLTreeNode(
                            value=6,
                            left=AVLTreeNode(value=5),
                            right=AVLTreeNode(value=8)
                        )
                    )
            )
        ]

    )
    def test_left_right_rotation(self, initial_tree, item_to_add, expected_tree):
        initial_tree.add(item_to_add)
        assert initial_tree == expected_tree

    @pytest.mark.parametrize(
        "initial_tree, item, expected_tree",
        [
            (
                    AVLTree(
                        root=AVLTreeNode(
                            value=1,
                            left=AVLTreeNode(0),
                            right=AVLTreeNode(2),
                        )
                    ),
                    2,
                    AVLTree(
                        AVLTreeNode(
                            value=1,
                            left=AVLTreeNode(0)
                        )
                    )
            ),
            (
                    AVLTree(
                        AVLTreeNode(
                            value=1,
                            left=AVLTreeNode(0),
                            right=AVLTreeNode(2),
                        )
                    ),
                    0,
                    AVLTree(
                        AVLTreeNode(
                            value=1,
                            right=AVLTreeNode(2)
                        )
                    )
            )
        ]
    )
    def test_remove_leaf_items(self, initial_tree, item, expected_tree):
        initial_tree.remove(item)
        assert initial_tree == expected_tree

    @pytest.mark.parametrize(
        "initial_tree, item, expected_tree",
        [
            (
                    tree_from_values([10, 20, 5, 3]),
                    5,
                    AVLTree(
                        root=AVLTreeNode(
                            value=10,
                            left=AVLTreeNode(3),
                            right=AVLTreeNode(20)
                        )
                    )
            ),
            (
                    AVLTree(
                        root=AVLTreeNode(
                            value=5,
                            left=AVLTreeNode(
                                value=1,
                                left=AVLTreeNode(
                                    value=-2,
                                    left=AVLTreeNode(-1),
                                    right=AVLTreeNode(0),
                                ),
                                right=AVLTreeNode(4)
                            ),
                            right=AVLTreeNode(
                                value=10,
                                right=AVLTreeNode(20)),
                        )
                    ),
                    1,
                    AVLTree(
                        root=AVLTreeNode(
                            value=5,
                            left=AVLTreeNode(
                                value=0,
                                left=AVLTreeNode(
                                    value=-2,
                                    left=AVLTreeNode(value=-1)
                                ),
                                right=AVLTreeNode(4)
                            ),
                            right=AVLTreeNode(
                                value=10,
                                right=AVLTreeNode(20)),
                        )
                    )
            ),
            (
                    AVLTree(
                        root=AVLTreeNode(
                            value=4,
                            left=AVLTreeNode(
                                value=3,
                                left=AVLTreeNode(value=2)
                            ),
                            right=AVLTreeNode(
                                value=9,
                                left=AVLTreeNode(
                                    value=7,
                                    left=AVLTreeNode(value=6)
                                ),
                                right=AVLTreeNode(
                                    value=11,
                                    left=AVLTreeNode(value=10)
                                )
                            ),
                        )
                    ),
                    9,
                    AVLTree(
                        root=AVLTreeNode(
                            value=4,
                            left=AVLTreeNode(
                                value=3,
                                left=AVLTreeNode(value=2)
                            ),
                            right=AVLTreeNode(
                                value=7,
                                left=AVLTreeNode(value=6),
                                right=AVLTreeNode(
                                    value=11,
                                    left=AVLTreeNode(value=10)
                                )
                            )
                        )
                    )
            ),
            (
                    AVLTree(
                        root=AVLTreeNode(
                            value=4,
                            left=AVLTreeNode(
                                value=3,
                                left=AVLTreeNode(value=2)
                            ),
                            right=AVLTreeNode(
                                value=9,
                                left=AVLTreeNode(value=7),
                                right=AVLTreeNode(
                                    value=11,
                                    left=AVLTreeNode(value=10)
                                )
                            ),
                        )
                    ),
                    9,
                    AVLTree(
                        root=AVLTreeNode(
                            value=4,
                            left=AVLTreeNode(
                                value=3,
                                left=AVLTreeNode(value=2)
                            ),
                            right=AVLTreeNode(
                                value=10,
                                left=AVLTreeNode(value=7),
                                right=AVLTreeNode(value=11)
                            )
                        )
                    )
            )
        ]
    )
    def test_remove_items_with_left_subtree(self, initial_tree, item, expected_tree):
        initial_tree.remove(item)
        assert initial_tree == expected_tree

    @pytest.mark.parametrize(
        "initial_tree, item, expected_tree",
        [
            (
                    AVLTree(
                        root=AVLTreeNode(
                            value=4,
                            left=AVLTreeNode(value=3),
                            right=AVLTreeNode(
                                value=6,
                                right=AVLTreeNode(value=9)),
                        )
                    ),
                    6,
                    AVLTree(
                        root=AVLTreeNode(
                            value=4,
                            left=AVLTreeNode(value=3),
                            right=AVLTreeNode(value=9),
                        )
                    )
            )
        ]
    )
    def test_remove_items_with_only_right_subtree(self, initial_tree, item, expected_tree):
        initial_tree.remove(item)
        assert initial_tree == expected_tree

    @pytest.mark.parametrize(
        "initial_tree, item, expected_tree",
        [
            (
                    AVLTree(
                        root=AVLTreeNode(
                            value=4,
                            left=None,
                            right=None
                        )
                    ),
                    4,
                    AVLTree(
                        root=None
                    )
            ),
            (
                    AVLTree(
                        root=AVLTreeNode(
                            value=4,
                            left=AVLTreeNode(value=3),
                            right=None
                        )
                    ),
                    4,
                    AVLTree(
                        root=AVLTreeNode(
                            value=3,
                            left=None,
                            right=None
                        )
                    )
            ),
            (
                    AVLTree(
                        root=AVLTreeNode(
                            value=4,
                            left=AVLTreeNode(value=3),
                            right=None
                        )
                    ),
                    4,
                    AVLTree(
                        root=AVLTreeNode(
                            value=3,
                            left=None,
                            right=None
                        )
                    )
            ),
            (
                    AVLTree(
                        root=AVLTreeNode(
                            value=4,
                            left=None,
                            right=AVLTreeNode(value=5)
                        )
                    ),
                    4,
                    AVLTree(
                        root=AVLTreeNode(
                            value=5,
                            left=None,
                            right=None
                        )
                    )
            ),
            (
                    AVLTree(
                        root=AVLTreeNode(
                            value=4,
                            left=AVLTreeNode(value=3),
                            right=AVLTreeNode(
                                value=6,
                                right=AVLTreeNode(value=9)),
                        )
                    ),
                    4,
                    AVLTree(
                        root=AVLTreeNode(
                            value=6,
                            left=AVLTreeNode(value=3),
                            right=AVLTreeNode(value=9),
                        )
                    )
            )
        ]
    )
    def test_remove_root_node(self, initial_tree, item, expected_tree):
        initial_tree.remove(item)
        assert initial_tree == expected_tree
