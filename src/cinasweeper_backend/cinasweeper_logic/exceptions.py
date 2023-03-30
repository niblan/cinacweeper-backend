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
