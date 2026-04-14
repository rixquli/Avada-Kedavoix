import pygame

from client.enums.anchor import Anchor
from client.ui.uiUtils import UIUtils


class UIRect:
    def __init__(
        self,
        position,
        width=500,
        height=500,
        fullscreen=False,
        color=(225, 225, 225),
        anchor: Anchor = Anchor.TOPLEFT,
    ):
        self.width = width
        self.height = height
        self.position = position
        self.fullscreen = fullscreen
        self.color = color
        self.anchor = anchor

        if self.fullscreen:
            surface = pygame.display.get_surface()
            if surface is not None:
                self.width, self.height = surface.get_size()

        # self.position = position par rapport au point d'ancrage
        # actual_position = la position du rendu de l'objet dans le monde
        self.actual_position = UIUtils.calculate_position_with_anchor(
            self.width, self.height, self.anchor, self.position
        )

        self.rect = pygame.Rect(
            self.actual_position[0], self.actual_position[1], self.width, self.height
        )

    def update_position(self):
        self.actual_position = UIUtils.calculate_position_with_anchor(
            self.width, self.height, self.anchor, self.position
        )
        self.rect.topleft = self.actual_position

    def on_resize(self):
        self.update_position()

    def draw_rect_alpha(self, surface, color, rect):
        shape_surf = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
        pygame.draw.rect(shape_surf, color, shape_surf.get_rect())
        surface.blit(shape_surf, rect)

    def draw(self, window):
        self.update_position()

        if len(self.color) > 3:
            self.draw_rect_alpha(window, self.color, self.rect)
        else:
            pygame.draw.rect(window, self.color, self.rect)
