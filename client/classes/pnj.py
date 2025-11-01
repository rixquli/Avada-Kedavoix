from typing import List, Tuple

import pygame
from server.classes.serializable import Serializable


class PNJ(Serializable):
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
        # Dessine un losange (carré tourné de 45°) centré sur display_x/display_y + size/2
        cx = self.display_x + self.size / 2 + offset[0]
        cy = self.display_y + self.size / 2 + offset[1]
        half = self.size / 2
        points = [
            (int(cx), int(cy - half)),  # haut
            (int(cx + half), int(cy)),  # droite
            (int(cx), int(cy + half)),  # bas
            (int(cx - half), int(cy)),  # gauche
        ]
        pygame.draw.polygon(surface, self.color, points)

    def set_target_position(self, x, y):
        """
        Applique une interpolation lors de l'application des positions recu du serveur
        permettant d'éviter des mouvements sacadés
        """
        self.target_x = float(x)
        self.target_y = float(y)

    @staticmethod
    def draw_all(surface, offset: Tuple[float, float], pnjs: List["PNJ"]):
        """
        Dessine tout les pnj
        """
        if pnjs:
            if isinstance(pnjs, list):
                for pnj in pnjs:
                    pnj.draw(surface, offset)
            else:
                pnjs.draw(surface, offset)
