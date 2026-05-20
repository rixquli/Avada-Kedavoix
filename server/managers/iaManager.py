"""
to manage ias
"""

import time
from random import randint
import math

from client.classes.pnj import PNJ
from client.classes.enemy import Enemy
from server.NetworkManager import NetworkManager
from server.ia.pathFinding import Path


class Ia:
    """
    classe pour enregistrer les ia dans les entiteesç
    executer self.ia.update() pour appliquer des mouvementset actualiser l'ia
    """

    def __init__(self, ia_type: str, entity):
        self.ia_type = ia_type
        self.entity = entity

    def update(self):
        dir_ia = [
            getattr(ListIa, method)
            for method in dir(ListIa)
            if not method.startswith("_") and callable(getattr(ListIa, method))
        ]
        for ia in dir_ia:
            if ia.__name__ == self.ia_type:
                ia(self.entity)


class BasicIaUtility:
    """banque de methode pour calculs de donnees utiles"""

    def __init__(self):
        pass

    @staticmethod
    def get_players_pos(world_layer: int | None = None) -> list[tuple[float, float]]:
        """renvois les posistion de tous les joueurs"""
        players = NetworkManager().game_state.players.get_all()
        pos = []
        for player in players:
            current_player = players[player]
            if (
                world_layer is not None
                and hasattr(current_player, "world_layer")
                and current_player.world_layer != world_layer
            ):
                continue
            pos.append((current_player.display_x, current_player.display_y))
        return pos

    @staticmethod
    def get_pos_closest_player(
        x: float = 0.0,
        y: float = 0.0,
        dist_min: int = -1,
        world_layer: int | None = None,
    ) -> tuple[float, float] | None:

        players_pos = BasicIaUtility.get_players_pos(world_layer=world_layer)
        if len(players_pos) != 0:
            player_pos = (x, y)
            for pos in players_pos:
                dist = ((pos[0] - x) ** 2 + (pos[1] - y) ** 2) ** 0.5
                if dist < dist_min or dist_min == -1:
                    dist_min = dist
                    player_pos = pos
            return player_pos
        return None

    @staticmethod
    def get_dist(x: float, y: float, x1: float, y1: float) -> float:
        return math.sqrt((x - x1) ** 2 + (y - y1) ** 2)

    @staticmethod
    def dir_target(
        x: float = 0.0,
        y: float = 0.0,
        dist_min: int = -1,
        world_layer: int | None = None,
    ) -> tuple[float, float]:
        """renvois la direction du joueurs le plus proche"""
        pos0 = x
        pos1 = y
        for pos in BasicIaUtility.get_players_pos(world_layer=world_layer):
            dist = (pos[0] - x) ** 2 + (pos[1] - y) ** 2
            if dist < dist_min or dist_min == -1:
                dist_min = dist
                pos0 = pos[0]
                pos1 = pos[1]

        if dist_min == -1:
            return 0, 0
        dist_min = dist_min**0.5
        pos0 = (pos0 - x) / dist_min
        pos1 = (pos1 - y) / dist_min

        return pos0, pos1

    @staticmethod
    def is_dest_reached(x, y, dest_x, dest_y, precision):
        return abs(dest_x - x) <= precision and abs(dest_y - y) < precision


class ListIa:
    """
    stockes les ia associees aux entitees (nom du type: entity_name+"_ia")
    rajouter dans l'entitee ce meme nom avec self.ia_type"""

    def __init__(self):
        pass

    @staticmethod
    def enemy_ia(enemy: Enemy) -> None:
        """ia des ennemis: target = joueur le plus proche, chemin = path finding"""
        search_len = 20
        cible_pos = BasicIaUtility.get_pos_closest_player(
            enemy.x, enemy.y, enemy.reach, world_layer=enemy.world_layer
        )
        if enemy.next_pos_vect[0] <= 0 or enemy.next_pos_vect[1] <= 0:
            if cible_pos is None:
                enemy.vx = 0
                enemy.vy = 0
                enemy.path = []
                return

            if (
                BasicIaUtility.get_dist(enemy.x, enemy.y, cible_pos[0], cible_pos[1])
                <= enemy.dist_from
            ):
                dx, dy = (0, 0)

            else:
                if enemy.path_finder is None:
                    enemy.path_finder = Path(
                        (int(enemy.x), int(enemy.y)),
                        cible_pos,
                        enemy.hitbox,
                        enemy.world_layer,
                        enemy.vitesse * 10,
                    )
                elif len(enemy.path) <= search_len - 10:
                    enemy.path_finder.update_dest(cible_pos[0], cible_pos[1])
                    enemy.path_finder.update_pos(enemy.x, enemy.y)
                    enemy.path = enemy.path_finder.find_path(search_len)
                dx, dy = Path.follow_path(enemy.path, (enemy.x, enemy.y))
            sx, sy = 1, 1
            if dx < 0:
                dx = -dx
                sx = -1
            if dy < 0:
                dy = -dy
                sy = -1
            enemy.next_pos_vect = (dx, dy)
            enemy.next_pos_sign = (sx, sy)
        d = (enemy.next_pos_vect[0] ** 2 + enemy.next_pos_vect[1] ** 2) ** 0.5
        if d == 0:
            enemy.vx, enemy.vy = (0, 0)
        else:
            enemy.vx = (
                enemy.next_pos_vect[0] / d * enemy.vitesse * 5 * enemy.next_pos_sign[0]
            )
            enemy.vy = (
                enemy.next_pos_vect[1] / d * enemy.vitesse * 5 * enemy.next_pos_sign[1]
            )
            vect_x = enemy.next_pos_vect[0] - abs(enemy.vx)
            vect_y = enemy.next_pos_vect[1] - abs(enemy.vy)
            enemy.next_pos_vect = (vect_x, vect_y)

        if time.time() - enemy.prec_attack_time > enemy.attack_delay:
            attack_dir = BasicIaUtility.dir_target(
                enemy.x, enemy.y, world_layer=enemy.world_layer
            )
            if attack_dir != (0, 0):
                enemy.do_attack(attack_dir)
                enemy.prec_attack_time = time.time()

    @staticmethod
    def pnj_ia(pnj: PNJ) -> None:
        """ia des pnj: deplacement aleatoires (wandering)"""
        if BasicIaUtility.is_dest_reached(pnj.x, pnj.y, pnj.target_x, pnj.target_y, 1):
            pnj.x_target = randint(int(pnj.x - 100), int(pnj.x + 100))
            pnj.y_target = randint(int(pnj.y - 100), int(pnj.y + 100))
            pnj.dist = (
                (pnj.x_target - pnj.x) ** 2 + (pnj.y_target - pnj.y) ** 2
            ) ** 0.5
            if pnj.dist == 0:
                pnj.vx = 0
                pnj.vy = 0
            else:
                pnj.vx = (pnj.x_target - pnj.x) / pnj.dist
                pnj.vy = (pnj.y_target - pnj.y) / pnj.dist
