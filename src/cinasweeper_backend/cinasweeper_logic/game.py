from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING
import datetime
from .user import User
from .gamemode import GameMode
from .database import Database
from .move import Move
from .minesweeper import main
from .exceptions import GameIsEnded

if TYPE_CHECKING:
    from .gamestate import GameState

@dataclass
class Game:
    """A class representing a Minesweeper game.

    Args:
        id (str): A unique identifier for the game.
        owner (User | None): The user object who created the game, or None if the game has not yet been claimed.
        started (bool): True if the game has started, False otherwise.
        started_time (datetime.datetime): The time at which the game started.
        game_mode (GameMode): The game mode object representing the difficulty level of the game.
        database (Database): The database object used to store and retrieve game data.
        ended (bool): True if the game has ended, False otherwise.
        opponent_id (str | None): The identifier of the opponent user, or None if the game is not multiplayer.
        score (int): The score of the game, which is the number of cells uncovered without detonating a mine.

    Methods:
        state(self) -> GameState:
            Returns the current game state as a GameState object.

        play_move(self, move: Move):
            Plays the given move on the game board. If the move results in a win or a loss, the game is marked as ended.
            Raises GameIsEnded exception if the game has already ended.

        claim(self, user: User) -> None:
            Claims the game for the given user, if it has not yet been claimed. Does nothing if the game has already been claimed.
    """
    id: str
    owner: User | None
    started: bool
    started_time: datetime.datetime
    game_mode: GameMode
    database: Database
    ended = False
    opponent_id: str | None
    score: int

    @property
    def state(self) -> GameState:
        return self.database.get_game_state(self.id)

    def play_move(self, move: Move):
        """
        Plays a move on the game board based on the given Move object.

        Raises:
            GameIsEnded: If the game has already ended.

        Returns:
            None
        """
        if self.ended:
            raise GameIsEnded
        game_move = main(self.state.gameboard, self.state.mines, self.state.game_info, move.action, (move.x, move.y))
        if game_move == 'Win' or game_move == 'Lose':
            self.ended = True
        return self.database.save_game_state(self.id, self.state)

    def claim(self, user: User) -> None:
        """
        Assigns the game to the specified user if the game has no owner.
        Saves the game to the database.

        Returns:
            None
        """
        if self.owner is None:
            self.owner = user
        self.database.save_game(self)
