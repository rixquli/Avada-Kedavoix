import time
from typing import List, Tuple
import pygame

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
        lifetime: float = 5.0,
    ):
        self.id = id
        self.x = float(x)
        self.y = float(y)
        self.player_id = player_id
        self.color = tuple(color)
        self.dir = tuple(dir)
        self.radius = int(radius)
        self.lifetime = float(lifetime)
        self.creation_time = time.time()

    def move(self, x, y):
        self.x = x
        self.y = y

    def update(self):
        self.x += self.dir[0]
        self.y += self.dir[1]

    def is_expired(self) -> bool:
        """VErifie si le sort a depasse sa duree de vie"""
        return time.time() - self.creation_time > self.lifetime

    def draw(self, surface, offset: Tuple[float, float]):

        pygame.draw.circle(
            surface,
            self.color,
            (int(self.x + offset[0]), int(self.y + offset[1])),
            self.radius,
        )

    @staticmethod
    def draw_all(surface, offset: Tuple[float, float], all_spells: List["Spell"]):
        """
        Dessine tout les spells
        """
        if all_spells:
            if isinstance(all_spells, list):
                for spell in all_spells:
                    spell.draw(surface, offset)
            else:
                all_spells.draw(surface, offset)
