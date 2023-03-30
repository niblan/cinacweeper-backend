"""The implementation of the redis database"""
from __future__ import annotations

import datetime
import uuid
from typing import TYPE_CHECKING

from redis.commands.json.path import Path
from redis.commands.search.field import NumericField, TagField, TextField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query

from ..cinasweeper_logic import Game, GameMode, GameState, Leaderboard, User

if TYPE_CHECKING:
    import redis

    from ..cinasweeper_logic import Database


class Serializer:
    """Serializes and deserializes games"""

    def __init__(self, database: Database) -> None:
        """Initializes the serializer

        Args:
            database (Database): The database to use
        """
        self.database = database

    # TODO: consider using TypedDict instead of dict

    def from_json(self, json: dict) -> Game:
        """Deserializes a game from json

        Args:
            json (dict): The json to deserialize

        Returns:
            Game: The deserialized game
        """
        return Game(
            json["id"],
            User(json["owner"], self.database),
            json["started"],
            json["started_time"],
            json["type"],
            json["ended"],
            json["opponent_id "],
            json["score"],
        )

    def to_json(self, game: Game) -> dict:
        """Serializes a game to json

        Args:
            game (Game): The game to serialize

        Returns:
            dict: The serialized game
        """
        return {
            "id": game.id,
            "owner": None if game.owner is None else game.owner.id,
            "started": game.started,
            "started_time": game.started_time,
            "type": game.game_mode,
            "ended": game.ended,
            "opponent_id": game.opponent_id,
            "score": game.score,
        }

    def state_from_json(self, json: dict) -> GameState:
        """Deserializes a game state from json

        Args:
            json (dict): The json to deserialize

        Returns:
            GameState: The deserialized game state
        """
        # Check it with the GameState
        return GameState(
            database=self.database,
            gameboard=json["gameboard"],
            mines=json["mines"],
            game_info=json["game_info"],
        )

    def state_to_json(self, state: GameState) -> dict:
        """Serializes a game state to json

        Args:
            state (GameState): The game state to serialize

        Returns:
            dict: The serialized game state
        """
        return {
            "gameboard": state.gameboard,
            "mines": state.mines,
            "game_info": state.game_info,
        }


class RedisDatabase:
    """A database that uses RedisJson and RedisSearch to store the games"""

    def __init__(self, redis_client: redis.Redis) -> None:
        """Initialize the database

        Args:
            redis_client (redis.Redis): The redis client to use
        """
        self.redis_client = redis_client
        self.serializer = Serializer(self)

    def setup_index(self) -> None:
        """Set up the index for the games"""
        schema = (
            TextField("$.owner", as_name="owner"),
            TagField("$.type", as_name="type"),
            NumericField("$.score", as_name="score"),
        )

        self.redis_client.ft().create_index(
            schema,
            definition=IndexDefinition(prefix=["game:"], index_type=IndexType.JSON),
        )

    def get_games(self, owner: User) -> tuple[Game, ...]:
        """Returns top N games owned by a given User object.

        Args:
            owner (User): The User object to retrieve games for.

        Returns:
            tuple[Game]:
                A tuple containing all Game objects owned by the given User object.
        """
        query = Query(owner.id).sort_by("score", asc=False)
        games = (
            self.redis_client.ft()
            .search(
                query,
            )
            .docs
        )
        return tuple(self.serializer.from_json(game) for game in games)

    def get_game(self, identifier: str) -> Game:
        """Returns a game by its id

        Args:
            identifier (str): The id of the game

        Returns:
            Game: The game
        """
        return self.serializer.from_json(
            self.redis_client.json().get(f"game:{identifier}")
        )

    def get_top_games(self, num_of_games: int) -> tuple[Game, ...]:
        """Get the global top_n games

        Args:
            num_of_games (int): The number of games to get

        Returns:
            tuple[Game, ...]: The top_n games
        """
        # TODO: think about how to make this *not* top-10 but top-n
        query = Query("*").sort_by("score", asc=False)
        games = (
            self.redis_client.ft()
            .search(
                query,
            )
            .docs
        )
        return tuple(self.serializer.from_json(game) for game in games)

    def get_game_state(self, identifier: str) -> GameState:
        """Returns the current state of a given game.

        Args:
            identifier (str): The ID of the game to retrieve the state for.

        Returns:
            GameState:The GameState object representing
                the current state of the specified game.
        """
        return self.serializer.state_from_json(
            self.redis_client.json().get(f"gamestate:{identifier}")
        )

    def save_game_state(self, identifier: str, gamestate: GameState) -> None:
        """Saves a given game state to the database.

        Args:
            identifier (str): The ID of the game to save the state for.
            gamestate (GameState): The GameState object to save.
        """
        self.redis_client.json().set(
            f"gamestate:{identifier}",
            Path.root_path(),
            self.serializer.state_to_json(gamestate),
        )

    def save_game(self, game: Game) -> None:
        """
        Saves the state of a given game.

        Args:
            game (Game): The Game object to save the state for.
        """
        self.redis_client.json().set(
            f"game:{game.id}",
            Path.root_path(),
            self.serializer.to_json(game),
        )

    def create_game(self, owner: User | None, gamemode: GameMode) -> Game:
        """Creates a new game owned by the specified User object,
        or by no one if owner is None.

        Args:
            owner (User | None): The User object to create the game for,
                or None if the game should have no owner.
            gamemode (GameMode): The GameMode object to create the game for.

        Returns:
            Game: The newly created Game object.
        """
        identifier = str(uuid.uuid4())
        game = Game(
            identifier,
            started=False,
            started_time=datetime.datetime.now(),
            owner=owner,
            database=self,
            game_mode=gamemode,
            opponent_id=None,
            score=0,
        )
        self.save_game(game)
        state = GameState(self)
        self.save_game_state(identifier, state)
        return game

    def get_leaderboard(self) -> Leaderboard:
        """Returns the global leaderboard.

        Returns:
            Leaderboard: The global leaderboard.
        """
        return Leaderboard(self)
