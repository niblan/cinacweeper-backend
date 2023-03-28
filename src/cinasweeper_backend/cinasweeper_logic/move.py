from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .database import Database

@dataclass
class Move:
    """інфа про намір людини"""
    pass
