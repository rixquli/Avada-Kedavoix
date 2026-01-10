"""
Classe pour la gestion des hitbox mais local
Elle permet de gérer seulement les collisions
Exemple: gestion des collision entre le joueur et les murs
"""

import pygame
from server.classes.serializable import Serializable


class HitBox(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, w: int, h: int, debug: bool = False):
        super().__init__()
        self.w = int(w)
        self.h = int(h)
        self.x = int(x)
        self.y = int(y)
        self.image = pygame.Surface((w, h))
        self.image.fill((0, 255, 0))
        self.rect = self.image.get_rect()
        self.rect.center = (int(x), int(y))

        self.debug = debug

        from client.gameManager import GameManager

        self.game_manager = GameManager()

        from server.NetworkManager import NetworkManager

        self.network = NetworkManager()

    def update(self, x: int, y: int):
        self.rect.center = (x, y)

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
        return pygame.sprite.spritecollide(
            self,
            self.game_manager.collision_manager.client_collider_groups.get("obstacle"),
            False,
        )

    def get_server_collided(self) -> bool:
        return pygame.sprite.spritecollide(
            self,
            self.network.game_state.collision_manager.client_collider_groups.get(
                "obstacle"
            ),
            False,
        )

    def collide(self, entity: Serializable) -> bool:
        if hasattr(entity, "rect"):
            return self.rect.colliderect(entity.rect)
        return self.rect.colliderect(entity.hitbox.rect)
