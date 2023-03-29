from typing import Union
from dataclasses import dataclass

# фром .сіна_дейтабез імпорт датабейз
from ..cinasweeper_database import Database
from ..cinasweeper_logic import User, Move, Game, GameMod # {перелік класів}

from .authentication import AuthManager

from fastapi import FastAPI, WebSocket, HTTPException
from pydantic import BaseModel
import time

app = FastAPI()
database = Database(...)
manager = AuthManager()

def id_and_user_from_jwt(jwt: str):
    user_id = manager.verify(jwt)
    if not user_id:
        raise HTTPException(404, "User not found.")

    return user_id, User(user_id=user_id, database=database)

# /games post (приймає жейсон веб ток) створюємо гру датабаза.create_game() повертає гейм.
@app.post("/games", response_model=Game)
def create_game(jwt: str, gamemode: GameMode):
    user_id, user = id_and_user_from_jwt(jwt)[0]

    return database.create_game(
        owner=user, gamemode=gamemode
    )

# /games get список датакласів ( Репрезентують гейм (треба написати. Метод який з геймів Артура робить моїх (забирає датабейз)) ).
@dataclass
class Game:
    id: str
    owner: str | None
    started: bool
    started_time: datetime.datetime
    game_mode: GameMode

    @classmethod
    def from_logic(cls, game):
        return Game(game.id, game.owner and manager.get_user(game.owner), game.started, \
                    game.started_time, game.game_mode)

# return your games
@app.get("/games")
def get_games(jwt: str):
    user = id_and_user_from_jwt(jwt)[1]
    return [Game.from_logic(game) for game in user.games]

# /leaders_board get ретурнить список геймів
@app.get("/leaders_board")
def get_top_games():
    return [Game.from_logic(game) for game in database.get_leaderboard().top_n(15)]

# /games/{id гри} інфо про стан (з імпортованого викликаю get_game_state(id) з нього можу .мувз)
@app.get("/games/{game_id}")
def get_game_info(game_id: str):
    return database.get_game_state(game_id)

# /games/{id гри} put викликаю get_game(id).claim(owner). Воно приймає жейсон веб ток
@app.put("/games/{game_id}")
def put_game(game_id: str, jwt: str):
    user = id_and_user_from_jwt(jwt)[1]

    database.get_game(game_id).claim(user)

@app.post("/games/{game_id}/moves")
def post_move(game_id: str, action: int, x: int, y: int):
    database.get_game(game_id).play_move(Move(x=x, y=y, action=action))

# розібратися з імпортом дата
