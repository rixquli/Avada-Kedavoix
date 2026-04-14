"""
Classe pour la gestion des murs
"""

import pygame
from client.classes.hitbox import HitBox
from client.layerList import Layer

from server.classes.serializable import Serializable


class Wall(Serializable, pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, world_layer: int | Layer = Layer.OVERWORLD):
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
        self.world_layer = (
            world_layer.value if isinstance(world_layer, Layer) else int(world_layer)
        )

    def server_update(self):
        pass

    def draw(self, surface: pygame.Surface, offset=(0, 0)):
        x = self.x + offset[0]
        y = self.y + offset[1]
        surface.blit(self.image, (x, y))

    @staticmethod
    def draw_all(
        surface,
        offset: tuple[float, float],
        walls: list["Wall"],
        active_world_layer: int | None = None,
    ):
        """
        Dessine tout les murs
        """
        if walls:
            if isinstance(walls, list):
                for wall in walls:
                    if (
                        active_world_layer is not None
                        and wall.world_layer != active_world_layer
                    ):
                        continue
                    wall.draw(surface, offset)
            else:
                walls.draw(surface, offset)
