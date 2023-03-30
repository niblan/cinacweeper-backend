"""The games leaderboard"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .database import Database
    from .game import Game


@dataclass
class Leaderboard:
    """The games leaderboard"""

    database: Database

    def top_n(self, num_games: int = 10) -> tuple[Game, ...]:
        """Returns the top n games

        Args:
            num_games (int): The number of games to return. Defaults to 10.

        Returns:
            tuple[Game, ...]: The top n games
        """
        return self.database.get_top_games(num_games)
