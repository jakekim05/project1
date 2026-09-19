from gamemanager import GameManager
from humanplayer import HumanPlayer
from randomplayer import RandomPlayer
from simpleplayer import SimplePlayer
from smartplayergaessapgosu import SmartPlayerGaeSsapGosu
from godplayernemesis import RealGosu

import sys
argv = sys.argv
mkp = [HumanPlayer, RandomPlayer, SimplePlayer, SmartPlayerGaeSsapGosu, RealGosu]

game = GameManager(mkp[int(argv[1])](0), mkp[int(argv[2])](1))
while game.whos_win() == -1:
    game.start_turn(-1)
game.end_game()