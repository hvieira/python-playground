from app.minesweeper import MineSweeperCell, MineSweeperBoard, PickedMineException, UnsupportedMove, GameResult

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
                0: MineSweeperCell(x=0, y=0, mined=True, revealed=False, num_adjacent_mines=0),
                1: MineSweeperCell(x=0, y=1, mined=False, revealed=False, num_adjacent_mines=1),
                2: MineSweeperCell(x=0, y=2, mined=False, revealed=False, num_adjacent_mines=0),
            },
            1: {
                0: MineSweeperCell(x=1, y=0, mined=False, revealed=False, num_adjacent_mines=1),
                1: MineSweeperCell(x=1, y=1, mined=False, revealed=False, num_adjacent_mines=1),
                2: MineSweeperCell(x=1, y=2, mined=False, revealed=False, num_adjacent_mines=0),
            },
            2:{
                0: MineSweeperCell(x=2, y=0, mined=False, revealed=False, num_adjacent_mines=0),
                1: MineSweeperCell(x=2, y=1, mined=False, revealed=False, num_adjacent_mines=0),
                2: MineSweeperCell(x=2, y=2, mined=False, revealed=False, num_adjacent_mines=0),
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
                0: MineSweeperCell(x=0, y=0, mined=False, revealed=False, num_adjacent_mines=2),
                1: MineSweeperCell(x=0, y=1, mined=True, revealed=False, num_adjacent_mines=1),
                2: MineSweeperCell(x=0, y=2, mined=False, revealed=False, num_adjacent_mines=1),
            },
            1: {
                0: MineSweeperCell(x=1, y=0, mined=True, revealed=False, num_adjacent_mines=1),
                1: MineSweeperCell(x=1, y=1, mined=False, revealed=False, num_adjacent_mines=3),
                2: MineSweeperCell(x=1, y=2, mined=False, revealed=False, num_adjacent_mines=2),
            },
            2:{
                0: MineSweeperCell(x=2, y=0, mined=False, revealed=False, num_adjacent_mines=1),
                1: MineSweeperCell(x=2, y=1, mined=False, revealed=False, num_adjacent_mines=2),
                2: MineSweeperCell(x=2, y=2, mined=True, revealed=False, num_adjacent_mines=0),
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
                0: MineSweeperCell(x=0, y=0, mined=True, revealed=False, num_adjacent_mines=0),
                1: MineSweeperCell(x=0, y=1, mined=False, revealed=True, num_adjacent_mines=1),
                2: MineSweeperCell(x=0, y=2, mined=False, revealed=False, num_adjacent_mines=0),
            },
            1: {
                0: MineSweeperCell(x=1, y=0, mined=False, revealed=False, num_adjacent_mines=1),
                1: MineSweeperCell(x=1, y=1, mined=False, revealed=False, num_adjacent_mines=1),
                2: MineSweeperCell(x=1, y=2, mined=False, revealed=False, num_adjacent_mines=0),
            },
            2:{
                0: MineSweeperCell(x=2, y=0, mined=False, revealed=False, num_adjacent_mines=0),
                1: MineSweeperCell(x=2, y=1, mined=False, revealed=False, num_adjacent_mines=0),
                2: MineSweeperCell(x=2, y=2, mined=False, revealed=False, num_adjacent_mines=0),
            }
        })

    @patch("random.sample")
    def test_on_reveal_reveal_picked_cell_if_there_are_no_neighbour_cells_with_no_adjancent_mines(self, mock_sample):
        board_size = 3
        
        mock_sample.return_value = [1, 3]
        board = MineSweeperBoard.create(board_size, 2)
        board.reveal(x=2, y=2)

        assert board == MineSweeperBoard(size=board_size, cells={
            0: {
                0: MineSweeperCell(x=0, y=0, mined=False, revealed=False, num_adjacent_mines=2),
                1: MineSweeperCell(x=0, y=1, mined=True, revealed=False, num_adjacent_mines=1),
                2: MineSweeperCell(x=0, y=2, mined=False, revealed=False, num_adjacent_mines=1),
            },
            1: {
                0: MineSweeperCell(x=1, y=0, mined=True, revealed=False, num_adjacent_mines=1),
                1: MineSweeperCell(x=1, y=1, mined=False, revealed=False, num_adjacent_mines=2),
                2: MineSweeperCell(x=1, y=2, mined=False, revealed=False, num_adjacent_mines=1),
            },
            2:{
                0: MineSweeperCell(x=2, y=0, mined=False, revealed=False, num_adjacent_mines=1),
                1: MineSweeperCell(x=2, y=1, mined=False, revealed=False, num_adjacent_mines=1),
                2: MineSweeperCell(x=2, y=2, mined=False, revealed=True, num_adjacent_mines=0),
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
                0: MineSweeperCell(x=0, y=0, mined=True, revealed=False, num_adjacent_mines=0),
                1: MineSweeperCell(x=0, y=1, mined=False, revealed=False, num_adjacent_mines=1),
                2: MineSweeperCell(x=0, y=2, mined=False, revealed=True, num_adjacent_mines=0),
            },
            1: {
                0: MineSweeperCell(x=1, y=0, mined=False, revealed=False, num_adjacent_mines=1),
                1: MineSweeperCell(x=1, y=1, mined=False, revealed=False, num_adjacent_mines=1),
                2: MineSweeperCell(x=1, y=2, mined=False, revealed=True, num_adjacent_mines=0),
            },
            2:{
                0: MineSweeperCell(x=2, y=0, mined=False, revealed=True, num_adjacent_mines=0),
                1: MineSweeperCell(x=2, y=1, mined=False, revealed=True, num_adjacent_mines=0),
                2: MineSweeperCell(x=2, y=2, mined=False, revealed=True, num_adjacent_mines=0),
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
                0: MineSweeperCell(x=0, y=0, mined=True, revealed=False, num_adjacent_mines=1),
                1: MineSweeperCell(x=0, y=1, mined=False, revealed=False, num_adjacent_mines=2),
                2: MineSweeperCell(x=0, y=2, mined=False, revealed=True, num_adjacent_mines=0),
            },
            1: {
                0: MineSweeperCell(x=1, y=0, mined=True, revealed=False, num_adjacent_mines=1),
                1: MineSweeperCell(x=1, y=1, mined=False, revealed=False, num_adjacent_mines=2),
                2: MineSweeperCell(x=1, y=2, mined=False, revealed=True, num_adjacent_mines=0),
            },
            2:{
                0: MineSweeperCell(x=2, y=0, mined=False, revealed=False, num_adjacent_mines=1),
                1: MineSweeperCell(x=2, y=1, mined=False, revealed=False, num_adjacent_mines=1),
                2: MineSweeperCell(x=2, y=2, mined=False, revealed=True, num_adjacent_mines=0),
            }
        })

    @patch("random.sample")
    def test_on_reveal_if_mined_is_picked_throw_exception(self, mock_sample):
        board_size = 3
        
        mock_sample.return_value = [0]
        board = MineSweeperBoard.create(board_size, 1)
        
        with pytest.raises(PickedMineException):
            board.reveal(x=0, y=0)

        assert board == MineSweeperBoard(size=board_size, cells={
            0: {
                0: MineSweeperCell(x=0, y=0, mined=True, revealed=True, num_adjacent_mines=0),
                1: MineSweeperCell(x=0, y=1, mined=False, revealed=False, num_adjacent_mines=1),
                2: MineSweeperCell(x=0, y=2, mined=False, revealed=False, num_adjacent_mines=0),
            },
            1: {
                0: MineSweeperCell(x=1, y=0, mined=False, revealed=False, num_adjacent_mines=1),
                1: MineSweeperCell(x=1, y=1, mined=False, revealed=False, num_adjacent_mines=1),
                2: MineSweeperCell(x=1, y=2, mined=False, revealed=False, num_adjacent_mines=0),
            },
            2:{
                0: MineSweeperCell(x=2, y=0, mined=False, revealed=False, num_adjacent_mines=0),
                1: MineSweeperCell(x=2, y=1, mined=False, revealed=False, num_adjacent_mines=0),
                2: MineSweeperCell(x=2, y=2, mined=False, revealed=False, num_adjacent_mines=0),
            }
        })

    @patch("random.sample")
    def test_on_flag_update_cell_to_flagged(self, mock_sample):
        board_size = 3
        
        mock_sample.return_value = [0]
        board = MineSweeperBoard.create(board_size, 1)
        
        board.flag(x=1, y=1)

        assert board == MineSweeperBoard(size=board_size, cells={
            0: {
                0: MineSweeperCell(x=0, y=0, mined=True, revealed=False, num_adjacent_mines=0),
                1: MineSweeperCell(x=0, y=1, mined=False, revealed=False, num_adjacent_mines=1),
                2: MineSweeperCell(x=0, y=2, mined=False, revealed=False, num_adjacent_mines=0),
            },
            1: {
                0: MineSweeperCell(x=1, y=0, mined=False, revealed=False, num_adjacent_mines=1),
                1: MineSweeperCell(x=1, y=1, mined=False, revealed=False, flagged=True, num_adjacent_mines=1),
                2: MineSweeperCell(x=1, y=2, mined=False, revealed=False, num_adjacent_mines=0),
            },
            2:{
                0: MineSweeperCell(x=2, y=0, mined=False, revealed=False, num_adjacent_mines=0),
                1: MineSweeperCell(x=2, y=1, mined=False, revealed=False, num_adjacent_mines=0),
                2: MineSweeperCell(x=2, y=2, mined=False, revealed=False, num_adjacent_mines=0),
            }
        })

    @patch("random.sample")
    def test_flag_a_mined_cell(self, mock_sample):
        board_size = 3
        
        mock_sample.return_value = [0]
        board = MineSweeperBoard.create(board_size, 1)
        
        board.flag(x=0, y=0)

        assert board == MineSweeperBoard(size=board_size, cells={
            0: {
                0: MineSweeperCell(x=0, y=0, mined=True, revealed=False, flagged=True, num_adjacent_mines=0),
                1: MineSweeperCell(x=0, y=1, mined=False, revealed=False, num_adjacent_mines=1),
                2: MineSweeperCell(x=0, y=2, mined=False, revealed=False, num_adjacent_mines=0),
            },
            1: {
                0: MineSweeperCell(x=1, y=0, mined=False, revealed=False, num_adjacent_mines=1),
                1: MineSweeperCell(x=1, y=1, mined=False, revealed=False, num_adjacent_mines=1),
                2: MineSweeperCell(x=1, y=2, mined=False, revealed=False, num_adjacent_mines=0),
            },
            2:{
                0: MineSweeperCell(x=2, y=0, mined=False, revealed=False, num_adjacent_mines=0),
                1: MineSweeperCell(x=2, y=1, mined=False, revealed=False, num_adjacent_mines=0),
                2: MineSweeperCell(x=2, y=2, mined=False, revealed=False, num_adjacent_mines=0),
            }
        })

    def test_on_flag_a_revealed_cell_raise_error(self):
        board = MineSweeperBoard(size=1, cells={
            0: {
                0: MineSweeperCell(x=0, y=0, mined=False, revealed=True, num_adjacent_mines=0),
            }
        })
        
        with pytest.raises(UnsupportedMove):
            board.flag(x=0, y=0)

    def test_on_flag_a_flagged_cell_is_a_noop(self):
        board = MineSweeperBoard(size=1, cells={
            0: {
                0: MineSweeperCell(x=0, y=0, mined=False, revealed=False, flagged=True, num_adjacent_mines=0),
            }
        })
        
        assert board == MineSweeperBoard(size=1, cells={
            0: {
                0: MineSweeperCell(x=0, y=0, mined=False, revealed=False, flagged=True, num_adjacent_mines=0),
            }
        })

    def test_on_reveal_a_flagged_cell_is_an_unsupported_move(self):
        board = MineSweeperBoard(size=1, cells={
            0: {
                0: MineSweeperCell(x=0, y=0, mined=False, revealed=False, flagged=True, num_adjacent_mines=0),
            }
        })
        
        with pytest.raises(UnsupportedMove):
            board.reveal(0, 0)

        # assert state has not been changed
        assert board == MineSweeperBoard(size=1, cells={
            0: {
                0: MineSweeperCell(x=0, y=0, mined=False, revealed=False, flagged=True, num_adjacent_mines=0),
            }
        })

    def test_on_unflag_a_flagged_cell_unflag_the_cell(self):
        board = MineSweeperBoard(size=1, cells={
            0: {
                0: MineSweeperCell(x=0, y=0, mined=False, revealed=False, flagged=True, num_adjacent_mines=0),
            }
        })
        
        board.unflag(0, 0)

        assert board == MineSweeperBoard(size=1, cells={
            0: {
                0: MineSweeperCell(x=0, y=0, mined=False, revealed=False, flagged=False, num_adjacent_mines=0),
            }
        })

    def test_on_unflag_an_unflagged_cell_is_noop(self):
        board = MineSweeperBoard(size=1, cells={
            0: {
                0: MineSweeperCell(x=0, y=0, mined=False, revealed=False, flagged=False, num_adjacent_mines=0),
            }
        })
        
        board.unflag(0, 0)

        assert board == MineSweeperBoard(size=1, cells={
            0: {
                0: MineSweeperCell(x=0, y=0, mined=False, revealed=False, flagged=False, num_adjacent_mines=0),
            }
        })

    def test_on_unflag_a_revealed_cell_raise_error(self):
        board = MineSweeperBoard(size=1, cells={
            0: {
                0: MineSweeperCell(x=0, y=0, mined=False, revealed=True, flagged=False, num_adjacent_mines=0),
            }
        })
        
        with pytest.raises(UnsupportedMove):
            board.unflag(x=0, y=0)

    @patch("random.sample")
    def test_on_reveal_flagged_cells_are_not_revealed(self, mock_sample):
        board_size = 3
        
        mock_sample.return_value = [0]
        board = MineSweeperBoard.create(board_size, 1)

        board.flag(2,0)
        board.reveal(x=2, y=2)

        assert board == MineSweeperBoard(size=board_size, cells={
            0: {
                0: MineSweeperCell(x=0, y=0, mined=True, revealed=False, num_adjacent_mines=0),
                1: MineSweeperCell(x=0, y=1, mined=False, revealed=False, num_adjacent_mines=1),
                2: MineSweeperCell(x=0, y=2, mined=False, revealed=True, num_adjacent_mines=0),
            },
            1: {
                0: MineSweeperCell(x=1, y=0, mined=False, revealed=False, num_adjacent_mines=1),
                1: MineSweeperCell(x=1, y=1, mined=False, revealed=False, num_adjacent_mines=1),
                2: MineSweeperCell(x=1, y=2, mined=False, revealed=True, num_adjacent_mines=0),
            },
            2:{
                0: MineSweeperCell(x=2, y=0, mined=False, revealed=False, flagged=True, num_adjacent_mines=0),
                1: MineSweeperCell(x=2, y=1, mined=False, revealed=True, num_adjacent_mines=0),
                2: MineSweeperCell(x=2, y=2, mined=False, revealed=True, num_adjacent_mines=0),
            }
        })

    @patch("random.sample")
    def test_on_reveal_flagged_cells_can_block_further_reveal_of_safe_cells(self, mock_sample):
        board_size = 3
        
        mock_sample.return_value = [0]
        board = MineSweeperBoard.create(board_size, 1)

        board.flag(1,1)
        board.flag(1,2)
        board.flag(2,1)
        board.reveal(x=2, y=2)

        assert board == MineSweeperBoard(size=board_size, cells={
            0: {
                0: MineSweeperCell(x=0, y=0, mined=True, revealed=False, num_adjacent_mines=0),
                1: MineSweeperCell(x=0, y=1, mined=False, revealed=False, num_adjacent_mines=1),
                2: MineSweeperCell(x=0, y=2, mined=False, revealed=False, num_adjacent_mines=0),
            },
            1: {
                0: MineSweeperCell(x=1, y=0, mined=False, revealed=False, num_adjacent_mines=1),
                1: MineSweeperCell(x=1, y=1, mined=False, revealed=False, flagged=True, num_adjacent_mines=1),
                2: MineSweeperCell(x=1, y=2, mined=False, revealed=False, flagged=True, num_adjacent_mines=0),
            },
            2:{
                0: MineSweeperCell(x=2, y=0, mined=False, revealed=False, num_adjacent_mines=0),
                1: MineSweeperCell(x=2, y=1, mined=False, revealed=False, flagged=True, num_adjacent_mines=0),
                2: MineSweeperCell(x=2, y=2, mined=False, revealed=True, num_adjacent_mines=0),
            }
        })


    # TODO end game states
    def test_game_is_over_if_a_mine_was_revealed(self):
        assert MineSweeperBoard(size=1, cells={
            0: {
                0: MineSweeperCell(x=0, y=0, mined=True, revealed=True, num_adjacent_mines=0),
            }
        }).is_game_over() == GameResult(game_over=True, victory=False)

    def test_game_is_over_if_all_non_mined_cells_revealed_and_all_mines_are_flagged(self):
        assert MineSweeperBoard(size=3, cells={
            0: {
                0: MineSweeperCell(x=0, y=0, mined=True, revealed=False, flagged=True, num_adjacent_mines=0),
                1: MineSweeperCell(x=0, y=1, mined=False, revealed=True, num_adjacent_mines=1),
                2: MineSweeperCell(x=0, y=2, mined=False, revealed=True, num_adjacent_mines=0),
            },
            1: {
                0: MineSweeperCell(x=1, y=0, mined=False, revealed=True, num_adjacent_mines=1),
                1: MineSweeperCell(x=1, y=1, mined=False, revealed=True, num_adjacent_mines=1),
                2: MineSweeperCell(x=1, y=2, mined=False, revealed=True, num_adjacent_mines=0),
            },
            2:{
                0: MineSweeperCell(x=2, y=0, mined=False, revealed=True, num_adjacent_mines=0),
                1: MineSweeperCell(x=2, y=1, mined=False, revealed=True, num_adjacent_mines=0),
                2: MineSweeperCell(x=2, y=2, mined=False, revealed=True, num_adjacent_mines=0),
            }
        }).is_game_over() == GameResult(game_over=True, victory=True)

    def test_game_is_not_over_under_all_other_circunstances(self):
        assert MineSweeperBoard(size=3, cells={
            0: {
                0: MineSweeperCell(x=0, y=0, mined=True, revealed=False, num_adjacent_mines=0),
                1: MineSweeperCell(x=0, y=1, mined=False, revealed=True, num_adjacent_mines=1),
                2: MineSweeperCell(x=0, y=2, mined=False, revealed=False, num_adjacent_mines=0),
            },
            1: {
                0: MineSweeperCell(x=1, y=0, mined=False, revealed=False, num_adjacent_mines=1),
                1: MineSweeperCell(x=1, y=1, mined=False, revealed=False, flagged=True, num_adjacent_mines=1),
                2: MineSweeperCell(x=1, y=2, mined=False, revealed=False, num_adjacent_mines=0),
            },
            2:{
                0: MineSweeperCell(x=2, y=0, mined=False, revealed=False, num_adjacent_mines=0),
                1: MineSweeperCell(x=2, y=1, mined=False, revealed=False, flagged=True, num_adjacent_mines=0),
                2: MineSweeperCell(x=2, y=2, mined=False, revealed=True, num_adjacent_mines=0),
            }
        }).is_game_over() == GameResult(game_over=False, victory=False)

    # TODO immutability?