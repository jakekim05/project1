class Board:
    def __init__(self, size = 19):
        self.size = size
        self.board = [[-1 for _ in range(size)] for _ in range(size)]