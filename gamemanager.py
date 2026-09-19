from player import Player
from board import Board

class GameManager:
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.board = Board()
    def whos_win(self):
        for i in range(19):
            for j in range(19):
                if self.board.board[i][j] != -1:
                    color = self.board.board[i][j]
                    count = 1
                    for di, dj in [(1, 0), (0, 1), (1, 1), (1, -1)]:
                        ni, nj = i, j
                        count = 1

    def end_game