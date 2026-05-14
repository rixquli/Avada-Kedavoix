"""
Classe pour la gestion des hitbox mais local
Elle permet de gérer seulement les collisions
Exemple: gestion des collision entre le joueur et les murs
"""

import pygame
from client.layerList import Layer
from server.classes.serializable import Serializable


class HitBox(pygame.sprite.Sprite):
    def __init__(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        world_layer: int | Layer = Layer.OVERWORLD,
        debug: bool = False,
    ):
        super().__init__()
        self.w = int(w)
        self.h = int(h)
        self.x = int(x)
        self.y = int(y)
        self.image = pygame.Surface((w, h))
        self.image.fill((0, 255, 0))
        self.rect = self.image.get_rect()
        self.rect.center = (int(x), int(y))
        self.world_layer = world_layer

        self.debug = debug

        from client.gameManager import GameManager

        self.game_manager = GameManager()

        from server.NetworkManager import NetworkManager

        self.network = NetworkManager()

    def update(self, x: int, y: int, world_layer: int | Layer = Layer.OVERWORLD):
        self.x = int(x)
        self.y = int(y)
        self.rect.center = (x, y)
        self.world_layer = world_layer

    def draw(self, surface, offset=(0, 0)):
        if self.debug:
            # Dessiner le rectangle de la hitbox en vert
            pygame.draw.rect(
                surface,
                (0, 255, 0),  # Vert
                (self.rect.x + offset[0], self.rect.y + offset[1], self.w, self.h),
                2,  # Épaisseur du contour (2 pixels)
            )

    def get_local_collided(self) -> bool:
        obstacles = self.game_manager.collision_manager.client_collider_groups.get(
            "obstacle"
        )
        if obstacles is None:
            return False

        filtered = [o for o in obstacles if o.world_layer == self.world_layer]
        return pygame.sprite.spritecollide(
            self,
            filtered,
            False,
        )

    def get_server_collided(self) -> bool:
        obstacles = (
            self.network.game_state.collision_manager.client_collider_groups.get(
                "obstacle"
            )
        )
        if obstacles is None:
            return False

        filtered = [o for o in obstacles if o.world_layer == self.world_layer]
        return pygame.sprite.spritecollide(
            self,
            filtered,
            False,
        )

    def collide(self, entity: Serializable) -> bool:
        if (
            not self.world_layer
            or not entity.world_layer
            or entity.world_layer != self.world_layer
        ):
            return False

        if hasattr(entity, "rect"):
            return self.rect.colliderect(entity.rect)
        return self.rect.colliderect(entity.hitbox.rect)
