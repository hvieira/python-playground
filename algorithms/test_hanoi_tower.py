from hanoi_tower import HanoiTower, HanoiMove

def test_single_disk():
    assert HanoiTower([1]).moves_to_solve() == [
        HanoiMove(1,"A", "C")
    ]

def test_two_disk():
    assert HanoiTower([2, 1]).moves_to_solve() == [
        HanoiMove(1, "A", "B"),
        HanoiMove(2, "A", "C"),
        HanoiMove(1, "B", "C"),
    ]

def test_three_disk():
    assert HanoiTower([3, 2, 1]).moves_to_solve() == [
        HanoiMove(1, "A", "C"),
        HanoiMove(2, "A", "B"),
        HanoiMove(1, "C", "B"),
        HanoiMove(3, "A", "C"),
        HanoiMove(1, "B", "A"),
        HanoiMove(2, "B", "C"),
        HanoiMove(1, "A", "C"),
    ]

def test_four_disk():
    assert HanoiTower([4, 3, 2, 1]).moves_to_solve() == [
        HanoiMove(1, "A", "B"),
        HanoiMove(2, "A", "C"),
        HanoiMove(1, "B", "C"),
        HanoiMove(3, "A", "B"),
        HanoiMove(1, "C", "A"),
        HanoiMove(2, "C", "B"),
        HanoiMove(1, "A", "B"),
        HanoiMove(4, "A", "C"),
        HanoiMove(1, "B", "C"),
        HanoiMove(2, "B", "A"),
        HanoiMove(1, "C", "A"),
        HanoiMove(3, "B", "C"),
        HanoiMove(1, "A", "B"),
        HanoiMove(2, "A", "C"),
        HanoiMove(1, "B", "C"),
    ]
