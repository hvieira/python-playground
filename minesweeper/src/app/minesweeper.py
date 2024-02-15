import argparse
import dataclasses
import typing
import typing_extensions
import random


class PickedMineException(Exception):
    pass

class UnsupportedMove(Exception):
    pass


@dataclasses.dataclass
class MineSweeperCell():
    x: int
    y: int
    mined: bool
    revealed: bool
    num_adjacent_mines: int
    flagged: bool = False

    def reveal(self) -> typing_extensions.Self:
        if self.flagged:
            raise UnsupportedMove("Cell is flagged")
        else:
            return dataclasses.replace(self, revealed = True)
    
    def flag(self) -> typing_extensions.Self:
        if self.revealed:
            raise UnsupportedMove("Cell is already revealed")
        else:
            return dataclasses.replace(self, flagged = True)
        
    def unflag(self) -> typing_extensions.Self:
        if self.revealed:
            raise UnsupportedMove("Cell is already revealed")
        else:
            return dataclasses.replace(self, flagged = False)
    
    def has_adjacent_mines(self) -> bool:
        return self.num_adjacent_mines > 0

    def print_to_stdout(self, reveal_all=False) -> None:
        if reveal_all or self.revealed:
            if self.flagged:
                print('F', end='')
            elif self.mined:
                print('X', end='')
            else:
                print(self.num_adjacent_mines, end='')
        else:
            print('#', end='')


@dataclasses.dataclass
class MineSweeperBoard():
    size: int
    cells: typing.Dict[int, typing.Dict[int, MineSweeperCell]]

    def print_to_stdout(self, reveal_all=False) -> None:
        for x in range(0, self.size):
            for y in range(0, self.size):
                self.cells[x][y].print_to_stdout(reveal_all=reveal_all)
            print()

    def reveal(self: typing_extensions.Self, x: int, y: int):
        revealed_cell = self.update_cell(x, y, lambda cell : cell.reveal())

        if revealed_cell.mined:
            raise PickedMineException()

        if not revealed_cell.has_adjacent_mines():
            self._reveal_other_safe_cells(revealed_cell)

    def flag(self: typing_extensions.Self, x: int, y: int):
        self.update_cell(x, y, lambda cell : cell.flag())

    def unflag(self: typing_extensions.Self, x: int, y: int):
        self.update_cell(x, y, lambda cell : cell.unflag())

    def update_cell(self: typing_extensions.Self, 
                    x: int, 
                    y: int, 
                    update_fn: typing.Callable[[MineSweeperCell], MineSweeperCell]) -> None:
        updated = update_fn(self.cells[x][y])
        self.cells[x][y] = updated

        return updated

    def _reveal_other_safe_cells(self, cell):
        to_explore = MineSweeperBoard._adjacent_coordinates(cell.x, cell.y, self.cells)
        explored = {(cell.x, cell.y)}
        while len(to_explore) > 0:
            x, y = to_explore.pop()
            explored.add((x,y))
            
            # if this was a safe/blank cell, reveal the adjacent ones
            if not self.cells[x][y].has_adjacent_mines():
                self.update_cell(x, y, lambda cell : cell.reveal())

                # do not explore what it has been explored already (i.e. avoid non ending loop)
                adjacent_coordinates = MineSweeperBoard._adjacent_coordinates(x, y, self.cells)
                to_explore = to_explore | (adjacent_coordinates - explored)


    @staticmethod 
    def _adjacent_coordinates(x, y, board_cells):
        result = set()
        for ax in [x-1,x,x+1]:
            for ay in [y-1,y,y+1]:
                try:
                    if board_cells[ax][ay]:
                        result.add((ax,ay))
                except KeyError:
                    continue
        
        result.remove((x,y))
        return result

    @staticmethod 
    def _num_of_adjacent_mines(x, y, board_cells):
        num_mines = 0
        for x,y in MineSweeperBoard._adjacent_coordinates(x, y, board_cells): 
            if board_cells[x][y].mined:
                num_mines += 1
        return num_mines


    @staticmethod
    def create(size: int, num_mines: int) -> typing_extensions.Self:
        if num_mines > ((size * size) / 2):
            raise RuntimeError('Number of mines cannot be more than half of the board')
        
        board_cells = {}
        # add the same cells to an array from which we will pick indexes at random so that we dont waste processing
        # with randoms that might clash
        cells_array = []
        
        for x in range(0, size):
            if x not in board_cells:
                board_cells[x] = {}
            for y in range(0, size):
                cell = MineSweeperCell(x,y, mined=False, revealed=False, num_adjacent_mines=0)
                board_cells[x][y] = cell
                cells_array.append(cell)

        # get the cells that will be mined
        indexes = list(range(0, size*size))
        chosen_indexes = random.sample(indexes, num_mines)

        for i in chosen_indexes:
            x = cells_array[i].x
            y = cells_array[i].y

            mined_cell = dataclasses.replace(board_cells[x][y], mined=True)
            board_cells[x][y] = mined_cell

        # scan board to define number of adjacent mines
        for x in range(0, size):
            for y in range(0, size):
                num_of_adjacent_mines = MineSweeperBoard._num_of_adjacent_mines(x, y, board_cells)
                updated_cell = dataclasses.replace(board_cells[x][y], num_adjacent_mines=num_of_adjacent_mines)
                board_cells[x][y] = updated_cell

        return MineSweeperBoard(size, board_cells)
        

if __name__ == "main":

    argparser = argparse.ArgumentParser()
    argparser.add_argument('size', type=int, metavar='S', help='size of the board (square)')
    argparser.add_argument('mines', type=int, metavar='M', help='size of the board (square)')

    parsed_args = argparser.parse_args()

    board = MineSweeperBoard.create(parsed_args.size, parsed_args.mines)
    board.print_to_stdout(reveal_all=True)


    input = input('Enter coordinates in form [x,y] to reveal:')
    raw_coords = input.split(',')
    if len(raw_coords) != 2:
        raise RuntimeError(f'Coordinates in wrong format {input}')

    x = int(raw_coords[0])
    y = int(raw_coords[1])

    try:
        board.reveal(x, y)
    except PickedMineException:
        print('BOOM!')        

    board.print_to_stdout()
