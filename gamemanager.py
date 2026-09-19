from player import Player
from board import Board

class GameManager:
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.board = Board()
    def whos_win(self):
        for i in range(self.board.size):
            for j in range(self.board.size):
                if self.board.board[i][j] != -1:
                    color = self.board.board[i][j]
                    for di, dj in [(1, 0), (0, 1), (1, 1), (1, -1)]:
                        ni, nj = i, j
                        count = 1
                        while 0 <= ni + di < self.board.size and 0 <= nj + dj < self.board.size\
                        and self.board.board[ni + di][nj + dj] == color:
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

    def start_turn(self, player, time):
        move = player.take_turn(self.board.board, time)
        if move:
            row, col = move
            self.board.board[row][col] = player.color
            print(f"Player {'Black' if player.color == 0 else 'White'} placed at ({row}, {col})")
        else:
            print("No valid move made.")