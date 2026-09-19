from gamemanager import GameManager
from humanplayer import HumanPlayer
from randomplayer import RandomPlayer
from simpleplayer import SimplePlayer
from smartplayergaessapgosu import SmartPlayerGaeSsapGosu

def main():
    mkp = [HumanPlayer, RandomPlayer, SimplePlayer, SmartPlayerGaeSsapGosu]
    
    wins = 0
    losses = 0
    draws = 0

    print("=== Welcome to Omok++ Multiple Sessions ===")

    while True:
        print("\nSelect your opponent:")
        print("  0: HumanPlayer")
        print("  1: RandomPlayer")
        print("  2: SimplePlayer")
        
        try:
            opp_choice = int(input("Enter opponent number (0-2): "))
            if opp_choice not in [0, 1, 2]:
                print("Invalid selection. Please choose 0, 1, or 2.")
                continue
        except ValueError:
            print("Invalid input. Please enter an integer.")
            continue

        player1 = mkp[0](0)
        player2 = mkp[opp_choice](1)

        game = GameManager(player1, player2)
        while game.whos_win() == -1:
            game.start_turn(-1)
        
        game.end_game()
        
        winner = game.whos_win()
        if winner == 0:
            wins += 1
        elif winner == 1:
            losses += 1
        else:
            draws += 1

        print("\n==============================")
        print(f" SCOREBOARD -> Wins: {wins} | Losses: {losses} | Draws: {draws}")
        print("==============================")

        cont = ""
        while cont != "e" and cont != "c":
            cont = input("Type 'c' to play another game or 'e' to exit: ").strip().lower()
        
        if cont == "e":
            print("\nExiting Omok++. Final Records:")
            print(f"Wins: {wins} | Losses: {losses} | Draws: {draws}")
            break

if __name__ == "__main__":
    main()