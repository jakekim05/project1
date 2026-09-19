from player import Player
from board import Board
import time

# The timer code in this class was written with help from OpenAI Codex.

class GameManager:
    def __init__(self, player1, player2, time_limit=-1):
        self.player = [player1, player2]
        self.whos_turn = 0
        self.board = Board()
        self.time_winner = -1
        self.timed_out_player = -1

        if time_limit == -1:
            self.remaining_time = [-1, -1]
        else:
            time_in_ms = time_limit * 60 * 1000
            self.remaining_time = [time_in_ms, time_in_ms]
    
    def whos_win(self):
        if self.time_winner != -1:
            return self.time_winner

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

        if self.timed_out_player != -1:
            loser = "Black" if self.timed_out_player == 0 else "White"
            winner_name = "White" if self.timed_out_player == 0 else "Black"
            print(f"{loser} player ran out of time.")
            print(f"{winner_name} player wins!")
        elif winner == 0:
            print("Black player wins!")
        elif winner == 1:
            print("White player wins!")
        else:
            print("The game is a draw.")

    def start_turn(self):
        player_number = self.whos_turn
        player = self.player[player_number]
        board = self.board
        print("Current Board:")
        board.print_board()

        player_time = self.remaining_time[player_number]
        start_time = time.time()
        move = player.take_turn(board.board, int(player_time))
        end_time = time.time()

        if player_time != -1:
            used_time = (end_time - start_time) * 1000
            self.remaining_time[player_number] -= used_time

            if self.remaining_time[player_number] <= 0:
                self.remaining_time[player_number] = 0
                self.timed_out_player = player_number
                self.time_winner = 1 - player_number
                return

        if not move:
            raise ValueError("The player did not return a move.")

        if not board.valid_pos(*move) or board.board[move[0]][move[1]] != -1:
            raise ValueError("The player returned an invalid move.")

        i, j = move
        board.board[i][j] = player.color
        print(f"Player {'Black' if player.color == 0 else 'White'} placed at ({i}, {j})")
        
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

        self.whos_turn ^= 1
