"""The API itself"""
import datetime
import json
import os
from dataclasses import dataclass
from typing import List, Optional

import redis
from fastapi import Body, Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# фром .сіна_дейтабез імпорт датабейз
from ..cinasweeper_database import Database
from ..cinasweeper_logic import Game as LogicGame  # {перелік класів}
from ..cinasweeper_logic import GameEndedError, GameMode, GameNotStartedError
from ..cinasweeper_logic import GameState as LogicGameState
from ..cinasweeper_logic import Move, PlayingAgainstSelfError, User
from .authentication import AuthManager


def get_conf_value(key: str) -> str:
    """Get a value from the config file
    Args:
        key (str): The key to get the value from
    Raises:
        KeyError: If the key doesn't exist
    Returns:
        str: The value
    """
    try:
        with open("environment.json", "r") as file:
            return json.load(file)[key]
    except FileNotFoundError:
        return os.getenv(key)


host = get_conf_value("REDIS_HOST")
port = get_conf_value("REDIS_PORT")
redis_client = redis.Redis(
    host=host if host else "localhost",
    port=int(port) if port and port.isdigit() else 6379,
    password=get_conf_value("REDIS_PASSWORD"),
    db=0,
)
app = FastAPI()
database = Database(redis_client)
manager = AuthManager()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@dataclass
class Game:
    """A specific game"""

    identifier: str
    owner: Optional[str]
    started: bool
    started_time: datetime.datetime
    game_mode: GameMode
    opponent_id: Optional[str]
    score: int
    ended: bool

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
            game.score,
            game.ended,
        )


@dataclass
class GameState:
    """The state of a game"""

    board: List[List[Optional[int]]]

    @classmethod
    def gameboard_to_board(
        cls, state: LogicGameState, full: bool = False
    ) -> List[List[Optional[int]]]:  # save only opend ceils (tuples -> None)
        """Convert a gameboard to a board that can be sent to the client
        (remove all unopened cells)
        Args:
            state (LogicGameState): The gameboard
        Returns:
            List[List[Optional[int]]]: The board
        """
        return [
            [
                None
                if isinstance(cell, list)
                else (-2 if isinstance(cell, str) else cell)
                for cell in row
            ]
            for row in (state.game_info if full else state.gameboard)
        ]

    @classmethod
    def from_logic(cls, state: LogicGameState, full: bool = False) -> "GameState":
        """Convert a logic game to the API game state
        Args:
            state (LogicGameState): The logic game state
            full (bool): Whether to send the full board or not.
        Returns:
            GameState: The API game state
        """
        return GameState(
            cls.gameboard_to_board(state, full),
        )


@dataclass
class MoveResult:
    """The result of a move"""

    state: GameState
    game_changed: bool


@dataclass
class UnauthorizedMessage:
    """The message to send when the user is unauthorized"""

    detail: str = "Bearer token missing or unknown"


def user_from_jwt(jwt: str) -> User:
    """Get the user object from a JWT
    Args:
        jwt (str): The JWT to get the user id and user object from
    Raises:
        HTTPException: If the JWT is invalid
    Returns:
        User: The user object
    """
    user_id = manager.verify(jwt)
    if not user_id:
        raise HTTPException(401, UnauthorizedMessage.detail)

    return User(user_id["user_id"], database=database)


async def get_token(
    authorization: str = Header(default="Bearer "),
) -> User:
    """Get the user id and user object from the authorization header
    Args:
        authorization (str): The authorization header.
    Raises:
        HTTPException: If the authorization header is invalid
    Returns:
        User: The user object
    """
    method, token = authorization.split(" ")
    if method != "Bearer":
        raise HTTPException(401, UnauthorizedMessage.detail)
    return user_from_jwt(token)


# /games post (приймає жейсон веб ток)
# створюємо гру датабаза.create_game() повертає гейм.
@app.post(
    "/games",
    response_model=Game,
    responses={401: dict(model=UnauthorizedMessage)},
)
def create_game(
    gamemode: GameMode = Body(embed=True), user: User = Depends(get_token)
) -> Game:
    """Create a new game"""
    return Game.from_logic(database.create_game(owner=user, gamemode=gamemode))


# /games get список датакласів
# (Репрезентують гейм)
# (треба написати. Метод який з геймів Артура робить моїх (забирає датабейз)).

# return your games
@app.get(
    "/games",
    responses={401: dict(model=UnauthorizedMessage)},
)
def get_games(
    user: User = Depends(get_token),
) -> List[Game]:
    """Get your own games"""
    return [Game.from_logic(game) for game in user.games]


# /leaders_board get ретурнить список геймів
@app.get("/leaders_board")
def get_top_games() -> List[Game]:
    """Get the global top games"""
    return [Game.from_logic(game) for game in database.get_leaderboard().top_n(15)]


@app.get("/games/{game_id}")
def get_game_info(game_id: str) -> Game:
    """Get the game"""
    return Game.from_logic(database.get_game(game_id))


# /games/{id гри} інфо про стан
# (з імпортованого викликаю get_game_state(id) з нього можу .мувз)
@app.get("/games/{game_id}/state")
def get_game_info(game_id: str) -> GameState:
    """Get the state of a game"""
    game = database.get_game(game_id)
    return GameState.from_logic(game.state, game.ended)


# /games/{id гри} put викликаю get_game(id).claim(owner). Воно приймає жейсон веб ток
@app.put(
    "/games/{game_id}",
    responses={401: dict(model=UnauthorizedMessage)},
)
def put_game(game_id: str, user: User = Depends(get_token)) -> Game:
    """Claim a game; only applies to games that don't have an owner"""

    game = database.get_game(game_id)
    try:
        game.claim(user)
    except PlayingAgainstSelfError:
        raise HTTPException(400, "You can`t play against yourself.")
    return Game.from_logic(game)


@app.post(
    "/games/{game_id}/moves",
    responses={401: dict(model=UnauthorizedMessage)},
)
def post_move(game_id: str, move: Move, user: User = Depends(get_token)) -> MoveResult:
    """Make a move on a specific game; you must be the owner of the game"""
    game = database.get_game(game_id)
    if game.owner != user:
        raise HTTPException(403, "You are not the owner of this game.")
    try:
        game_changed = game.play_move(move)
    except GameEndedError:
        raise HTTPException(409, "Game over.")
    except GameNotStartedError:
        raise HTTPException(404, "Game is not started.")

    state = GameState.from_logic(game.state, game.ended)
    return MoveResult(state, game_changed)
