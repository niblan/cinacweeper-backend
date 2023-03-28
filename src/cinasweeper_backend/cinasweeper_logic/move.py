from __future__ import annotations
from dataclasses import dataclass

@dataclass
class Move:
    x: int
    y: int
    action: int