from gamemanager import GameManager
from humanplayer import HumanPlayer
from randomplayer import RandomPlayer
from simpleplayer import SimplePlayer
from smartplayergaessapgosu import SmartPlayerGaeSsapGosu

import sys
argv = sys.argv
mkp = [HumanPlayer, RandomPlayer, SimplePlayer, SmartPlayerGaeSsapGosu]

# Timer-related changes in this file were written with help from OpenAI Codex.

def main():
    if len(sys.argv) != 4:
        print("Usage: python omok.py [player-1] [player-2] [time-limit]")
        return

    try:
        player1_number = int(sys.argv[1])
        player2_number = int(sys.argv[2])
        time_limit = int(sys.argv[3])
    except ValueError:
        print("The player numbers and time limit must be integers.")
        return

    player_types = [HumanPlayer, RandomPlayer, SimplePlayer]

    if player1_number not in range(len(player_types)) or player2_number not in range(len(player_types)):
        print("Player number must be 0, 1, or 2.")
        return

    if time_limit < -1:
        print("Time limit must be -1 or a non-negative number of minutes.")
        return

    player1 = player_types[player1_number](0)
    player2 = player_types[player2_number](1)
    game = GameManager(player1, player2, time_limit)

    while game.whos_win() == -1:
        game.start_turn()

    game.end_game()


if __name__ == "__main__":
    main()
