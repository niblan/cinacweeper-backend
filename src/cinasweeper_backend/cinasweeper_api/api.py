"""The API itself"""
import datetime
import os
from dataclasses import dataclass

import redis
from dotenv import load_dotenv
from fastapi import Body, FastAPI, HTTPException

# фром .сіна_дейтабез імпорт датабейз
from ..cinasweeper_database import Database
from ..cinasweeper_logic import Game as LogicGame  # {перелік класів}
from ..cinasweeper_logic import GameMode
from ..cinasweeper_logic import GameState as LogicGameState
from ..cinasweeper_logic import Move, User
from .authentication import AuthManager

load_dotenv()
host = os.getenv("REDIS_HOST")
port = os.getenv("REDIS_PORT")
redis_client = redis.Redis(
    host=host if host else "localhost",
    port=int(port) if port and port.isdigit() else 6379,
    password=os.getenv("REDIS_PASSWORD"),
    db=0,
)
app = FastAPI()
database = Database(redis_client)
manager = AuthManager()


@dataclass
class Game:
    """A specific game"""

    identifier: str
    owner: str | None
    started: bool
    started_time: datetime.datetime
    game_mode: GameMode
    opponent_id: str | None

    @classmethod
    def from_logic(cls, game: LogicGame) -> "Game":
        """Convert a logic game to the API game

        Args:
            game (LogicGame): The logic game

        Returns:
            Game: The API game
        """
        user = None if game.owner is None else manager.get_user(game.owner.identifier)
        username = None if user is None else user.display_name
        return Game(
            game.identifier,
            username,
            game.started,
            game.started_time,
            game.game_mode,
            game.opponent_id,
        )


@dataclass
class GameState:
    """The state of a game"""

    board: list[list[int | None]]

    @classmethod
    def gameboard_to_board(
        self, gameboard: list[list[int | tuple[int, int]]]
    ) -> list[list[int | None]]:
        ...

    @classmethod
    def from_logic(cls, state: LogicGameState) -> "GameState":
        """Convert a logic game to the API game state

        Args:
            state (LogicGameState): The logic game state

        Returns:
            GameState: The API game state
        """
        return GameState(
            cls.gameboard_to_board(state.gameboard),
        )


def id_and_user_from_jwt(jwt: str) -> tuple[str, User]:
    """Get the user id and user object from a JWT

    Args:
        jwt (jwt): The JWT to get the user id and user object from

    Raises:
        HTTPException: If the JWT is invalid

    Returns:
        tuple[str, User]: The user id and user object
    """
    user_id = manager.verify(jwt)
    if not user_id:
        raise HTTPException(404, "User not found.")

    return user_id["user_id"], User(user_id["user_id"], database=database)


# /games post (приймає жейсон веб ток)
# створюємо гру датабаза.create_game() повертає гейм.
@app.post("/games", response_model=Game)
def create_game(
    jwt: str = Body(embed=True), gamemode: GameMode = Body(embed=True)
) -> Game:
    """Create a new game"""
    user = id_and_user_from_jwt(jwt)[1]

    return Game.from_logic(database.create_game(owner=user, gamemode=gamemode))


# /games get список датакласів
# (Репрезентують гейм)
# (треба написати. Метод який з геймів Артура робить моїх (забирає датабейз)).

# return your games
@app.get("/games")
def get_games(jwt: str = Body(embed=True)) -> list[Game]:
    """Get your own games"""
    user = id_and_user_from_jwt(jwt)[1]
    return [Game.from_logic(game) for game in user.games]


# /leaders_board get ретурнить список геймів
@app.get("/leaders_board")
def get_top_games() -> list[Game]:
    """Get the global top games"""
    return [Game.from_logic(game) for game in database.get_leaderboard().top_n(15)]


# /games/{id гри} інфо про стан
# (з імпортованого викликаю get_game_state(id) з нього можу .мувз)
@app.get("/games/{game_id}")
def get_game_info(game_id: str) -> GameState:
    """Get the state of a game"""
    return GameState.from_logic(database.get_game_state(game_id))


# /games/{id гри} put викликаю get_game(id).claim(owner). Воно приймає жейсон веб ток
@app.put("/games/{game_id}")
def put_game(game_id: str, jwt: str = Body(embed=True)) -> Game:
    """Claim a game; only applies to games that don't have an owner"""
    user = id_and_user_from_jwt(jwt)[1]

    game = database.get_game(game_id)
    game.claim(user)
    return Game.from_logic(game)


@app.post("/games/{game_id}/moves")
def post_move(game_id: str, move: Move, jwt: str = Body(embed=True)) -> GameState:
    """Make a move on a specific game; you must be the owner of the game"""
    user = id_and_user_from_jwt(jwt)[1]

    game = database.get_game(game_id)
    if game.owner != user:
        raise HTTPException(403, "You are not the owner of this game.")

    game.play_move(move)

    return GameState.from_logic(game.state)


# розібратися з імпортом дата
