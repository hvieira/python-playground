import argparse
import dataclasses
import typing
import typing_extensions
import random


class UnsupportedMoveException(Exception):
    pass


@dataclasses.dataclass
class GameResult():
    game_over: bool
    victory: bool

@dataclasses.dataclass(frozen=True)
class Coordinates():
    x: int
    y: int

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
            raise UnsupportedMoveException("Cell is flagged")
        else:
            return dataclasses.replace(self, revealed = True)
    
    def flag(self) -> typing_extensions.Self:
        if self.revealed:
            raise UnsupportedMoveException("Cell is already revealed")
        else:
            return dataclasses.replace(self, flagged = True)
        
    def unflag(self) -> typing_extensions.Self:
        if self.revealed:
            raise UnsupportedMoveException("Cell is already revealed")
        else:
            return dataclasses.replace(self, flagged = False)
    
    def has_adjacent_mines(self) -> bool:
        return self.num_adjacent_mines > 0

    def print_to_stdout(self, reveal_all=False) -> None:
        if self.flagged:
            print('F', end='')
        elif reveal_all or self.revealed:
            if self.mined:
                print('X', end='')
            else:
                print(self.num_adjacent_mines, end='')
        else:
            print('#', end='')


@dataclasses.dataclass
class MineSweeperBoard():
    size: int
    cells: typing.Dict[Coordinates, MineSweeperCell]

    def print_to_stdout(self, reveal_all=False) -> None:
        for x in range(0, self.size):
            for y in range(0, self.size):
                self.cells[Coordinates(x, y)].print_to_stdout(reveal_all=reveal_all)
            print()

    def reveal(self: typing_extensions.Self, x: int, y: int):
        coords = Coordinates(x, y)
        revealed_cell = self.update_cell(coords, lambda cell : cell.reveal())

        if revealed_cell.mined:
            return

        if not revealed_cell.has_adjacent_mines():
            self._reveal_other_safe_cells(coords)

    def flag(self: typing_extensions.Self, x: int, y: int):
        self.update_cell(Coordinates(x, y), lambda cell : cell.flag())

    def unflag(self: typing_extensions.Self, x: int, y: int):
        self.update_cell(Coordinates(x, y), lambda cell : cell.unflag())

    def update_cell(self: typing_extensions.Self, 
                    coordinates: Coordinates, 
                    update_fn: typing.Callable[[MineSweeperCell], MineSweeperCell]) -> None:
        updated = update_fn(self.cells[coordinates])
        self.cells[coordinates] = updated

        return updated

    # rules:
    # if cell is mined and revealed -> lost
    # if all non mined cells are revealed + all mines are flagged -> win
    def is_game_over(self):
        total_cells = self.size * self.size
        # TODO this could be a board metadata to ease calculations
        num_mines = 0
        
        num_mines_non_flagged = 0
        num_non_mine_cells_revealed = 0
        for x in range(0, self.size):
            for y in range(0, self.size):
                coords = Coordinates(x, y)
                if self.cells[coords].mined:
                    num_mines += 1
                    # revealed a mine. game is lost
                    if self.cells[coords].revealed:
                        return GameResult(game_over=True, victory=False)
                    
                    if not self.cells[coords].flagged:
                        num_mines_non_flagged += 1
                else:
                    if self.cells[coords].revealed:
                        num_non_mine_cells_revealed += 1

        success = num_mines_non_flagged == 0 and (total_cells-num_mines) == num_non_mine_cells_revealed
        return GameResult(game_over=success, victory=success)

    def _reveal_other_safe_cells(self, start_coordinates: Coordinates):
        to_explore = MineSweeperBoard._adjacent_coordinates(start_coordinates, self.cells)
        explored = {start_coordinates}
        while len(to_explore) > 0:
            coords = to_explore.pop()
            explored.add(coords)
            
            # if this is a safe/blank cell (not flagged), reveal the adjacent ones
            if not self.cells[coords].has_adjacent_mines() and not self.cells[coords].flagged:
                self.update_cell(coords, lambda cell : cell.reveal())

                # do not explore what it has been explored already (i.e. avoid non ending loop)
                adjacent_coordinates = MineSweeperBoard._adjacent_coordinates(coords, self.cells)
                to_explore = to_explore | (adjacent_coordinates - explored)


    @staticmethod 
    def _adjacent_coordinates(center: Coordinates, 
                              board_cells: typing.Mapping[Coordinates, MineSweeperCell]) -> typing.MutableSet[Coordinates]:
        result = set()
        for ax in [center.x-1,center.x,center.x+1]:
            for ay in [center.y-1,center.y,center.y+1]:
                coordinates = Coordinates(x=ax, y=ay)
                try:
                    if board_cells[coordinates]:
                        result.add(coordinates)
                except KeyError:
                    continue
        
        result.remove(center)
        return result

    @staticmethod 
    def _num_of_adjacent_mines(center: Coordinates, board_cells):
        num_mines = 0
        for coordinates in MineSweeperBoard._adjacent_coordinates(center, board_cells): 
            if board_cells[coordinates].mined:
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
            for y in range(0, size):
                cell = MineSweeperCell(x,y, mined=False, revealed=False, num_adjacent_mines=0)
                board_cells[Coordinates(x, y)] = cell
                cells_array.append(cell)

        # get the cells that will be mined
        indexes = list(range(0, size*size))
        chosen_indexes = random.sample(indexes, num_mines)

        for i in chosen_indexes:
            x = cells_array[i].x
            y = cells_array[i].y

            coords = Coordinates(x, y)
            mined_cell = dataclasses.replace(board_cells[coords], mined=True)
            board_cells[coords] = mined_cell

        # scan board to define number of adjacent mines
        for x in range(0, size):
            for y in range(0, size):
                coords = Coordinates(x, y)
                num_of_adjacent_mines = MineSweeperBoard._num_of_adjacent_mines(coords, board_cells)
                updated_cell = dataclasses.replace(board_cells[coords], num_adjacent_mines=num_of_adjacent_mines)
                board_cells[coords] = updated_cell

        return MineSweeperBoard(size, board_cells)
        

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument('size', type=int, metavar='S', help='size of the board (square)')
    argparser.add_argument('mines', type=int, metavar='M', help='size of the board (square)')

    parsed_args = argparser.parse_args()

    board = MineSweeperBoard.create(parsed_args.size, parsed_args.mines)
    # this is just to help debug
    board.print_to_stdout(reveal_all=True)

    game_over = False

    while(not game_over):
        raw_command = input('Enter command in form [C,X,Y] where C is a command: F (flag), U (unflag), R (reveal) and X,Y are coordinates (0 index):')
        command = raw_command.split(',')
        if len(command) != 3:
            raise RuntimeError(f'Coordinates in wrong format {input}')

        x = int(command[1])
        y = int(command[2])
        match(command[0]):
            case 'R':
                board.reveal(x, y)
            case 'F':
                try:
                    board.flag(x, y)
                except UnsupportedMoveException:
                    print('unsupported move!')
            case 'U':
                try:
                    board.unflag(x, y)
                except UnsupportedMoveException:
                    print('unsupported move!')
            case _:
                print('Invalid command')

        game_result = board.is_game_over()
        game_over = game_result.game_over
        
        board.print_to_stdout()
        match game_result:
            case GameResult(game_over=True, victory=True):
                print('You managed to clear the field!')
            case GameResult(game_over=True, victory=False):
                print('That was your last step, before you heard the BOOM.')
            case _:
                pass
