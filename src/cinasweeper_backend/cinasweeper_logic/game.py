"""The base game class."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .exceptions import GameEndedError
from .minesweeper import main

if TYPE_CHECKING:
    import datetime

    from .database import Database
    from .gamemode import GameMode
    from .gamestate import GameState
    from .move import Move
    from .user import User


@dataclass
class Game:
    """A class representing a Minesweeper game."""

    identifier: str
    owner: User | None
    started: bool
    started_time: datetime.datetime
    game_mode: GameMode
    database: Database
    opponent_id: str | None
    score: int = 0
    ended: bool = False

    @property
    def state(self) -> GameState:
        """Returns the current state of the game.

        Returns:
            GameState: The current state of the game.
        """
        return self.database.get_game_state(self.identifier)

    def play_move(self, move: Move) -> None:
        """Plays a move on the game board based on the given Move object.

        Args:
            move (Move): The Move object to play.

        Raises:
            GameEndedError: If the game has already ended.
        """
        if self.ended:
            raise GameEndedError
        state = self.state
        game_move = main(
            state.gameboard,
            state.mines,
            state.game_info,
            move.action,
            (move.x, move.y),
        )
        if game_move in ["Win", "Lose"]:
            if game_move == "Win":
                time = int(
                    (datetime.datetime.now() - self.started_time).total_seconds()
                )
                self.score = int(((1 / time) * 100) ** 2)
            self.ended = True
            self.database.save_game(self)
        self.database.save_game_state(self.identifier, state)

    def claim(self, user: User) -> None:
        """Assigns the game to the specified user if the game has no owner.
        Saves the game to the database.

        Args:
            user (User): The user to assign the game to.
        """
        if self.owner is None:
            self.owner = user
        self.database.save_game(self)
