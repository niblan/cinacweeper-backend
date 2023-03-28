from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING
import datetime
from .user import User
from .gamemode import GameMode
from .database import Database
from .move import Move
from .minesweeper import main
from .exceptions import GameIsEnded

if TYPE_CHECKING:
    from .gamestate import GameState

@dataclass
class Game:
    id: str
    owner: User | None
    started: bool
    started_time: datetime.datetime
    game_mode: GameMode
    database: Database
    ended = False
    opponent_id: str | None
    score: int

    @property
    def state(self) -> GameState:
        return self.database.get_game_state(self.id)

    def play_move(self, move: Move):
        if self.ended:
            raise GameIsEnded
        game_move = main(self.state.gameboard, self.state.mines, self.state.game_info, move.action, (move.x, move.y))
        if game_move == 'Win' or game_move == 'Lose':
            self.ended = True
        return self.database.save_game_state(self.id, self.state)

    def claim(self, user: User) -> None:
        """при відсутності гравця присвоїти собі гру"""
        if self.owner is None:
            self.owner = user
        self.database.save_game(self)
