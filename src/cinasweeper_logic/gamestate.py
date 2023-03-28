from dataclasses import dataclass
from typing import TYPE_CHECKING
from .minesweeper import generate_board, set_mines, get_info_board, flag, end_game, check_ceil, get_step

if TYPE_CHECKING:
    from .database import Database
    from .move import Move

@dataclass
class GameState:
    ended: bool
    database: Database
    gameboard: list

    @property
    def moves(self) -> tuple[Move]:
        ...

    def play_move(self, move: Move) -> None:
        # Raises all the relevant exceptions
        pass

    @property
    def is_over(self) -> bool:
        ...
