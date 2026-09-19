class Board:
    def __init__(self, size = 19):
        self.size = size
        self.board = [[-1 for _ in range(size)] for _ in range(size)]

    def valid_pos(self, row, col):
        return 0 <= row < self.size and 0 <= col < self.size
    
    def print_board(self):
        print("  " + " ".join(f"{i:2}" for i in range(self.size)))
        for i, row in enumerate(self.board):
            print(f"{i:2} " + "  ".join('B' if cell == 0 else 'W' if cell == 1 else '.' for cell in row))
            print()