"""
Classe pour la gestion des murs
"""

import pygame


class CleintElementBehaviour:
    def __init__(self, x, y):
        self.x = x
        self.y = y

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

    def draw_all(self, surface, offset: tuple[float, float]):
        """
        Dessine tout les murs
        """
        for element in self.elements:
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
