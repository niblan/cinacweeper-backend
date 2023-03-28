from __future__ import annotations
from dataclasses import dataclass
from .minesweeper import generate_board, set_mines, get_info_board, main
from .database import Database
from .move import Move

@dataclass
class GameState:
    ended: bool
    database: Database
    gameboard = generate_board(14, 14)
    mines = set_mines(14, 14, 56, (6, 9))
    game_info = get_info_board(14, 14, mines)