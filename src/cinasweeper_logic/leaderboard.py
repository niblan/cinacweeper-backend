from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .database import Database
    from .game import Game

@dataclass
class Leaderboard:
    database: Database

    def top_n(self, n: int = 10) -> tuple[Game]:
        #return from database
        ...
