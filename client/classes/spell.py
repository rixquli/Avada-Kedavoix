from typing import Tuple

from server.classes.serializable import Serializable


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
    ):
        self.id = id
        self.x = float(x)
        self.y = float(y)
        self.player_id = player_id
        self.color = tuple(color)
        self.dir = tuple(dir)
        self.radius = int(radius)

    def move(self, x, y):
        self.x = x
        self.y = y

    def update(self):
        self.x += self.dir[0]
        self.y += self.dir[1]

    def draw(self, surface):
        import pygame

        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
