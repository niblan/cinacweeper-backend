from dataclasses import dataclass
from typing import TYPE_CHECKING
from enum import Enum
import datetime

if TYPE_CHECKING:
    from logic import Database


@dataclass
class User:
    id: str
    database: Database

    @property
    def games(self):
        return self.database.get_games(self)

@dataclass
class Move:
    """інфа про намір людини"""

    pass


class GameMode(Enum):
    ONE_V_ONE = "1v1"
    SINGLEPLAYER = "singleplayer"


@dataclass
class GameState:
    ended: bool
    database: Database

    @property
    def moves(self) -> tuple[Move]:
        ...

    def play_move(self, move: Move) -> None:
        # Raises all the relevant exceptions
        pass

    @property
    def is_over(self) -> bool:
        ...


@dataclass
class Game:
    id: str
    owner: User | None
    started: bool
    started_time: datetime.datetime
    game_mode: GameMode
    database: Database
    score: int

    @property
    def state(self) -> GameState:
        return self.database.get_game_state(self.id)

    def play_move(self, move: Move) -> GameState:
        # Adds more exception raises depending on the gamemode
        #save to database
        pass

    def claim(self, user: User) -> None:
        """при відсутності гравця присвоїти собі гру"""
        if self.owner is None:
            self.owner = user
        self.database.save_game(self)


@dataclass
class Leaderboard:
    database: Database

    def top_n(self, n: int = 10) -> tuple[Game]:
        #return from database
        ...
    