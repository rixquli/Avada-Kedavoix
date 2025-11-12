"""
Classe pour la gestion des hitbox mais local
Elle permet de gérer seulement les collisions
Exemple: gestion des collision entre le joueur et les murs
"""

import pygame


class HitBox(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, debug=False):
        super().__init__()
        self.w = w
        self.h = h
        self.x = x
        self.y = y
        self.image = pygame.Surface((w, h))
        self.image.fill((0, 255, 0))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        self.debug = debug

        from client.gameManager import GameManager

        self.game_manager = GameManager()

    def update(self, x, y):
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

    def get_collided(self):
        """
        return pygame.sprite.spritecollide(
            self, self.game_manager.groups["obstacle"], False
        )
        """
        for wall in self.game_manager.walls:
            if self.collide(wall):
                return True
        return False

    def collide(self, entity):
        if hasattr(entity, "rect"):
            return self.rect.colliderect(entity.rect)
        return self.rect.colliderect(entity.hitbox.rect)
