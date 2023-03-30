"""The API itself"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from fastapi import FastAPI, HTTPException

# фром .сіна_дейтабез імпорт датабейз
from ..cinasweeper_database import Database
from ..cinasweeper_logic import Game as LogicGame  # {перелік класів}
from ..cinasweeper_logic import GameMode
from ..cinasweeper_logic import GameState as LogicGameState
from ..cinasweeper_logic import Move, User
from .authentication import AuthManager

if TYPE_CHECKING:
    import datetime


app = FastAPI()
database = Database(...)
manager = AuthManager()


@dataclass
class Game:
    """A game object, the one sent to the client"""

    id: str
    owner: str | None
    started: bool
    started_time: datetime.datetime
    game_mode: GameMode

    @classmethod
    def from_logic(cls, game: LogicGame) -> Game:
        """Convert a logic game to the API game

        Args:
            game (LogicGame): The logic game

        Returns:
            Game: The API game
        """
        user = None if game.owner is None else manager.get_user(game.owner.id)
        username = None if user is None else user["username"]
        return Game(
            game.id,
            username,
            game.started,
            game.started_time,
            game.game_mode,
        )


@dataclass
class GameState:
    """A game state object, the one sent to the client"""

    gameboard: list[list[tuple[int, int]]]
    mines: list[tuple[int, int]]
    game_info: list[list[int]] | None

    @classmethod
    def from_logic(cls, state: LogicGameState) -> GameState:
        """Convert a logic game to the API game state

        Args:
            state (LogicGameState): The logic game state

        Returns:
            GameState: The API game state
        """
        return GameState(
            state.gameboard,
            state.mines,
            state.game_info,
        )


def id_and_user_from_jwt(jwt: str) -> tuple[str, User]:
    """Get the user id and user object from a JWT

    Args:
        jwt (str): The JWT to get the user id and user object from

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
def create_game(jwt: str, gamemode: GameMode) -> Game:
    """Create a new game

    Args:
        jwt (str): The JWT of the user creating the game
        gamemode (GameMode): The gamemode of the game

    Returns:
        Game: The created game
    """
    user = id_and_user_from_jwt(jwt)[1]

    return Game.from_logic(database.create_game(owner=user, gamemode=gamemode))


# /games get список датакласів
# (Репрезентують гейм)
# (треба написати. Метод який з геймів Артура робить моїх (забирає датабейз)).

# return your games
@app.get("/games")
def get_games(jwt: str) -> list[Game]:
    """Get the games of the user

    Args:
        jwt (str): The JWT of the user

    Returns:
        list[Game]: The games of the user
    """
    user = id_and_user_from_jwt(jwt)[1]
    return [Game.from_logic(game) for game in user.games]


# /leaders_board get ретурнить список геймів
@app.get("/leaders_board")
def get_top_games() -> list[Game]:
    """Get the top games

    Returns:
        list[Game]: The top games
    """
    return [Game.from_logic(game) for game in database.get_leaderboard().top_n(15)]


# /games/{id гри} інфо про стан
# (з імпортованого викликаю get_game_state(id) з нього можу .мувз)
@app.get("/games/{game_id}")
def get_game_info(game_id: str) -> GameState:
    """Get the game state

    Args:
        game_id (str): The id of the game

    Returns:
        GameState: The game state
    """
    return GameState.from_logic(database.get_game_state(game_id))


# /games/{id гри} put викликаю get_game(id).claim(owner). Воно приймає жейсон веб ток
@app.put("/games/{game_id}")
def put_game(game_id: str, jwt: str) -> Game:
    """Claim a game

    Args:
        game_id (str): The id of the game
        jwt (str): The JWT of the user claiming the game

    Returns:
        Game: The claimed game
    """
    user = id_and_user_from_jwt(jwt)[1]

    game = database.get_game(game_id)
    game.claim(user)
    return Game.from_logic(game)


@app.post("/games/{game_id}/moves")
def post_move(game_id: str, move: Move, jwt: str) -> GameState:
    """Make a move

    Args:
        game_id (str): The id of the game
        move (Move): The move to make
        jwt (str): The JWT of the user making the move

    Raises:
        HTTPException: If the JWT is invalid
            or the user is not the owner of the game

    Returns:
        GameState: The game state after the move
    """
    user = id_and_user_from_jwt(jwt)[1]

    game = database.get_game(game_id)
    if game.owner != user:
        raise HTTPException(403, "You are not the owner of this game.")

    game.play_move(move)

    return GameState.from_logic(game.state)


# розібратися з імпортом дата
