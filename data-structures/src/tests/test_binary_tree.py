from mypystructs.binarytree import BinaryTree


class TestBinaryTree:

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
