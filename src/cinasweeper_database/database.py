"""The implementation of the redis database"""
import datetime
import pickle

import redis

from ..cinasweeper_logic import Game, GameMode, GameState, Leaderboard, User


class Database:
    """
    A protocol representing a database of games.
    Attributes:
        None
    """

    def __init__(self) -> None:
        self.redis_client = redis.Redis()

    def get_games(self, owner: User) -> tuple[Game]:
        """
        Returns all games owned by a given User object.
        Args:
            owner (User): The User object to retrieve games for.
        Returns:
            tuple[Game]:
                A tuple containing all Game objects owned by the given User object.
        """
        game_ids = self.redis_client.smembers(f"user:{owner.id}:games")
        games = []
        for game_id in game_ids:
            game = self.redis_client.get(f"game:{game_id}")
            if game:
                games.append(game)
        return tuple(games)

    def get_leaderboard(self) -> Leaderboard:
        """
        Returns the leaderboard.
        Returns:
            Leaderboard: The leaderboard object.
        """
        leaderboard_data = self.redis_client.get("leaderboard")
        if leaderboard_data:
            return pickle.loads(leaderboard_data)
        return Leaderboard(self)

    def get_game_state(self, identifier: str) -> GameState:
        """
        Returns the current state of a given game.
        Args:
            identifier (str): The ID of the game to retrieve the state for.
<<<<<<< HEAD:src/cinasweeper_database/database
=======

>>>>>>> 1cb917b46857fcb4d257b2a677bb4fa5bfaf54f2:src/cinasweeper_database/database.py
        Returns:
            GameState: The GameState object representing
                the current state of the specified game.
        """
        game_data = self.redis_client.get(f"game:{identifier}")
        if game_data:
            return pickle.loads(game_data)
        return None

    def save_game(self, game: Game) -> None:
        """
        Saves the state of a given game.
        Args:
            game (Game): The Game object to save the state for.
        """
        game_data = pickle.dumps(game)
        self.redis_client.set(f"game:{game.id}", game_data)

    def create_game(self, owner: User | None) -> Game:
        """
        Creates a new game owned by the specified User object,
        or by no one if owner is None.
<<<<<<< HEAD:src/cinasweeper_database/database
        Args:
            owner (User | None): The User object to create the game for,
                or None if the game should have no owner.
=======

        Args:
            owner (User | None): The User object to create the game for,
                or None if the game should have no owner.

>>>>>>> 1cb917b46857fcb4d257b2a677bb4fa5bfaf54f2:src/cinasweeper_database/database.py
        Returns:
            Game: The newly created Game object.
        """
        game_id = self.redis_client.incr("game_id")
        game = Game(
            str(game_id),
            owner,
            False,
            datetime.datetime.now(),
            GameMode.ONE_V_ONE,
            self,
        )
        self.save_game(game)
        if owner:
            self.redis_client.sadd(f"user:{owner.id}:games", game.id)
        return game