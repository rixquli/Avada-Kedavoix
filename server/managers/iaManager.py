#to manage an ia

import time
from random import randint
import math

from client.gameManager import GameManager
from client.classes.pnj import PNJ
from client.classes.enemy import Enemy
from server.ia.pathFinding import Path

class Ia:
    def __init__(
            self,
            ia_type: str,
            entity
    ):
        self.ia_type = ia_type
        self.entity = entity

    def update(self):
        dir_ia = [getattr(ListIa, method) for method in dir(ListIa) if
                  not method.startswith("_") and callable(getattr(ListIa, method))]
        for ia in dir_ia:
            if ia.__name__ == self.ia_type:
                ia(None, self.entity)

class BasicIaUtility:
    def __init__(self):
        pass

    @staticmethod
    def get_players_pos() -> list[tuple[float, float]]:
        """renvois les posistion de tous les joueurs"""
        players = GameManager().client_manager.game_state.players.get_all()
        pos = []
        for player in players:
            pos.append((players[player].display_x, players[player].display_y))
        return pos

    @staticmethod
    def get_pos_closest_player(x: float = 0.0, y: float = 0.0, dist_min: int = -1) -> tuple[float, float]:
        players_pos = BasicIaUtility.get_players_pos()
        if len(players_pos) != 0:
            player_pos = players_pos[0]
            for pos in players_pos:
                dist = (pos[0] - x) ** 2 + (pos[1] - y) ** 2
                if dist < dist_min or dist_min == -1:
                    dist_min = dist
                    player_pos = pos
            return player_pos
        return x,y

    @staticmethod
    def get_dist(x, y, x1, y1):
        return math.sqrt((x - x1) ** 2 + (y - y1) ** 2)


    @staticmethod
    def dir_target (x: float = 0.0, y: float = 0.0, dist_min: int = -1) -> tuple[float, float]:
        """renvois la direction du joueurs le plus proche"""
        pos0 = x
        pos1 = y
        for pos in BasicIaUtility.get_players_pos():
            dist = (pos[0]-x)**2 + (pos[1]-y)**2
            if dist < dist_min or dist_min == -1:
                dist_min = dist
                pos0 = pos[0]
                pos1 = pos[1]

        if dist_min == -1:
            return 0, 0
        dist_min = dist_min**0.5
        pos0 = (pos0 - x)/dist_min
        pos1 = (pos1 - y)/dist_min
        return pos0, pos1


class ListIa:
    def __init__(self):
        pass

    #@staticmethod
    def enemy_ia(self,enemy: Enemy) -> None:
        cible_pos = BasicIaUtility.get_pos_closest_player(enemy.x, enemy.y)
        if BasicIaUtility.get_dist(enemy.x, enemy.y, cible_pos[0], cible_pos[1]) < 20:
            enemy.vx, enemy.vy = BasicIaUtility.dir_target(enemy.x, enemy.y)
        else:
            if enemy.path is None:
                enemy.path = Path((int(enemy.x), int(enemy.y)), cible_pos, enemy.hitbox)
            elif len(enemy.path.path) == 0:
                enemy.path.update_pos(enemy.x, enemy.y)
                enemy.path.update_dest(cible_pos[0], cible_pos[1])
                enemy.path.find_path(enemy.vitesse, 5)
            print(enemy.path.path)
            enemy.vx,enemy.vy = enemy.path.follow_path()
        print(enemy.vx,enemy.vy)

        if time.time() - enemy.prec_attack_time > enemy.attack_delay:
            enemy.do_attack((enemy.vx, enemy.vy))
            enemy.prec_attack_time = time.time()

    #@staticmethod
    def pnj_ia(self, pnj: PNJ) -> None:
        if abs(pnj.x_target - pnj.x) < 1 and abs(pnj.y_target - pnj.y) < 1:
            pnj.x_target = randint(int(pnj.y - 100), int(pnj.x + 100))
            pnj.y_target = randint(int(pnj.y - 100), int(pnj.y + 100))
            pnj.dist = ((pnj.x_target - pnj.x) ** 2 + (pnj.y_target - pnj.y) ** 2) ** 0.5
            if pnj.dist == 0:
                pnj.vx = 0
                pnj.vy = 0
            else:
                pnj.vx = (pnj.x_target - pnj.x) / pnj.dist
                pnj.vy = (pnj.y_target - pnj.y) / pnj.dist


