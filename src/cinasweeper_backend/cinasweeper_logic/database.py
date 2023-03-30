"""This module contains protocol for database"""
from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from .game import Game
    from .gamemode import GameMode
    from .gamestate import GameState
    from .leaderboard import Leaderboard
    from .user import User


class Database(Protocol):
    """A protocol representing a database of games."""

    def get_games(self, owner: User) -> tuple[Game, ...]:
        """
        Returns all games owned by a given User object.

        Args:
            owner (User): The User object to retrieve games for.
        """

    def get_game(self, identifier: str) -> Game:
        """Returns a game by its id

        Args:
            identifier (str): The id of the game
        """

    def get_leaderboard(self) -> Leaderboard:
        """Returns the leaderboard."""

    def get_top_games(self, num_of_games: int) -> tuple[Game, ...]:
        """Returns the top games.

        Args:
            num_of_games (int): The number of games to return.
        """

    def get_game_state(self, identifier: str) -> GameState:
        """Returns the current state of a given game.

        Args:
            identifier (str): The ID of the game to retrieve the state for.
        """

    def save_game(self, game: Game) -> None:
        """
        Saves the state of a given game.

        Args:
            game (Game): The Game object to save the state for.
        """

    def save_game_state(self, identifier: str, gamestate: GameState) -> None:
        """Saves a given game state to the database.

        Args:
            identifier (str): The ID of the game to save the state for.
            gamestate (GameState): The GameState object to save.
        """

    def create_game(self, owner: User | None, gamemode: GameMode) -> Game:
        """
        Creates a new game owned by the specified User object,
        or by no one if owner is None.

        Args:
            owner (User | None): The User object to create the game for,
                or None if the game should have no owner.
            gamemode (GameMode): The GameMode object to create the game for.
        """
