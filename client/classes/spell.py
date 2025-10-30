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

        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

    @classmethod
    def drawSpell(self, surface, all_spells: List["Spell"]):
        # Dessine met a jour tout les spells
        # player_spells = [s for s in all_spells if s.player_id == self.my_player_id]
        # other_player_spells = [
        #     s for s in all_spells if s.player_id != self.my_player_id
        # ]

        if all_spells:
            if isinstance(all_spells, list):
                for spell in all_spells:
                    spell.draw(surface)
            else:
                all_spells.draw(surface)

        # if isinstance(player_spells, list):
        #     for spell in player_spells:
        #         spell.draw(surface)
        #         # spell.update()
        # else:
        #     player_spells.draw(surface)
        # player_spells.update()
