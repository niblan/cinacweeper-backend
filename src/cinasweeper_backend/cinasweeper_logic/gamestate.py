from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING
from .minesweeper import Minesweeper
from .database import Database

if TYPE_CHECKING:
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