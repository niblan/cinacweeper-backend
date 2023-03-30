"""The state of a given game"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .minesweeper import generate_board, get_info_board, set_mines

if TYPE_CHECKING:
    from .database import Database


@dataclass
class GameState:
    """The state of a given game"""

    database: Database
    gameboard: list[list[tuple[int, int]]] = field(
        default_factory=lambda: generate_board(14, 14)
    )
    mines: list[tuple[int, int]] = field(
        default_factory=lambda: set_mines(14, 14, 56, (6, 9))
    )
    game_info: list[list[int]] | None = None

    def __post_init__(self) -> None:
        """Post init; initializes the game info"""
        if self.game_info is None:
            self.game_info = get_info_board(14, 14, self.mines)
