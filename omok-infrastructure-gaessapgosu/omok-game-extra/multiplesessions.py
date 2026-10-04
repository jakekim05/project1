from gamemanager import GameManager
from humanplayer import HumanPlayer
from randomplayer import RandomPlayer
from simpleplayer import SimplePlayer

class MultipleSessions:
    def __init__(self):
        self.opponent_classes = [HumanPlayer, RandomPlayer, SimplePlayer]
        self.opponent_names = ["HumanPlayer", "RandomPlayer", "SimplePlayer"]
        
        self.wins = 0
        self.losses = 0
        self.draws = 0

    def run(self):
        print("=== Welcome to Omok++ Multiple Sessions (Extra Credit) ===")

        while True:
            print("\n------------------------------")
            print("Select your opponent from the list:")
            for idx, name in enumerate(self.opponent_names):
                print(f"  {idx}: {name}")
            
            #Select opponent
            opp_choice = self._get_valid_input("Enter opponent choice (0-2): ", len(self.opponent_names))
            opponent_cls = self.opponent_classes[opp_choice]

            #Choose whether human plays black or white
            print("\nChoose your turn order:")
            print("  0: Human plays First (Black)")
            print("  1: Human plays Second (White)")
            order_choice = self._get_valid_input("Enter order choice (0-1): ", 2)

            if order_choice == 0:
                human_color = 0
                player1 = HumanPlayer(0)
                player2 = opponent_cls(1)
            else:
                human_color = 1
                player1 = opponent_cls(0)
                player2 = HumanPlayer(1)

            # 3. Run the game session (no command-line params for players)[cite: 13]
            game = GameManager(player1, player2)
            while game.whos_win() == -1:
                game.start_turn(-1)
            
            game.end_game()

            winner = game.whos_win()
            if winner == human_color:
                print("You won this game!")
                self.wins += 1
            elif winner == -1:
                print("The game is a draw.")
                self.draws += 1
            else:
                print("You lost this game.")
                self.losses += 1

            print("\n==============================")
            print(f" SCOREBOARD -> Wins: {self.wins} | Losses: {self.losses} | Draws: {self.draws}")
            print("==============================")

            # 5. Play another game or exit[cite: 13]
            cont = ""
            while cont != "e" and cont != "c":
                cont = input("Type 'c' to play another game or 'e' to exit: ").strip().lower()
            
            if cont == "e":
                print("\nExiting Omok++. Final Records:")
                print(f"Wins: {self.wins} | Losses: {self.losses} | Draws: {self.draws}")
                break

    def _get_valid_input(self, prompt, max_val):
        while True:
            try:
                val = int(input(prompt))
                if 0 <= val < max_val:
                    return val
                print(f"Please enter a number between 0 and {max_val - 1}.")
            except ValueError:
                print("Invalid input. Please enter an integer.")