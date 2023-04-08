"""The state of a given game"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .minesweeper import generate_board, get_info_board, main, set_mines

if TYPE_CHECKING:
    from .database import Database
    from .move import Move


@dataclass
class GameState:
    """The state of a given game"""

    database: Database
    gameboard: list[list[tuple[int, int] | int]] | None = None
    mines: list[tuple[int, int]] | None = None
    game_info: list[list[tuple[int, int] | int]] | None = None

    def play_move(self, move: Move) -> str:
        """Plays a move on the gameboard

        Args:
            move (Move): The move to play

        Returns:
            str: The result of the move
        """
        if self.gameboard is None:
            self.gameboard = generate_board(14, 14)
            self.mines = set_mines(14, 14, 30, (move.x, move.y))
            self.game_info = get_info_board(14, 14, self.mines)
        return main(
            self.gameboard,
            self.mines,
            self.game_info,
            move.action,
            (move.x, move.y),
        )
