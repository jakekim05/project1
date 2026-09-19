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
                    for di, dj in [(1, 0), (0, 1), (1, 1), (1, -1)]:
                        ni, nj = i, j
                        count = 1
                        while 0 <= ni + di < 19 and 0 <= nj + dj < 19 and self.board.board[ni + di][nj + dj] == color:
                            count += 1
                            ni += di
                            nj += dj
                        if count == 5:
                            return color
        return -1

    def end_game(self):
        winner = self.whos_win()
        if winner == 0:
            print("Black player wins!")
        elif winner == 1:
            print("White player wins!")
        else:
            print("The game is a draw.")
    