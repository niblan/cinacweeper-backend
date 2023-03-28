from __future__ import annotations
from dataclasses import dataclass
from .minesweeper import Minesweeper
from .database import Database

@dataclass
class GameState:
    ended: bool
    database: Database
    gameboard: list