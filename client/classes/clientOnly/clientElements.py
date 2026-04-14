"""
Classe pour la gestion des murs
"""

import pygame
from client.layerList import Layer


class CleintElementBehaviour:
    def __init__(self, x, y, world_layer: int | Layer = Layer.OVERWORLD):
        self.x = x
        self.y = y
        self.world_layer = (
            world_layer.value if isinstance(world_layer, Layer) else int(world_layer)
        )

    def draw(self, surface, offset):
        pass

    def local_update(self):
        pass


class ClientElements:
    def __init__(self):
        """
        elements: [
            Object must have at least {
                x,
                y,
                draw(surface, offset),
                local_update(),
                handle_event(event)
            }
        ]
        """
        self.elements = []

    def add(self, element):
        self.elements.append(element)

    def draw_all(
        self,
        surface,
        offset: tuple[float, float],
        active_world_layer: int | None = None,
    ):
        """
        Dessine tout les murs
        """
        for element in self.elements:
            if (
                active_world_layer is not None
                and element.world_layer != active_world_layer
            ):
                continue
            element.draw(surface, offset)

    def local_update_all(self):
        """
        Met à jour tout les éléments locaux
        """
        for element in self.elements:
            element.local_update()

    def handle_event(self, event):
        """
        Gère les evenement pour tout les éléments locaux
        """
        for element in self.elements:
            element.handle_event(event)
