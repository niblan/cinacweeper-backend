from __future__ import annotations
from dataclasses import dataclass
from .database import Database

@dataclass
class User:
    id: str
    database: Database

    @property
    def games(self):
        return self.database.get_games(self)
