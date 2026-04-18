import os

import pygame

from client.Utils.ImageTool import ImageTool
from client.enums.anchor import Anchor
from client.ui.image import Image
from client.ui.text import Text
from client.ui.uiUtils import UIUtils


class DialogBox:
    def __init__(
        self,
        text,
        position,
        close_callback,
        anchor: Anchor = Anchor.MIDBOTTOM,
    ):
        self.text = text
        self.position = position
        self.anchor = anchor
        self.close_callback = close_callback
        # self.shown = True

        project_root = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "..",
            )
        )
        path = os.path.join(project_root, "client", "ressources", "UI", "DialogBox.png")

        source_image = ImageTool.load(path)
        source_width, source_height = source_image.get_size()
        self.width = source_width
        self.height = source_height

        self.actual_position = UIUtils.calculate_position_with_anchor(
            self.width, self.height, self.anchor, self.position
        )

        self.image = Image(path, self.width, self.height, position, anchor)

        self.textIndex = 0

        self.nameComp = Text(
            text[0].get("name", ""),
            (position[0] - 425, position[1] - 200),
            height=50,
            width=230,
            anchor=anchor,
            background=True,
        )
        self.textComp = Text(
            text[0].get("text", ""),
            (position[0], position[1] - 10),
            width=1080,
            height=180,
            background=True,
            anchor=anchor,
        )

    # def show(self):
    #     self.shown = True

    # def hide(self):
    #     self.shown = False

    def update_position(self):
        self.actual_position = UIUtils.calculate_position_with_anchor(
            self.width, self.height, self.anchor, self.position
        )
        self.image.actual_position = self.actual_position

    def on_resize(self):
        self.update_position()

    def draw(self, window):
        # if not self.shown:
        #     return
        self.update_position()
        self.image.draw(window)
        self.nameComp.draw(window)
        self.textComp.draw(window)

    def next_text(self):
        if self.textIndex < len(self.text) - 1:
            self.textIndex += 1
            self.nameComp.change_text(self.text[self.textIndex].get("name", ""))
            self.textComp.change_text(self.text[self.textIndex].get("text", ""))
        else:
            if self.close_callback is not None:
                self.close_callback()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.next_text()
