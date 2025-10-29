import os
import sys
from typing import Tuple

# To import module from other folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from client.classes.player import Player


class PlayersManager:
    def __init__(self):
        self.players = {}
        self.counter = 0

    def addPlayer(
        self,
        x: float,
        y: float,
        color: Tuple[int, int, int],
        radius: int = 10,
        vx: float = 0,
        vy: float = 0,
    ):
        id = self.getId()
        self.players[id] = Player(x, y, color, radius, vx, vy)
        return id

    def removePlayer(self, id: int):
        if id in self.players:
            del self.players[id]

    def getId(self):
        id = self.counter
        self.counter += 1
        return id

    def getPlayer(self, id):
        return self.players[id]

    def updatePlayer(self, player_id, player_data):
        self.players[player_id] = player_data

    def getOtherPlayers(self, player_id):
        """Renvoie la liste des autres joueurs"""
        return [p for pid, p in self.players.items() if pid != player_id]
