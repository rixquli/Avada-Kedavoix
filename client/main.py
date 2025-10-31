import os
import sys
from _thread import *


# To import module from other folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from client.gameManager import GameManager

game_manager = GameManager()


def main():
    while True:
        game_manager.render()


if __name__ == "__main__":
    main()
