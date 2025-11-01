from typing import List, Tuple

import pygame
from server.classes.serializable import Serializable


class Enemy(Serializable):
    def __init__(
        self,
        x: float,
        y: float,
        color: Tuple[int, int, int],
        size: int = 10,
        vx: float = 0,
        vy: float = 0,
        id: int = None,
    ):
        self.id = id
        self.color = tuple(color)
        self.size = int(size)

        # Vértable position envoyées au serveur
        self.x = float(x)
        self.y = float(y)

        # Pour gérer les mouvements stoque la vitesse
        self.vx = float(vx)
        self.vy = float(vy)

        # Position affiché
        self.display_x = float(x)
        self.display_y = float(y)

        # Pour l'interpolation
        self.target_x = float(x)
        self.target_y = float(y)
        self.interpolation_speed = 0.1

    def update(self):
        # TODO: Ajouter l'ia ici pour le comportement des créatures
        # Utiliser set_target_postion pour modifier la position de la créature

        # Interpolation vers la position cible
        # Permet d'eviter les mouvements sacadé
        self._interpolate_position()

    def _interpolate_position(self):
        """Interpolation du mouvement vers le point cible"""
        self.display_x += (self.target_x - self.display_x) * self.interpolation_speed
        self.display_y += (self.target_y - self.display_y) * self.interpolation_speed

    def draw(self, surface, offset: Tuple[float, float]):
        pygame.draw.rect(
            surface,
            self.color,
            pygame.Rect(
                self.display_x + offset[0],
                self.display_y + offset[1],
                self.size,
                self.size,
            ),
        )

    def set_target_position(self, x, y):
        """
        Applique une interpolation lors de l'application des positions recu du serveur
        permettant d'éviter des mouvements sacadés
        """
        self.target_x = float(x)
        self.target_y = float(y)

    @staticmethod
    def draw_all(surface, offset: Tuple[float, float], enemies: List["Enemy"]):
        """
        Dessine tout les ennemi
        """
        if enemies:
            if isinstance(enemies, list):
                for enemy in enemies:
                    enemy.draw(surface, offset)
            else:
                enemies.draw(surface, offset)
