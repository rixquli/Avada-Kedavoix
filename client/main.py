"""
Script d'entré qui lance tout le reste nottament le GameManager
"""

import os
import sys
from _thread import *

# To import module from other folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from client.gameManager import GameManager

# Le game_manager est un singleton
# ce qui implique que dans tout le projet
# GameManager() renverra la meme instance qu'importe ou il est appele
game_manager = GameManager()


def main():
    game_manager.setup()

    while True:
        game_manager.render()


if __name__ == "__main__":
    main()
