"""The base game class."""
from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import TYPE_CHECKING

from .exceptions import (GameEndedError, GameNotStartedError,
                         PlayingAgainstSelfError)
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
    started_time: datetime.datetime
    game_mode: GameMode
    database: Database
    opponent_id: str | None
    started: bool = False
    score: int = 0
    ended: bool = False

    @property
    def state(self) -> GameState:
        """Returns the current state of the game.

        Returns:
            GameState: The current state of the game.
        """
        return self.database.get_game_state(self.identifier)

    def play_move(self, move: Move) -> bool:
        """Plays a move on the game board based on the given Move object.

        Args:
            move (Move): The Move object to play.

        Raises:
            GameEndedError: If the game has already ended.

        Returns:
            bool: True if the state of the game has changed, False otherwise.
        """
        if self.ended:
            raise GameEndedError
        if not self.started:
            raise GameNotStartedError
        state = self.state
        game_move = main(
            state.gameboard,
            state.mines,
            state.game_info,
            move.action,
            (move.x, move.y),
        )
        self.database.save_game_state(self.identifier, state)
        if game_move in ["Win", "Lose"]:
            if game_move == "Win":
                time = int(
                    (datetime.datetime.now() - self.started_time).total_seconds()
                )
                self.score = int(((1 / time) * 100) ** 2)
            self.ended = True
            self.database.save_game(self)
            return True
        return False

    def claim(self, user: User) -> None:
        """Assigns the game to the specified user if the game has no owner.
        Saves the game to the database.

        Args:
            user (User): The user to assign the game to.

        Raises:
            SelfPlayerException: If the user is already the owner of the opponent game.
        """
        if self.owner is not None or self.opponent_id is None:
            return

        opponent_game = self.database.get_game(self.opponent_id)

        if opponent_game.owner and user.identifier == opponent_game.owner.identifier:
            raise PlayingAgainstSelfError

        opponent_game.started = True
        opponent_game.started_time = datetime.datetime.now()
        self.database.save_game(opponent_game)

        self.owner = user
        self.started = True
        self.started_time = datetime.datetime.now()
        self.database.save_game(self)
