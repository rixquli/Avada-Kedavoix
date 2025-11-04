"""
Element graphique permet la creation de Texte
"""

from typing import Tuple
import pygame

from client.enums.anchor import Anchor
from client.ui.uiUtils import UIUtils


class Text:
    def __init__(
        self,
        text,
        position: Tuple[float, float],
        font_size=35,
        font_name="Corbel",
        background=False,
        width=None,
        height=None,
        color=(20, 20, 20),
        bg_color=(200, 200, 200),
        anchor: Anchor = Anchor.TOPLEFT,
    ):
        self.position = position
        self.color = color
        self.bg_color = bg_color
        self.font_size = font_size
        self.font_name = font_name
        self.font = pygame.font.SysFont(self.font_name, self.font_size)
        self.text = text
        self.rendered_text = self.font.render(text, True, self.color)
        self.background = background
        self.anchor = anchor

        # si la width et la heigth sont definit on s'en sert
        # sinon on prend la taille du texte
        if self.background and self.width and self.height:
            self.width = width
            self.height = height
        else:
            text_rect = self.rendered_text.get_rect()
            self.width = text_rect.width
            self.height = text_rect.height

        # self.position = position par rapport au point d'ancrage
        # actual_position = la position du rendu de l'objet dans le monde
        self.actual_position = UIUtils.calculate_position_with_anchor(
            self.width, self.height, self.anchor, self.position
        )

        if background:
            self.backgroundRect = pygame.Rect(
                self.position[0], self.position[1], self.width, self.height
            )
        else:
            self.backgroundRect = None

    def change_text(self, new_text):
        self.text = new_text
        self.rendered_text = self.font.render(self.text, True, self.color)

        if not (self.background and self.width and self.height):
            text_rect = self.rendered_text.get_rect()
            self.width = text_rect.width
            self.height = text_rect.height

        self.actual_position = UIUtils.calculate_position_with_anchor(
            self.width, self.height, self.anchor, self.position
        )

    def draw(self, window):
        if self.background:
            pygame.draw.rect(
                window, self.bg_color, self.backgroundRect, border_radius=10
            )

            pygame.draw.rect(
                window, (255, 255, 255), self.backgroundRect, 2, border_radius=10
            )

            text_x = (
                self.position[0]
                + self.backgroundRect.width / 2
                - self.rendered_text.get_rect().width / 2
            )
            text_y = (
                self.position[1]
                + self.backgroundRect.height / 2
                - self.rendered_text.get_rect().height / 2
            )
        else:
            text_x = self.actual_position[0]
            text_y = self.actual_position[1]

        window.blit(self.rendered_text, [text_x, text_y])
