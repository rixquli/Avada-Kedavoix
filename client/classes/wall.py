"""
Classe pour la gestion des murs
"""

import pygame
from client.layerList import Layer
from client.Utils.ImageTool import ImageTool

from server.classes.serializable import Serializable


class Wall(Serializable, pygame.sprite.Sprite):
    def __init__(
        self,
        x,
        y,
        w,
        h,
        world_layer: int | Layer = Layer.OVERWORLD,
        texture_path: str | None = "client/ressources/Dungeon/wall_tile.png",
        tile_size: int | None = 320,
    ):
        super().__init__()
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.image = pygame.Surface((w, h))
        self.hitbox_size = (w, h)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.world_layer = (
            world_layer.value if isinstance(world_layer, Layer) else int(world_layer)
        )

        if texture_path is not None:
            self._tile_texture(texture_path, tile_size)
        else:
            self.image.fill((100, 100, 100))

    def _tile_texture(self, texture_path: str, tile_size: int | None):
        """
        Charge une texture et la répète en tuile pour remplir la surface du mur.
        Args:
            texture_path: chemin vers l'image de la tuile
            tile_size: taille en pixels du carré de tuile (None = taille originale)
        """
        tile = ImageTool.load(texture_path)
        if tile_size is not None:
            tile = ImageTool.scale(tile, (tile_size, tile_size))
        tw, th = tile.get_size()
        for row in range(0, self.h, th):
            for col in range(0, self.w, tw):
                self.image.blit(tile, (col, row))

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
