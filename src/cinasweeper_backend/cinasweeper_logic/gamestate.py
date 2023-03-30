from __future__ import annotations
from dataclasses import dataclass, field
from .minesweeper import generate_board, set_mines, get_info_board, main
from .database import Database
from .move import Move

@dataclass
class GameState:
    database: Database
    gameboard: list[list[tuple[int, int]]] = field(default_factory=lambda: generate_board(14, 14))
    mines: list[tuple[int, int]] = field(default_factory=lambda: set_mines(14, 14, 56, (6, 9)))
    game_info: list[list[int]] | None = None

    def __post_init__(self):
        if self.game_info is None:
            self.game_info = get_info_board(14, 14, self.mines)
