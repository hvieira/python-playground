

class MyBinaryTree:

    def __init__(self, value, left, right):
        self._value = value
        self._left = left
        self._right = right

    def sum(self):
        total = self._value

        if self._left is not None:
            total += self._left.sum()

        if self._right is not None:
            total += self._right.sum()

        return total


class Leaf(MyBinaryTree):
    def __init__(self, value):
        super().__init__(value, None, None)

    def sum(self):
        return self._value


bt = MyBinaryTree(
    value=0,
    left=MyBinaryTree(1, None, None),
    right=Leaf(3)
)

print(bt.sum())