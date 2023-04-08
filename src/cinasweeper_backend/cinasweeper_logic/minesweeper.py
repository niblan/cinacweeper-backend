"""
Functions for Cin-Cin Game.
"""
from __future__ import annotations

from random import randint
from sys import exit


# generate board with indexes and without mines.
def generate_board(height: int, width: int) -> list[list]:
    """
    Create a board.
    :param height: number of rows.
    :param width: number of columns.
    Return board.
    >>> len(generate_board(5, 4))
    5
    >>> len(generate_board(5, 4)[0])
    4
    """
    return [[(row, col) for col in range(width)] for row in range(height)]

    # set mines at the board.


def set_mines(height: int, width: int, num_mines: int, step: tuple[int, int]) -> list:
    """
    Set mines at the field ignoring step`s coordinates
    :param num_mines: number of mines.
    :param step: tuple with coordinates of the first step.
    :param height: number of rows.
    :param width: number of columns.
    Return list of mines` coordinates.
    >>> len(set_mines(8, 8, 10))
    10
    """
    mines: set[tuple[int, int]] = set()
    while len(mines) < num_mines:
        mines.add((randint(0, height - 1), randint(0, width - 1)))
        mines.discard(step)  # ignore the coordinates
    return list(mines)

    # number of mines around


def get_info_board(height: int, width: int, mines: list) -> list[list]:
    """
    Increase value of ceils around mines. Set -1 to the ceil with mine.
    :param mines: list of mines` coordinates.
    :param height: number of rows.
    :param width: number of columns.
    Return info board (number of mines around the ceil).
    >>> ceil_info_board(3, 3, [(0, 0), (1, 2), (2, 2)])
    [[-1, 2, 1], [1, 3, -1], [0, 2, -1]]
    """
    board = [
        [-1 if (ind_row, ind_col) in mines else 0 for ind_col in range(width)]
        for ind_row in range(height)
    ]
    for mine in mines:  # increase value around mines
        for y in range(-1, 2):
            if mine[0] + y >= 0 and mine[0] + y < len(board):
                for x in range(-1, 2):
                    if mine[1] + x >= 0 and mine[1] + x < len(board[0]):
                        if board[mine[0] + y][mine[1] + x] >= 0:
                            board[mine[0] + y][mine[1] + x] += 1
    return board


def flag(board: list[list], step: tuple) -> None:
    """
    Set or delete flag.
    :param board: board to change.
    :param step: ceil coordinates to mark.
    Return None.
    """
    if board[step[0]][step[1]] == "F":
        board[step[0]][step[1]] = step
    else:
        board[step[0]][step[1]] = "F"


def end_game(board: list[list], info_board: list[list]):
    height = len(board)
    width = len(board[0])
    board = [
        [
            -1 if info_board[i_row][i_ceil] == -1 else board[i_row][i_ceil]
            for i_ceil in range(width)
        ]
        for i_row in range(height)
    ]
    s = [[str(e) for e in row] for row in board]
    lens = [max(map(len, col)) for col in zip(*s)]
    fmt = "\t".join("{{:{}}}".format(x) for x in lens)
    table = [fmt.format(*row) for row in s]
    exit()  # GET TO THE MEIN PAGE

    # check ceil (if 0 then...)


def check_ceil(board: list[list], info_board: list[list], step: tuple, zeros):
    """
    Set a value to the ceil.
    Return None.
    """
    if not info_board[step[0]][step[1]]:  # if 0 open 0s around
        board[step[0]][step[1]] = 0
        zeros.append(step)  # mark the ceil like already checked
        for y in range(-1, 2):
            if step[0] + y >= 0 and step[0] + y < len(
                board
            ):  # the ceil is inside the board (Y)
                for x in range(-1, 2):
                    if step[1] + x >= 0 and step[1] + x < len(
                        board[0]
                    ):  # the ceil is inside the board (X)
                        #  not a mine                                    we did not check the ceil
                        if (
                            info_board[step[0] + y][step[1] + x] >= 0
                            and (step[0] + y, step[1] + x) not in zeros
                        ):
                            check_ceil(
                                board, info_board, (step[0] + y, step[1] + x), zeros
                            )  # recurseve check ceils around
    elif info_board[step[0]][step[1]] == -1:  # it is a mine
        return "LOST"
    else:  # neither 0 or mine
        board[step[0]][step[1]] = info_board[step[0]][
            step[1]
        ]  # show the value to the user


# CHECK IS IT INSIDE BOARD
def get_step(x, y) -> tuple:
    """Return suitable step."""
    return (max(0, x), max(0, y))


def check_win(
    board: list[list], info_board: list[list], mines: list[list[int]]
) -> bool:
    flags_on_mines = 0
    for x, row in enumerate(board):
        for y, ceil in enumerate(row):  # ceil in mines
            if ceil == "F" and [x, y] in mines:
                flags_on_mines += 1
    return flags_on_mines == len(mines)


def main(board, mines, info_board, zeros, action, coord: tuple[int, int]):
    if action:
        if check_ceil(board, info_board, get_step(coord[0], coord[1]), zeros) == "LOST":
            return "Lose"
    else:
        if isinstance(board[coord[0]][coord[1]], int):
            return "Open"
        flag(board, get_step(coord[0], coord[1]))
        if check_win(board, info_board, mines):
            return "Win"
