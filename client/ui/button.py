"""
Element graphique permet la creation de boutons
et la gestion des evenements lors du clique
"""

import pygame

from client.enums.anchor import Anchor
from client.ui.uiUtils import UIUtils


class Button:
    def __init__(
        self,
        text,
        width,
        height,
        position,
        onclickFunction=None,
        color=(20, 20, 20),
        bg_color=(200, 200, 200),
        hover_color=(150, 150, 150),
        font_size=35,
        font_name="Corbel",
        anchor: Anchor = Anchor.TOPLEFT,
    ):
        self.width = width
        self.height = height
        self.position = position
        self.onclickFunction = onclickFunction
        self.color = color
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.font_size = font_size
        self.font_name = font_name
        self.font = pygame.font.SysFont(self.font_name, self.font_size)
        self.text = self.font.render(text, True, self.color)
        self.anchor = anchor

        # self.position = position par rapport au point d'ancrage
        # actual_position = la position du rendu de l'objet dans le monde
        self.actual_position = UIUtils.calculate_position_with_anchor(
            self.width, self.height, self.anchor, self.position
        )

        self.buttonRect = pygame.Rect(
            self.actual_position[0], self.actual_position[1], self.width, self.height
        )

    def update_position(self):
        self.actual_position = UIUtils.calculate_position_with_anchor(
            self.width, self.height, self.anchor, self.position
        )
        self.buttonRect.topleft = self.actual_position

    def on_resize(self):
        self.update_position()

    def draw(self, window):
        self.update_position()

        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.buttonRect.collidepoint(mouse_pos)

        current_color = self.hover_color if is_hovered else self.bg_color

        pygame.draw.rect(window, current_color, self.buttonRect, border_radius=10)

        pygame.draw.rect(window, (255, 255, 255), self.buttonRect, 2, border_radius=10)

        text_x = (
            self.actual_position[0]
            + self.buttonRect.width / 2
            - self.text.get_rect().width / 2
        )
        text_y = (
            self.actual_position[1]
            + self.buttonRect.height / 2
            - self.text.get_rect().height / 2
        )

        window.blit(self.text, [text_x, text_y])

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.buttonRect.collidepoint(event.pos):
                if self.onclickFunction:
                    self.onclickFunction()

    def is_clicked(self):
        if pygame.mouse.get_pressed()[0]:
            if self.buttonRect.collidepoint(pygame.mouse.get_pos()):
                if self.onclickFunction:
                    self.onclickFunction()
                return True
        return False
