import pygame
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from client.Utils.ImageTool import ImageTool
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
        is_background: bool = False,
    ):
        self.position = position
        self.anchor = anchor

        # Charger d'abord l'image pour pouvoir utiliser sa taille native si besoin.
        # path = os.path.abspath(
        #     os.path.join(os.path.dirname(__file__), "..", "..", path)
        # )
        loaded_image = ImageTool.load(path)
        native_width, native_height = loaded_image.get_size()
        self.width = width if width is not None else native_width
        self.height = height if height is not None else native_height

        self.actual_position = UIUtils.calculate_position_with_anchor(
            self.width, self.height, self.anchor, self.position
        )

        self.image = pygame.transform.scale(loaded_image, (self.width, self.height))
        self.is_back_ground = is_background

    def update_position(self):
        self.actual_position = UIUtils.calculate_position_with_anchor(
            self.width, self.height, self.anchor, self.position
        )

    def draw(self, window):
        self.update_position()
        window.blit(self.image, self.actual_position)

    def on_resize(self):
        if self.is_back_ground:
            display_info = pygame.display.Info()
            self.width, self.height = (display_info.current_w, display_info.current_h)
            self.image = pygame.transform.scale(self.image, (self.width, self.height))

