"""
Classe pour la gestion des murs
"""

from typing import List, Tuple
import pygame
from client.classes.hitbox import HitBox

from server.classes.serializable import Serializable


class Wall(Serializable, pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super().__init__()
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.image = pygame.Surface((w, h))
        self.hitbox_size = (w, h)
        self.image.fill((100, 100, 100))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)


    def server_update(self):
        pass

    def draw(self, surface: pygame.Surface, offset=(0, 0)):
        x = self.x + offset[0]
        y = self.y + offset[1]
        surface.blit(self.image, (x, y))

    @staticmethod
    def draw_all(surface, offset: Tuple[float, float], walls: List["Wall"]):
        """
        Dessine tout les murs
        """
        if walls:
            if isinstance(walls, list):
                for wall in walls:
                    wall.draw(surface, offset)
            else:
                walls.draw(surface, offset)
