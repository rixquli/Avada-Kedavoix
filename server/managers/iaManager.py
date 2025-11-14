import time
from random import randint

from client.gameManager import GameManager
from client.classes.pnj import PNJ
from client.classes.enemy import Enemy

class IaManager():
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

class BasicIaUtility():
    def __init__(self):
        pass

    def get_players_pos(self) -> list[tuple[float, float]]:
        """renvois les posistion de tous les joueurs"""
        players = GameManager().client_manager.game_state.players.get_all()
        pos = []
        for player in players:
            pos.append((players[player].display_x, players[player].display_y))
        return pos

    def dir_target (self, x: float = 0.0, y: float = 0.0) -> tuple[float, float]:
        """renvois la direction du joueurs le plus proche"""
        dist_min = 1000000000000
        pos0 = x
        pos1 = y
        for pos in self.get_players_pos():
            dist = (pos[0]-x)**2 + (pos[1]-y)**2
            if dist < dist_min:
                dist_min = dist
                pos0 = pos[0]
                pos1 = pos[1]
        dist_min = dist_min**0.5
        pos0 = (pos0 - x)/dist_min
        pos1 = (pos1 - y)/dist_min
        return pos0, pos1


class ListIa():
    def __init__(self):
        pass

    def enemy_ia(self, enemy: Enemy) -> None:
        enemy.vx,enemy.vy = BasicIaUtility().dir_target(enemy.x, enemy.y)

        if time.time() - enemy.prec_attack_time > enemy.attack_delay:
            enemy.do_attack((enemy.vx, enemy.vy))
            enemy.prec_attack_time = time.time()

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


