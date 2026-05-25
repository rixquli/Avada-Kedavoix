"""
Classe pour la gestion des maison
"""

from typing import Tuple
import pygame
import time
from enum import Enum

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from client.classes.animator import Animator
from client.classes.clientOnly.healthBar import HealthBar
from client.classes.spell import Spell, SpellList
from client.layerList import Layer
from server.classes.serializable import Serializable
from client.classes.hitbox import HitBox



class House(Serializable):
    def __init__(
        self,
        x: float,
        y: float,
        size: int=20,
        world_layer: int | Layer = Layer.OVERWORLD,
        debug: bool=False,
        is_server: bool=False,
        ):
        
        self.size = int(size)
        self.x = float(x)
        self.y = float(y)
        
        self.display_x = float(x)
        self.display_y = float(y)


        self.world_layer = (
            world_layer.value if isinstance(world_layer, Layer) else int(world_layer)
        )

        self.hitbox_size = (size * 9, size * 7)
        self.hitbox = HitBox(
            int(x), int(y), self.hitbox_size[0], self.hitbox_size[1], world_layer
        )

        self.animator = None
        
        if not is_server:
            self._init_client_resources()

        self.debug = debug


    def _init_client_resources(self):
        """Initialise les ressources graphiques côté client"""
        if self.animator is not None:
            return  # Déjà initialisé
        
        # pour les animations
        self.animator = Animator(
            size=(self.size * 9, self.size * 7), animation_speed=0.01
        )

         # Chemin vers la racine du projet
        PROJECT_ROOT = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..")
        )

        self.animator.state_manager.add_state(
            "idle",
            os.path.join(
                PROJECT_ROOT,
                "client",
                "ressources",
                "Village",
                "maison",
                "idle",
            ),
        )


    def server_update(self):
        #self.hitbox.update(int(self.x), int(self.y), self.world_layer)
        pass

    def draw(self, surface, offset: tuple[float, float]):
        self._init_client_resources()
        pos = (self.display_x + offset[0], self.display_y + offset[1])
        self.animator.blit_sprite(surface, pos)

        self.hitbox.draw(surface, offset)

        '''if self.debug:
            if self.path is not None:
                for pos in self.path:
                    pygame.draw.circle(
                        surface,
                        self.color,
                        (pos[0] + offset[0], pos[1] + offset[1]),
                        2,
                    )
        
        rect = pygame.Rect(
            self.display_x + offset[0],
            self.display_y + offset[1],
            self.size * 2,
            self.size * 2,
        )
        pygame.draw.rect(surface, (150, 100, 50), rect)

        if self.debug:
            self.hitbox.draw(surface, offset)
'''
    @staticmethod
    def draw_all(
        surface,
        offset: tuple[float, float],
        houses: list["House"],
        active_world_layer: int | None = None,
    ):
        """
        Dessine toutes les maisons
        """
        if houses:
            if isinstance(houses, list):
                for house in houses:
                    if (
                        active_world_layer is not None
                        and house.world_layer != active_world_layer
                    ):
                        continue
                    house.draw(surface, offset)
            else:
                houses.draw(surface, offset)
