import time as t

from player import Player
from randomplayer import RandomPlayer
from simpleplayer import SimplePlayer

SIZE = 19
EMPTY = -1

class HumanPlayer(Player):
    def __init__(self, color):
        super().__init__(color)
        self._prev_board = None

    def take_turn(self, board, time):
        x, y = map(int, input("Enter your move (row col): ").split())
        while board[x][y] != -1:
            print("Invalid move. Cell is already occupied.")
            x, y = map(int, input("Enter your move (row col): ").split())
        