"""The implementation of the redis database"""
import datetime
import json

from os import environ
from dotenv import load_dotenv
import redis
from ..cinasweeper_logic import Game, GameMode, GameState, Leaderboard, User
load_dotenv()

class Database:
    """
    A database of games.
    Attributes:
        None
    """

    def __init__(self) -> None:
        self.redis_client = redis.Redis(environ.get("DB_HOST"),
                                        environ.get("DB_USER"),
                                        environ.get("DB_PASSWORD")
                                        )

    def get_games(self, owner: User) -> tuple[Game]:
        """
        Returns all games owned by a given User object.
        Args:
            owner (User): The User object to retrieve games for.
        Returns:
            tuple[Game]:
                A tuple containing all Game objects owned by the given User object.
        """
        result = self.redis_client.hscan("games", match = f'owner:{owner.id}')
        games = [Game(**game) for game in result]
        return tuple(games)

    def get_game(self, id: str) -> Game:
        """
        Get game_info from the hash games and turn it into a Game object
        """
        return Game(**json.loads((self.redis_client.hget("games", f"{id}"))))

    def get_leaderboard(self) -> Leaderboard:
        """
        Returns the leaderboard.
        Returns:
            Leaderboard: The leaderboard object.
        """
        return Leaderboard(self)

    def get_top_games(self, num_of_games: int) -> tuple[Game]:
        result = self.redis_client.execute_command('HSCAN', 'myhash', '0', 'MATCH', '*', 'COUNT', num_of_games, 'SORT', 'BY', 'myhash:*->score', 'GET', '#', 'GET', '*', 'DESC')
        games = [Game(**json.loads(game)) for game in result]
        return tuple(games)

    def get_game_state(self, identifier: str) -> GameState:
        """
        Returns the current state of a given game.
        Args:
            identifier (str): The ID of the game to retrieve the state for.
        Returns:
            GameState: The GameState object representing
                the current state of the specified game.
        """
        game_data = self.redis_client.get(f"game:{identifier}")
        if game_data:
            return GameState(**json.loads(game_data))
        return None

    def save_game(self, game: Game) -> None:
        """
        Saves the state of a given game.
        Args:
            game (Game): The Game object to save the state for.
        """
        game_data = json.dumps(vars(game))
        self.redis_client.hset("games", f"{game.id}", game_data)

    def save_game_state(self, id: str, gamestate: GameState) -> None:
        """
        Save the state of the game using game identifier
        
        """
        game_state = json.dumps(vars(gamestate))
        self.redis_client.set(f"game:{id}", game_state)

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
        game_id = self.redis_client.incr("game_id")
        game = Game(
            str(game_id),
            owner,
            False,
            datetime.datetime.now(),
            gamemode,
            self,
            score = 0
        )
        self.save_game(game)
        #if owner:
        #    self.redis_client.sadd(f"user:{owner.id}:games", game.id)
        return game
