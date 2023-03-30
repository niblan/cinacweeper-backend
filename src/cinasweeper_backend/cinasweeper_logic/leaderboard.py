from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING
from .database import Database

if TYPE_CHECKING:
    from .game import Game

@dataclass
class Leaderboard:
    database: Database

    def top_n(self, n: int = 10) -> tuple[Game]:
        #return from database
        return self.database.get_top_games(n)
