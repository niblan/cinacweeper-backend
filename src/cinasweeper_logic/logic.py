"""This module contains protocol for database"""
from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from .datatest import Game, GameState, Leaderboard, User, GameMode


class Database(Protocol):
    """
    A protocol representing a database of games.

    Attributes:
        None
    """

    def get_games(self, owner: User) -> tuple[Game]:
        """
        Returns all games owned by a given User object.

        Args:
            owner (User): The User object to retrieve games for.

        Returns:
            tuple[Game]:
                A tuple containing all Game objects owned by the given User object.
        """

    def get_game(self, id: str) -> Game:
        ...

    def get_leaderboard(self) -> Leaderboard:
        """
        Returns the leaderboard.

        Returns:
            Leaderboard: The leaderboard object.
        """
    
    def get_top_games(self, num_of_games: int) -> tuple[Game]:
        ...

    def get_game_state(self, id: str) -> GameState:
        """
        Returns the current state of a given game.

        Args:
            identifier (str): The ID of the game to retrieve the state for.

        Returns:
            GameState:The GameState object representing
                the current state of the specified game.
        """

    def save_game(self, game: Game) -> None:
        """
        Saves the state of a given game.

        Args:
            game (Game): The Game object to save the state for.
        """
        ...

    def save_game_state(self, id: str, gamestate: GameState) -> None:
        ...

    def create_game(self, owner: User | None, gamemode: GameMode) -> Game:
        """
        Creates a new game owned by the specified User object,
        or by no one if owner is None.

        Args:
            owner (User | None): The User object to create the game for,
                or None if the game should have no owner.

        Returns:
            Game: The newly created Game object.
        """
