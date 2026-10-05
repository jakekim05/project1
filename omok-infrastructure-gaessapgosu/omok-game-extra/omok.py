from gamemanager import GameManager
from humanplayer import HumanPlayer
from randomplayer import RandomPlayer
from simpleplayer import SimplePlayer
from multiplesessions import MultipleSessions

mkp = [HumanPlayer, RandomPlayer, SimplePlayer]

game = GameManager(mkp[0](0), mkp[2](1))
while game.whos_win() == -1:
    game.start_turn(-1)
game.end_game()

def main():
    manager = MultipleSessions()
    manager.run()

if __name__ == "__main__":
    main()