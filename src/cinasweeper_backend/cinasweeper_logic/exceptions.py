"""The base exception class for the cinasweeper_logic module."""


class GameEndedError(Exception):
    """The game already ended"""


class GameNotFoundError(Exception):
    """The game was not found"""

    def __init__(self, identifier: str) -> None:
        """Initializes the exception

        Args:
            identifier (str): The id of the game that was not found
        """
        super().__init__(f"Game with id {identifier} not found")


class GameNotStartedError(Exception):
    """The game was not started"""


class PlayingAgainstSelfError(Exception):
    """A player cannot play against himself in 1v1 mode."""


class CellAlreadyOpenError(Exception):
    """The ceil is open, you can't flaged it"""

