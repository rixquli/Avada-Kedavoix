"""
Classe pour la gestion des spells (sorts)
"""

import time
from typing import List, Tuple
import pygame

from server.classes.serializable import Serializable
from client.classes.hitbox import HitBox


class Spell(Serializable):
    def __init__(
        self,
        x: float,
        y: float,
        player_id: int,
        color: Tuple[int, int, int],
        dir: Tuple[int, int],
        radius: int = 10,
        id: int = None,
        lifetime: float = 5.0,
        dmg: int = 1
    ):
        self.id = id
        self.x = float(x)
        self.y = float(y)
        self.player_id = player_id
        self.color = tuple(color)
        self.dir = tuple(dir)
        self.radius = int(radius)
        self.lifetime = float(lifetime)
        self.creation_time = time.time()

        # Position affiché
        self.display_x = float(x)
        self.display_y = float(y)

        # Pour l'interpolation
        self.target_x = float(x)
        self.target_y = float(y)
        self.interpolation_speed = 0.1
        self.min_threshold = 0.01

        self.hitbox_size = (10, 10)
        self.hitbox = HitBox(x, y, self.hitbox_size[0], self.hitbox_size[1])


        # Pour gerer le systeme vie/degat
        self.dmg = int(dmg)

    def interpolate_position(self):
        """Interpolation du mouvement vers le point cible"""
        x_diff = self.target_x - self.display_x
        y_diff = self.target_y - self.display_y

        if abs(x_diff) > self.min_threshold:
            self.display_x += x_diff * self.interpolation_speed
        else:
            self.display_x = self.target_x
        if abs(y_diff) > self.min_threshold:
            self.display_y += y_diff * self.interpolation_speed
        else:
            self.display_y = self.target_y

    def set_target_position(self, x, y):
        """
        Applique une interpolation lors de l'application des positions recu du serveur
        permettant d'éviter des mouvements sacadés
        """
        self.target_x = float(x)
        self.target_y = float(y)

    def server_update(self):
        self.x += self.dir[0]
        self.y += self.dir[1]

        self.hitbox.update(self.x, self.y)

    def is_expired(self) -> bool:
        """Verifie si le sort a depasse sa duree de vie"""
        return time.time() - self.creation_time > self.lifetime

    def draw(self, surface, offset: Tuple[float, float]):
        # Interpolation vers la position cible
        # Permet d'eviter les mouvements sacadé
        self.interpolate_position()

        pygame.draw.circle(
            surface,
            self.color,
            (int(self.display_x + offset[0]), int(self.display_y + offset[1])),
            self.radius,
        )

    @staticmethod
    def draw_all(surface, offset: Tuple[float, float], all_spells: List["Spell"]):
        """
        Dessine tout les spells
        """
        if all_spells:
            if isinstance(all_spells, list):
                for spell in all_spells:
                    spell.draw(surface, offset)
            else:
                all_spells.draw(surface, offset)
