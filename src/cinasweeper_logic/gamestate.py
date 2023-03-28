from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .database import Database

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
