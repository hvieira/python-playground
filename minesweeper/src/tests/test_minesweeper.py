from app.minesweeper import MineSweeperCell, MineSweeperBoard

from unittest.mock import patch
import pytest


class TestMineSweeperBoard:
    
    @patch("random.sample")
    def test_creation_adds_mines_according_to_cell_index_sample(self, mock_sample):
        board_size = 3
        
        mock_sample.return_value = [0]
        board = MineSweeperBoard.create(board_size, 1)

        assert board == MineSweeperBoard(size=board_size, cells={
            0: {
                0: MineSweeperCell(x=0, y=0, mined=True, revealed=False, num_adjancent_mines=0),
                1: MineSweeperCell(x=0, y=1, mined=False, revealed=False, num_adjancent_mines=1),
                2: MineSweeperCell(x=0, y=2, mined=False, revealed=False, num_adjancent_mines=0),
            },
            1: {
                0: MineSweeperCell(x=1, y=0, mined=False, revealed=False, num_adjancent_mines=1),
                1: MineSweeperCell(x=1, y=1, mined=False, revealed=False, num_adjancent_mines=1),
                2: MineSweeperCell(x=1, y=2, mined=False, revealed=False, num_adjancent_mines=0),
            },
            2:{
                0: MineSweeperCell(x=2, y=0, mined=False, revealed=False, num_adjancent_mines=0),
                1: MineSweeperCell(x=2, y=1, mined=False, revealed=False, num_adjancent_mines=0),
                2: MineSweeperCell(x=2, y=2, mined=False, revealed=False, num_adjancent_mines=0),
            }
        })

        mock_sample.assert_called_once_with([0, 1, 2, 3, 4, 5, 6, 7, 8], 1)

    @patch("random.sample")
    def test_creation_several_mines(self, mock_sample):
        board_size = 3
        
        mock_sample.return_value = [1, 3, 8]
        board = MineSweeperBoard.create(board_size, 3)

        assert board == MineSweeperBoard(size=board_size, cells={
            0: {
                0: MineSweeperCell(x=0, y=0, mined=False, revealed=False, num_adjancent_mines=2),
                1: MineSweeperCell(x=0, y=1, mined=True, revealed=False, num_adjancent_mines=1),
                2: MineSweeperCell(x=0, y=2, mined=False, revealed=False, num_adjancent_mines=1),
            },
            1: {
                0: MineSweeperCell(x=1, y=0, mined=True, revealed=False, num_adjancent_mines=1),
                1: MineSweeperCell(x=1, y=1, mined=False, revealed=False, num_adjancent_mines=3),
                2: MineSweeperCell(x=1, y=2, mined=False, revealed=False, num_adjancent_mines=2),
            },
            2:{
                0: MineSweeperCell(x=2, y=0, mined=False, revealed=False, num_adjancent_mines=1),
                1: MineSweeperCell(x=2, y=1, mined=False, revealed=False, num_adjancent_mines=2),
                2: MineSweeperCell(x=2, y=2, mined=True, revealed=False, num_adjancent_mines=0),
            }
        })

        mock_sample.assert_called_once_with([0, 1, 2, 3, 4, 5, 6, 7, 8], 3)

    @patch("random.sample")
    def test_on_reveal_reveal_the_picked_cell_if_there_are_adjancent_mines_and_nothing_else(self, mock_sample):
        board_size = 3
        
        mock_sample.return_value = [0]
        board = MineSweeperBoard.create(board_size, 1)
        board.reveal(x=0, y=1)

        assert board == MineSweeperBoard(size=board_size, cells={
            0: {
                0: MineSweeperCell(x=0, y=0, mined=True, revealed=False, num_adjancent_mines=0),
                1: MineSweeperCell(x=0, y=1, mined=False, revealed=True, num_adjancent_mines=1),
                2: MineSweeperCell(x=0, y=2, mined=False, revealed=False, num_adjancent_mines=0),
            },
            1: {
                0: MineSweeperCell(x=1, y=0, mined=False, revealed=False, num_adjancent_mines=1),
                1: MineSweeperCell(x=1, y=1, mined=False, revealed=False, num_adjancent_mines=1),
                2: MineSweeperCell(x=1, y=2, mined=False, revealed=False, num_adjancent_mines=0),
            },
            2:{
                0: MineSweeperCell(x=2, y=0, mined=False, revealed=False, num_adjancent_mines=0),
                1: MineSweeperCell(x=2, y=1, mined=False, revealed=False, num_adjancent_mines=0),
                2: MineSweeperCell(x=2, y=2, mined=False, revealed=False, num_adjancent_mines=0),
            }
        })


    @patch("random.sample")
    def test_on_reveal_reveal_neighbour_cells_with_no_adjancent_mines(self, mock_sample):
        board_size = 3
        
        mock_sample.return_value = [0]
        board = MineSweeperBoard.create(board_size, 1)
        board.reveal(x=2, y=2)

        assert board == MineSweeperBoard(size=board_size, cells={
            0: {
                0: MineSweeperCell(x=0, y=0, mined=True, revealed=False, num_adjancent_mines=0),
                1: MineSweeperCell(x=0, y=1, mined=False, revealed=False, num_adjancent_mines=1),
                2: MineSweeperCell(x=0, y=2, mined=False, revealed=True, num_adjancent_mines=0),
            },
            1: {
                0: MineSweeperCell(x=1, y=0, mined=False, revealed=False, num_adjancent_mines=1),
                1: MineSweeperCell(x=1, y=1, mined=False, revealed=False, num_adjancent_mines=1),
                2: MineSweeperCell(x=1, y=2, mined=False, revealed=True, num_adjancent_mines=0),
            },
            2:{
                0: MineSweeperCell(x=2, y=0, mined=False, revealed=True, num_adjancent_mines=0),
                1: MineSweeperCell(x=2, y=1, mined=False, revealed=True, num_adjancent_mines=0),
                2: MineSweeperCell(x=2, y=2, mined=False, revealed=True, num_adjancent_mines=0),
            }
        })

    @patch("random.sample")
    def test_on_reveal_reveal_neighbour_cells_with_no_adjancent_mines_other_scenario_1(self, mock_sample):
        board_size = 3
        
        mock_sample.return_value = [0, 3]
        board = MineSweeperBoard.create(board_size, 2)
        board.reveal(x=2, y=2)

        assert board == MineSweeperBoard(size=board_size, cells={
            0: {
                0: MineSweeperCell(x=0, y=0, mined=True, revealed=False, num_adjancent_mines=1),
                1: MineSweeperCell(x=0, y=1, mined=False, revealed=False, num_adjancent_mines=2),
                2: MineSweeperCell(x=0, y=2, mined=False, revealed=True, num_adjancent_mines=0),
            },
            1: {
                0: MineSweeperCell(x=1, y=0, mined=True, revealed=False, num_adjancent_mines=1),
                1: MineSweeperCell(x=1, y=1, mined=False, revealed=False, num_adjancent_mines=2),
                2: MineSweeperCell(x=1, y=2, mined=False, revealed=True, num_adjancent_mines=0),
            },
            2:{
                0: MineSweeperCell(x=2, y=0, mined=False, revealed=False, num_adjancent_mines=1),
                1: MineSweeperCell(x=2, y=1, mined=False, revealed=False, num_adjancent_mines=1),
                2: MineSweeperCell(x=2, y=2, mined=False, revealed=True, num_adjancent_mines=0),
            }
        })