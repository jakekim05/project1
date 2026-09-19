from player import Player
from board import Board

class GameManager:
    def __init__(self, player1, player2):
        self.player = [player1, player2]
        self.whos_turn = 0
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
                        di = -di
                        dj = -dj
                        ni, nj = i, j
                        while 0 <= ni + di < self.board.size and 0 <= nj + dj < self.board.size\
                        and self.board.board[ni + di][nj + dj] == color:
                            count += 1
                            ni += di
                            nj += dj
                        if count == 5:
                            return color
        return -1

    def end_game(self):
        self.board.print_board()
        winner = self.whos_win()
        if winner == 0:
            print("Black player wins!")
        elif winner == 1:
            print("White player wins!")
        else:
            print("The game is a draw.")

    def start_turn(self, time):
        player = self.player[self.whos_turn]
        self.whos_turn ^= 1
        board = self.board
        print("Current Board:")
        board.print_board()
        
        move = player.take_turn(board.board, time)
        if move:
            if not board.valid_pos(*move) or board.board[move[0]][move[1]] != -1:
                assert False, "Invalid move. Please try again."
            i, j = move
            board.board[i][j] = player.color
            print(f"Player {'Black' if player.color == 0 else 'White'} placed at ({i}, {j})")
        else:
            print("No valid move made.")
        
        for di, dj in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]:
            a, b, c = 0, 0, 0
            ni, nj = i + 1*di, j + 1*dj
            if board.valid_pos(ni, nj) and board.board[ni][nj] == 1-player.color:
                a = 1
            ni, nj = i + 2*di, j + 2*dj
            if board.valid_pos(ni, nj) and board.board[ni][nj] == 1-player.color:
                b = 1
            ni, nj = i + 3*di, j + 3*dj
            if board.valid_pos(ni, nj) and board.board[ni][nj] == player.color:
                c = 1
            if a and b and c:
                board.board[i+1*di][j+1*dj] = board.board[i+2*di][j+2*dj] = -1
