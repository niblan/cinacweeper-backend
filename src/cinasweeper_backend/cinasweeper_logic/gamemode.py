"""The gamemode

Currently only two are supported: singleplayer and 1v1
"""
from __future__ import annotations

from enum import Enum


class GameMode(Enum):
    """The gamemode"""

    ONE_V_ONE = "1v1"
    SINGLEPLAYER = "singleplayer"

