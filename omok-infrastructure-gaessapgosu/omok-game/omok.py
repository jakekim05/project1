from gamemanager import GameManager
from humanplayer import HumanPlayer
from randomplayer import RandomPlayer
from simpleplayer import SimplePlayer

import sys
argv = sys.argv
mkp = [HumanPlayer, RandomPlayer, SimplePlayer]

game = GameManager(mkp[int(argv[1])](0), mkp[int(argv[2])](1), argv[3],)
while game.whos_win() == -1:
    game.start_turn()
game.end_game()
