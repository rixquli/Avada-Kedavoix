import pygame

from client.enums.anchor import Anchor
from client.ui.rect import UIRect
from client.ui.text import Text


class Credit:
    def __init__(self, call_back):
        self.background = UIRect(
            fullscreen=True,
            color=(0, 0, 0, 255),
            position=(0, 0),
            anchor=Anchor.CENTER,
        )

        self.position = (0, 0)
        self.line_heigth = 50
        self.scroll_speed = 80
        self.start_offset = 50
        self.y_offset = self.start_offset
        self.call_back = call_back

        self.texts = [
            Text(
                "AVADA KEDAVOIX",
                self.position,
                color=(255, 255, 255),
                font_bold=True,
                font_size=56,
                anchor=Anchor.MIDBOTTOM,
            ),
            Text("", self.position, color=(255, 255, 255), anchor=Anchor.MIDBOTTOM),
            Text(
                "Un jeu par VoxStudio",
                self.position,
                color=(220, 220, 220),
                font_size=36,
                anchor=Anchor.MIDBOTTOM,
            ),
            Text("", self.position, color=(255, 255, 255), anchor=Anchor.MIDBOTTOM),
            Text(
                "Equipe de developpement",
                self.position,
                color=(255, 220, 130),
                font_bold=True,
                font_size=42,
                anchor=Anchor.MIDBOTTOM,
            ),
            Text("", self.position, color=(255, 255, 255), anchor=Anchor.MIDBOTTOM),
            Text(
                "Clement Bonnaud - Chef de projet",
                self.position,
                color=(255, 255, 255),
                font_size=34,
                anchor=Anchor.MIDBOTTOM,
            ),
            Text(
                "Mathilde Hubert - Maitre du temps et graphiste",
                self.position,
                color=(255, 255, 255),
                font_size=34,
                anchor=Anchor.MIDBOTTOM,
            ),
            Text(
                "Theo Privat - Developpeur en chef",
                self.position,
                color=(255, 255, 255),
                font_size=34,
                anchor=Anchor.MIDBOTTOM,
            ),
            Text(
                "Mathilde Pujol-Sillie - Rédactrice en chef",
                self.position,
                color=(255, 255, 255),
                font_size=34,
                anchor=Anchor.MIDBOTTOM,
            ),
            Text(
                "Anthon Nazon - Responsable COM",
                self.position,
                color=(255, 255, 255),
                font_size=34,
                anchor=Anchor.MIDBOTTOM,
            ),
            Text("", self.position, color=(255, 255, 255), anchor=Anchor.MIDBOTTOM),
            Text(
                "Technologies",
                self.position,
                color=(255, 220, 130),
                font_bold=True,
                font_size=40,
                anchor=Anchor.MIDBOTTOM,
            ),
            Text(
                "Python - Pygame - Vosk - PyTMX",
                self.position,
                color=(220, 220, 220),
                font_size=30,
                anchor=Anchor.MIDBOTTOM,
            ),
            Text("", self.position, color=(255, 255, 255), anchor=Anchor.MIDBOTTOM),
            Text(
                "Merci d'avoir joue !",
                self.position,
                color=(255, 255, 255),
                font_bold=True,
                font_size=40,
                anchor=Anchor.MIDBOTTOM,
            ),
        ]

        self.total_height = len(self.texts) * self.line_heigth
        self.last_ticks = pygame.time.get_ticks()

    def update(self):
        now = pygame.time.get_ticks()
        dt = (now - self.last_ticks) / 1000.0
        self.last_ticks = now

        self.y_offset -= self.scroll_speed * dt

        if self.y_offset < -2.5 * self.total_height:
            self.y_offset = self.start_offset
            self.call_back()

    def draw(self, surface):
        self.background.draw(surface)

        for i, line in enumerate(self.texts):
            line.position = (
                self.position[0],
                self.y_offset + i * self.line_heigth,
            )
            line.draw(surface)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.call_back()
