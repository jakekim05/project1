from player import Player

SIZE = 19
EMPTY = -1

class HumanPlayer(Player):
    def __init__(self, color):
        super().__init__(color)
        self._prev_board = None

    def take_turn(self, board, time):
        print(f"[{'Black' if self.color == 0 else 'White'} Player's Turn]")
        print(f"Time remaining: {time / 1000.0:.2f} seconds ({time} ms)")

        while True:
            try:
                #Get user input in format n,m
                user_input = input("Enter your move (format: row,col e.g. 3,4): ").strip()
                
                parts = user_input.split(",")
                if len(parts) != 2:
                    print("Invalid format. Please use n,m with no spaces.")
                    continue
                
                row = int(parts[0].strip())
                col = int(parts[1].strip())

                #Validate boundaries and empty position
                if not (0 <= row < SIZE and 0 <= col < SIZE):
                    print(f"Out of bounds! Coordinates must be between 0 and {SIZE - 1}.")
                    continue
                
                if board[row][col] != EMPTY:
                    print("That position is already occupied. Choose an empty spot.")
                    continue

                # Valid move found
                return (row, col)

            except ValueError:
                print("Invalid input. Please enter numbers separated by a comma (e.g., 3,4).")
