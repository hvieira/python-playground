from mypystructs.binarytree import BinaryTree

import pytest


def balanced_tree():
    return BinaryTree(
        value=5,
        left=BinaryTree(
            value=2,
            left=BinaryTree(1, None, None),
            right=BinaryTree(
                value=3,
                left=None,
                right=BinaryTree(4, None, None)),
        ),
        right=BinaryTree(
            value=7,
            left=BinaryTree(6, None, None),
            right=BinaryTree(8, None, None),
        )
    )


class TestBinaryTree:

    @pytest.mark.parametrize(
        "tree, element_in_not_tree",
        list(map(lambda num: (balanced_tree(), num), [-1, -2, 0, 10, 1000, -1000]))
    )
    def test_contains_false(self, tree, element_in_not_tree):
        assert element_in_not_tree not in tree

    @pytest.mark.parametrize(
        "tree, element_in_tree",
        list(map(lambda num: (balanced_tree(), num), range(1, 8 + 1)))
    )
    def test_contains_true(self, tree, element_in_tree):
        assert element_in_tree in tree

    @pytest.mark.parametrize(
        "tree, expected_size",
        [
            (BinaryTree(0, None, None), 1),
            (BinaryTree(
                value=0,
                left=BinaryTree(1, None, None),
                right=BinaryTree(3, None, None)
            ), 3),
            (BinaryTree(
                value=5,
                left=BinaryTree(
                    value=2,
                    left=BinaryTree(1, None, None),
                    right=BinaryTree(3, None, None),
                ),
                right=BinaryTree(10, None, None)
            ), 5),
            (BinaryTree(
                value=1,
                left=BinaryTree(0, None, None),
                right=BinaryTree(
                    value=3,
                    left=BinaryTree(2, None, None),
                    right=BinaryTree(4, None, None),
                )
            ), 5),
            (balanced_tree(), 8)
        ]
    )
    def test_tree_size(self, tree, expected_size):
        assert len(tree) == expected_size

    def test_iterator(self):
        expected_order = list(range(1, 8 + 1))
        gotten_elements = []
        for element in balanced_tree():
            gotten_elements.append(element)

        assert gotten_elements == expected_order

    @pytest.mark.parametrize(
        "initial_tree, item, expected_tree",
        [
            (
                    BinaryTree(10),
                    9,
                    BinaryTree(
                        value=10,
                        left=BinaryTree(9)
                    )
            ),
            (
                    BinaryTree(10),
                    11,
                    BinaryTree(
                        value=10,
                        right=BinaryTree(11)
                    )
            ),
            (
                    BinaryTree(
                        value=10,
                        left=BinaryTree(9),
                        right=BinaryTree(11)
                    ),
                    1,
                    BinaryTree(
                        value=10,
                        left=BinaryTree(
                            value=9,
                            left=BinaryTree(1)
                        ),
                        right=BinaryTree(11)
                    )
            ),
            (
                    BinaryTree(
                        value=10,
                        left=BinaryTree(9),
                        right=BinaryTree(11)
                    ),
                    20,
                    BinaryTree(
                        value=10,
                        left=BinaryTree(value=9),
                        right=BinaryTree(
                            value=11,
                            right=BinaryTree(20)
                        )
                    )
            ),
        ]
    )
    def test_add(self, initial_tree, item, expected_tree):
        initial_tree.add(item)
        assert initial_tree == expected_tree
