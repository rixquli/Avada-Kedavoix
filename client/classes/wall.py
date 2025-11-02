from typing import List, Tuple
import pygame


class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super().__init__()
        self.x = x
        self.y = y
        self.image = pygame.Surface((w, h))
        self.image.fill((100, 100, 100))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def update(self):
        pass

    def draw(self, surface: pygame.Surface, offset=(0, 0)):
        surface.blit(self.image, (self.x + offset[0], self.y + offset[1]))

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
