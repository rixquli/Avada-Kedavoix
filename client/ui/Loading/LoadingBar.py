import time
import pygame

from client.enums.anchor import Anchor
from client.ui.uiUtils import UIUtils


class LoadingBar:
    def __init__(
        self,
        width,
        height,
        position,
        color=(225, 225, 225),
        empty_color=(60, 60, 60),
        anchor: Anchor = Anchor.TOPLEFT,
        square_count=20,
        speed=12.0,  # carres par seconde
        gap=2,
    ):
        self.width = width
        self.height = height
        self.position = position
        self.color = color
        self.empty_color = empty_color
        self.anchor = anchor

        self.square_count = max(1, square_count)
        self.gap = max(0, gap)
        self.speed = max(0.1, speed)

        total_gap = self.gap * (self.square_count - 1)
        self.square_width = max(1, (self.width - total_gap) // self.square_count)

        self.fill_amount = 0
        self.direction = 1
        self.last_t = time.time()

        self.actual_position = UIUtils.calculate_position_with_anchor(
            self.width, self.height, self.anchor, self.position
        )

    def update_position(self):
        self.actual_position = UIUtils.calculate_position_with_anchor(
            self.width, self.height, self.anchor, self.position
        )

    def on_resize(self):
        self.update_position()

    def update(self):
        now = time.time()
        dt = now - self.last_t
        self.last_t = now

        self.fill_amount += self.direction * self.speed * dt

        if self.fill_amount >= self.square_count:
            self.fill_amount = float(self.square_count)
            self.direction = -1
        elif self.fill_amount <= 0:
            self.fill_amount = 0.0
            self.direction = 1

    def draw(self, window):
        self.update_position()
        filled = int(self.fill_amount)

        x0, y0 = self.actual_position
        for i in range(self.square_count):
            x = x0 + i * (self.square_width + self.gap)
            color = self.color if i < filled else self.empty_color
            pygame.draw.rect(
                window,
                color,
                (x, y0, self.square_width, self.height),
            )
