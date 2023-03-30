"""A user, owning cinasweeper games."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .database import Database
    from .game import Game


@dataclass
class User:
    """A user, owning cinasweeper games."""

    identifier: str
    database: Database

    @property
    def games(self) -> tuple[Game, ...]:
        """Returns the users own games

        Returns:
            tuple[Game, ...]: The users top own games
        """
        return self.database.get_games(self)
