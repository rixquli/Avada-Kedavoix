"""
Element graphique permet la creation d'input text (champ de text)
et la gestion des touches enregistrer lorsqu'il est selectionné
"""

import pygame

from client.enums.anchor import Anchor
from client.ui.uiUtils import UIUtils


class TextInput:
    def __init__(
        self,
        placeholder,
        position,
        width,
        height,
        onTextChanged,
        font_size=35,
        font_name="Corbel",
        color=(20, 20, 20),
        bg_color=(200, 200, 200),
        anchor: Anchor = Anchor.TOPLEFT,
        initial_text="",
    ):
        self.position = position
        self.width = width
        self.height = height
        self.onTextChanged = onTextChanged
        self.color = color
        self.bg_color = bg_color
        self.font_size = font_size
        self.font_name = font_name
        self.font = pygame.font.SysFont(self.font_name, self.font_size)
        self.placeholder = self.font.render(placeholder, True, self.color)
        self.text = initial_text
        self.previousText = self.text
        self.textRenderer = self.font.render(self.text, True, self.color)
        self.active = False
        self.done = False
        self.anchor = anchor

        # self.position = position par rapport au point d'ancrage
        # actual_position = la position du rendu de l'objet dans le monde
        self.actual_position = UIUtils.calculate_position_with_anchor(
            self.width, self.height, self.anchor, self.position
        )

        self.input_box = pygame.Rect(
            self.actual_position[0], self.actual_position[1], self.width, self.height
        )

        # Si initial_text est definie on execute onTextChanged
        self.onTextChanged(self.text)

    def updateText(self):
        if self.text != self.previousText:
            self.textRenderer = self.font.render(self.text, True, self.color)
            self.previousText = self.text
            self.onTextChanged(self.text)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.input_box.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False

        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                result = self.text
                return result
            elif event.key == pygame.K_BACKSPACE:
                # Retire le dernier element
                self.text = self.text[:-1]
            elif event.key == pygame.K_ESCAPE:
                self.active = False
            else:
                self.text += event.unicode

        return None

    def draw(self, window):
        self.updateText()
        pygame.draw.rect(window, self.bg_color, self.input_box, border_radius=10)

        pygame.draw.rect(window, (255, 255, 255), self.input_box, 2, border_radius=10)

        text_to_render = self.placeholder if self.text == "" else self.textRenderer

        text_x = (
            self.actual_position[0]
            + self.input_box.width / 2
            - text_to_render.get_rect().width / 2  # Pour centrer le texte
        )
        text_y = (
            self.actual_position[1]
            + self.input_box.height / 2
            - text_to_render.get_rect().height / 2  # Pour centrer le texte
        )

        window.blit(text_to_render, [text_x, text_y])
