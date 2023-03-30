"""A single move in a game of Cinasweeper."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Move:
    """A single move in a game of Cinasweeper."""

    x: int
    y: int
    action: int

