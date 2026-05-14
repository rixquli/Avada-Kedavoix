"""
Element graphique permet la creation de Texte
"""

import pygame

from client.enums.anchor import Anchor
from client.ui.uiUtils import UIUtils


class Text:
    def __init__(
        self,
        text,
        position: tuple[float, float],
        font_size=35,
        font_name="Corbel",
        background=False,
        width=None,
        height=None,
        color=(20, 20, 20),
        bg_alpha=255,
        bg_color=(200, 200, 200),
        anchor: Anchor = Anchor.TOPLEFT,
        text_align: str = "center",
        bg_border=True,
    ):
        self.position = position
        self.color = color
        self.bg_color = bg_color
        self.bg_alpha = bg_alpha
        self.bg_border = bg_border
        self.font_size = font_size
        self.font_name = font_name
        self.font = pygame.font.SysFont(self.font_name, self.font_size)
        self.text = text
        self.background = background
        self.anchor = anchor
        self.text_align = text_align
        self.fixed_background_size = bool(
            background and width is not None and height is not None
        )

        # si la width et la heigth sont definit on s'en sert
        # sinon on prend la taille du texte
        if self.fixed_background_size:
            self.width = width
            self.height = height
        else:
            test_render = self.font.render(text, True, self.color)
            text_rect = test_render.get_rect()
            self.width = text_rect.width
            self.height = text_rect.height

        # Wrapper le texte si on a une largeur fixe
        self.rendered_lines = self._render_lines()

        # Recalculer la hauteur si text wrapping
        if self.fixed_background_size and len(self.rendered_lines) > 1:
            line_height = self.font.get_height()
            self.height = max(self.height, len(self.rendered_lines) * line_height + 10)

        # self.position = position par rapport au point d'ancrage
        # actual_position = la position du rendu de l'objet dans le monde
        self.actual_position = UIUtils.calculate_position_with_anchor(
            self.width, self.height, self.anchor, self.position
        )

        if background:
            self.backgroundRect = pygame.Rect(
                self.actual_position[0],
                self.actual_position[1],
                self.width,
                self.height,
            )
        else:
            self.backgroundRect = None

    def _wrap_text(self) -> list[str]:
        """
        Découpe le texte en lignes selon la largeur disponible.
        Retourne une liste de lignes.
        """
        if not self.fixed_background_size:
            return [self.text]

        words = self.text.split(" ")
        lines = []
        current_line = ""

        for word in words:
            # Tester si on peut ajouter le mot à la ligne actuelle
            test_line = current_line + (" " if current_line else "") + word
            test_render = self.font.render(test_line, True, self.color)

            if test_render.get_width() < self.width - 10:  # Marges
                current_line = test_line
            else:
                # Le mot ne rentre pas, on passe à la ligne suivante
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines if lines else [self.text]

    def _render_lines(self) -> list[pygame.Surface]:
        """
        Rend le texte en lignes séparées selon le wrapping.
        Retourne une liste de surfaces pygame.
        """
        lines = self._wrap_text()
        return [self.font.render(line, True, self.color) for line in lines]

    def change_text(self, new_text):
        self.text = new_text
        self.rendered_lines = self._render_lines()

        if not self.fixed_background_size:
            total_width = (
                max([line.get_width() for line in self.rendered_lines])
                if self.rendered_lines
                else 0
            )
            line_height = self.font.get_height()
            self.width = total_width
            self.height = len(self.rendered_lines) * line_height

        self.actual_position = UIUtils.calculate_position_with_anchor(
            self.width, self.height, self.anchor, self.position
        )
        if self.backgroundRect:
            self.backgroundRect.topleft = self.actual_position
            self.backgroundRect.width = self.width
            self.backgroundRect.height = self.height

    def update_position(self):
        self.actual_position = UIUtils.calculate_position_with_anchor(
            self.width, self.height, self.anchor, self.position
        )
        if self.backgroundRect:
            self.backgroundRect.topleft = self.actual_position

    def on_resize(self):
        self.update_position()

    def draw(self, window):
        self.update_position()

        if self.background:
            bg_surface = pygame.Surface(
                (self.backgroundRect.width, self.backgroundRect.height),
                pygame.SRCALPHA,
            )
            bg_color = pygame.Color(
                self.bg_color[0], self.bg_color[1], self.bg_color[2], self.bg_alpha
            )
            pygame.draw.rect(
                bg_surface, bg_color, bg_surface.get_rect(), border_radius=10
            )
            window.blit(bg_surface, self.backgroundRect.topleft)
            if self.bg_border:
                pygame.draw.rect(
                    window, (255, 255, 255), self.backgroundRect, 2, border_radius=10
                )

            # Rendre les lignes avec l'alignement du texte
            line_height = self.font.get_height()
            total_lines_height = len(self.rendered_lines) * line_height

            # Position de départ en Y selon l'alignement
            if self.text_align == "center":
                start_y = (
                    self.actual_position[1]
                    + self.backgroundRect.height / 2
                    - total_lines_height / 2
                )
            elif self.text_align == "bottomleft" or self.text_align == "bottom":
                start_y = (
                    self.actual_position[1]
                    + self.backgroundRect.height
                    - total_lines_height
                    - 5
                )
            else:  # topleft, top (par défaut)
                start_y = self.actual_position[1] + 5

            # Rendre chaque ligne
            for i, rendered_line in enumerate(self.rendered_lines):
                line_y = start_y + i * line_height

                # Position en X selon l'alignement
                if self.text_align == "center":
                    line_x = (
                        self.actual_position[0]
                        + self.backgroundRect.width / 2
                        - rendered_line.get_width() / 2
                    )
                elif self.text_align == "topright" or self.text_align == "right":
                    line_x = (
                        self.actual_position[0]
                        + self.backgroundRect.width
                        - rendered_line.get_width()
                        - 5
                    )
                else:  # topleft, top, bottomleft (par défaut)
                    line_x = self.actual_position[0] + 5

                window.blit(rendered_line, [line_x, line_y])
        else:
            # Sans background : rendre les lignes à partir de actual_position
            line_height = self.font.get_height()

            for i, rendered_line in enumerate(self.rendered_lines):
                if self.text_align == "center":
                    line_x = (
                        self.actual_position[0]
                        + (self.width - rendered_line.get_width()) / 2
                    )
                elif self.text_align == "right":
                    line_x = (
                        self.actual_position[0]
                        + self.width
                        - rendered_line.get_width()
                    )
                else:  # topleft (par défaut)
                    line_x = self.actual_position[0]

                line_y = self.actual_position[1] + i * line_height
                window.blit(rendered_line, [line_x, line_y])
