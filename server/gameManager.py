import os
import sys

# To import module from other folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from server.managers.playersManager import PlayersManager


class GameManager:
    def __init__(self):
        self.playersManager = PlayersManager()

    def get_game_state(self):
        """Retourne l'état complet du jeu pour le broadcast"""
        return {
            "players": {
                pid: {
                    "x": p.x,
                    "y": p.y,
                    "color": p.color,
                    "radius": p.radius,
                    "vx": p.vx,
                    "vy": p.vy,
                }
                for pid, p in self.playersManager.players.items()
            }
        }
