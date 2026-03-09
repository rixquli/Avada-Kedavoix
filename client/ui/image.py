import pygame

from client.enums.anchor import Anchor
from client.ui.uiUtils import UIUtils


class Image:
    def __init__(
        self,
        path,
        width,
        height,
        position,
        anchor: Anchor = Anchor.TOPLEFT,
    ):
        self.width = width
        self.height = height
        self.position = position
        self.anchor = anchor

        # position réelle selon l'ancrage
        self.actual_position = UIUtils.calculate_position_with_anchor(
            self.width, self.height, self.anchor, self.position
        )

        # charger l'image
        self.image = pygame.image.load(path)

        # redimensionner l'image
        self.image = pygame.transform.scale(self.image, (self.width, self.height))

    def draw(self, window):
        window.blit(self.image, self.actual_position)
