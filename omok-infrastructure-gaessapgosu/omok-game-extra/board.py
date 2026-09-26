from gui import gui

class Board:
    def __init__(self, size = 19):
        self.size = size
        self.board = [[-1 for _ in range(size)] for _ in range(size)]
        self.stone = [[None for _ in range(size)] for _ in range(size)]

    def valid_pos(self, row, col):
        return 0 <= row < self.size and 0 <= col < self.size

    def put_stone(self, row, col, color):
        if self.valid_pos(row, col) and self.board[row][col] == -1:
            self.board[row][col] = color
            self.stone[row][col] = gui.draw_stone(row, col, color)
            return True
        return False

    def delete_stone(self, row, col):
        if self.valid_pos(row, col) and self.board[row][col] != -1:
            self.board[row][col] = -1
            if self.stone[row][col] is not None:
                gui.canvas.delete(self.stone[row][col])
                self.stone[row][col] = None
            return True
        return False

    def print_board(self):
        print("  " + " ".join(f"{i:2}" for i in range(self.size)))
        for i, row in enumerate(self.board):
            print(f"{i:2} " + "  ".join('B' if cell == 0 else 'W' if cell == 1 else '.' for cell in row))
            print()