from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .database import Database

@dataclass
class User:
    id: str
    database: Database

    @property
    def games(self):
        return self.database.get_games(self)
