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
        "tree, expected_height",
        [
            (BinaryTree(0, None, None), 1),
            (BinaryTree(
                value=0,
                left=BinaryTree(1, None, None),
                right=BinaryTree(3, None, None)
            ), 2),
            (BinaryTree(
                value=5,
                left=BinaryTree(
                    value=2,
                    left=BinaryTree(1, None, None),
                    right=BinaryTree(3, None, None),
                ),
                right=BinaryTree(10, None, None)
            ), 3),
            (BinaryTree(
                value=1,
                left=BinaryTree(0, None, None),
                right=BinaryTree(
                    value=3,
                    left=BinaryTree(2, None, None),
                    right=BinaryTree(4, None, None),
                )
            ), 3)
        ]
    )
    def test_height(self, tree, expected_height):
        assert tree.height() == expected_height

    @pytest.mark.parametrize(
        "tree, expected_str_repr",
        [
            (
                    BinaryTree(0, None, None),
                    """
                    (v=0)
                    """.strip()
            ),
            (
                    BinaryTree(
                        value=2,
                        left=BinaryTree(1, None, None),
                        right=BinaryTree(3, None, None)
                    ),
                    (
                            "(v=2)"
                            "\n|-L=(v=1)"
                            "\n|-R=(v=3)"
                    )
            ),
            (
                    BinaryTree(
                        value=5,
                        left=BinaryTree(
                            value=2,
                            left=BinaryTree(1, None, None),
                            right=BinaryTree(3, None, None),
                        ),
                        right=BinaryTree(10, None, None)
                    ),
                    (
                            "(v=5)"
                            "\n|-L=(v=2)"
                            "\n  |-L=(v=1)"
                            "\n  |-R=(v=3)"
                            "\n|-R=(v=10)"
                    )
            ),
            (
                    BinaryTree(
                        value=1,
                        left=BinaryTree(0, None, None),
                        right=BinaryTree(
                            value=3,
                            left=BinaryTree(2, None, None),
                            right=BinaryTree(4, None, None),
                        )
                    ),
                    (
                            "(v=1)"
                            "\n|-L=(v=0)"
                            "\n|-R=(v=3)"
                            "\n  |-L=(v=2)"
                            "\n  |-R=(v=4)"
                    )
            ),
            (
                    BinaryTree(
                        value=3,
                        left=BinaryTree(
                            value=1,
                            left=BinaryTree(0, None, None),
                            right=None),
                        right=BinaryTree(
                            value=5,
                            left=BinaryTree(4, None, None),
                            right=BinaryTree(6, None, None),
                        )
                    ),
                    (
                            "(v=3)"
                            "\n|-L=(v=1)"
                            "\n  |-L=(v=0)"
                            "\n|-R=(v=5)"
                            "\n  |-L=(v=4)"
                            "\n  |-R=(v=6)"
                    )
            )
        ]
    )
    def test_pretty_str_repr(self, tree, expected_str_repr):
        assert tree.as_pretty_string() == expected_str_repr

    def test_add_higher_values_keeps_tree_balanced(self):
        tree = BinaryTree.new(1)

        tree.add(1)
        assert tree == BinaryTree(1)

        tree.add(2)
        assert tree == BinaryTree(
            value=1,
            right=BinaryTree(2)
        )

        tree.add(3)
        assert tree == (
            BinaryTree(
                value=2,
                left=BinaryTree(1),
                right=BinaryTree(3)
            )
        )

        tree.add(4)
        assert tree == (
            BinaryTree(
                2,
                left=BinaryTree(1),
                right=BinaryTree(
                    value=3,
                    right=BinaryTree(4)
                )
            )
        )

        tree.add(5)
        assert tree == (
            BinaryTree(
                2,
                left=BinaryTree(1),
                right=BinaryTree(
                    value=4,
                    left=BinaryTree(3),
                    right=BinaryTree(5)
                )
            )
        )

        tree.add(6)
        assert tree == (
            BinaryTree(
                4,
                left=BinaryTree(
                    value=2,
                    left=BinaryTree(1),
                    right=BinaryTree(3)
                ),
                right=BinaryTree(
                    value=5,
                    right=BinaryTree(6)
                )
            )
        )

        tree.add(7)
        assert tree == (
            BinaryTree(
                4,
                left=BinaryTree(
                    value=2,
                    left=BinaryTree(1),
                    right=BinaryTree(3)
                ),
                right=BinaryTree(
                    value=6,
                    left=BinaryTree(5),
                    right=BinaryTree(7)
                )
            )
        )

        tree.add(8)
        assert tree == (
            BinaryTree(
                4,
                left=BinaryTree(
                    value=2,
                    left=BinaryTree(1),
                    right=BinaryTree(3)
                ),
                right=BinaryTree(
                    value=6,
                    left=BinaryTree(5),
                    right=BinaryTree(
                        value=7,
                        right=BinaryTree(8)
                    )
                )
            )
        )

        tree.add(9)
        assert tree == (
            BinaryTree(
                4,
                left=BinaryTree(
                    value=2,
                    left=BinaryTree(1),
                    right=BinaryTree(3)
                ),
                right=BinaryTree(
                    value=6,
                    left=BinaryTree(5),
                    right=BinaryTree(
                        value=8,
                        left=BinaryTree(7),
                        right=BinaryTree(9)
                    )
                )
            )
        )

        tree.add(10)
        assert tree == (
            BinaryTree(
                4,
                left=BinaryTree(
                    value=2,
                    left=BinaryTree(1),
                    right=BinaryTree(3)
                ),
                right=BinaryTree(
                    value=8,
                    left=BinaryTree(
                        value=6,
                        left=BinaryTree(5),
                        right=BinaryTree(7)
                    ),
                    right=BinaryTree(
                        value=9,
                        right=BinaryTree(10)
                    )
                )
            )
        )

        tree.add(11)
        assert tree == (
            BinaryTree(
                4,
                left=BinaryTree(
                    value=2,
                    left=BinaryTree(1),
                    right=BinaryTree(3)
                ),
                right=BinaryTree(
                    value=8,
                    left=BinaryTree(
                        value=6,
                        left=BinaryTree(5),
                        right=BinaryTree(7)
                    ),
                    right=BinaryTree(
                        value=10,
                        left=BinaryTree(9),
                        right=BinaryTree(11)
                    )
                )
            )
        )

        tree.add(12)
        assert tree == (
            BinaryTree(
                8,
                left=BinaryTree(
                    value=4,
                    left=BinaryTree(
                        value=2,
                        left=BinaryTree(1),
                        right=BinaryTree(3)
                    ),
                    right=BinaryTree(
                        value=6,
                        left=BinaryTree(5),
                        right=BinaryTree(7)
                    )
                ),
                right=BinaryTree(
                    value=10,
                    left=BinaryTree(9),
                    right=BinaryTree(
                        value=11,
                        right=BinaryTree(12)
                    )
                )
            )
        )

    def test_sum_single_branch(self):
        assert BinaryTree(
            value=0,
            left=BinaryTree(1, None, None),
            right=BinaryTree(3, None, None)
        ).sum() == 4

    def test_sum_left_depth(self):
        assert BinaryTree(
            value=5,
            left=BinaryTree(2,
                            left=BinaryTree(1, None, None),
                            right=BinaryTree(3, None, None),
                            ),
            right=BinaryTree(10, None, None)
        ).sum() == 21

    def test_sum_right_depth(self):
        assert BinaryTree(
            value=1,
            left=BinaryTree(0, None, None),
            right=BinaryTree(3,
                             left=BinaryTree(2, None, None),
                             right=BinaryTree(4, None, None),
                             )
        ).sum() == 10
