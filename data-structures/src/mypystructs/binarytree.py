class BinaryTree:

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
