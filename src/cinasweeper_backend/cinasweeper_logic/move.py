"""A single move in a game of Cinasweeper."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Move:
    """Represents a single move in a game of Cinasweeper.

    Attributes:
        x (int): The x-coordinate of the move.
        y (int): The y-coordinate of the move.
        action (int): The action taken for the move, where:
                        0 - Flag cell
                        1 - Reveal cell
    """
    x: int
    y: int
    action: int

