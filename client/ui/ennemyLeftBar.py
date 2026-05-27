import pygame

from client.enums.anchor import Anchor
from client.layerList import Layer
from client.ui.text import Text
from client.ui.uiUtils import UIUtils


class HealthBarGUI:
    def __init__(
        self,
        position,
        width: int = 40,
        height: int = 6,
        bg_color: tuple[int, int, int] = (50, 50, 50),
        fg_color: tuple[int, int, int] = (40, 220, 40),
        border_color: tuple[int, int, int] = (0, 0, 0),
        anchor: Anchor = Anchor.TOPLEFT,
    ):
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.border_color = border_color
        self.position = position
        self.anchor = anchor

        self.actual_position = UIUtils.calculate_position_with_anchor(
            self.width, self.height, self.anchor, self.position
        )
    def on_resize(self):
        self.actual_position = UIUtils.calculate_position_with_anchor(
            self.width, self.height, self.anchor, self.position
        )

    def draw(
        self,
        surface,
        current_hp: int,
        max_hp: int,
    ):
        if max_hp <= 0:
            return

        ratio = max(0.0, min(1.0, current_hp / max_hp))

        bar_x = self.actual_position[0]
        bar_y = self.actual_position[1]

        # bar_x = int(x - self.width / 2)
        # bar_y = int(y - self.height / 2)

        # Fond
        pygame.draw.rect(
            surface,
            self.bg_color,
            pygame.Rect(bar_x, bar_y, self.width, self.height),
        )

        # Vie restante
        pygame.draw.rect(
            surface,
            self.fg_color,
            pygame.Rect(bar_x, bar_y, int(self.width * ratio), self.height),
        )

        # Contour
        pygame.draw.rect(
            surface,
            self.border_color,
            pygame.Rect(bar_x, bar_y, self.width, self.height),
            1,
        )


class EnnemyLeftBar:
    def __init__(
        self,
        position=(0, 50),
        anchor: Anchor = Anchor.MIDTOP,
        font_size: int = 50,
        current_val=10,
    ):
        self.position = position
        self.anchor = anchor
        self.font_size = font_size

        self.current_val = current_val

        from client.gameManager import GameManager

        self.game_manager = GameManager()

        self.floor_enemy_left = Text(
            f"Enemy left: {self.current_val}",
            self.position,
            color=(255, 255, 255),
            anchor=self.anchor,
            font_size=self.font_size,
        )

        self.boss_bar = HealthBarGUI(
            (0, 100), width=500, height=25, anchor=Anchor.MIDTOP
        )
        self.boss_name = Text(
            f"Roi des Ténèbres",
            (0, 50),
            color=(255, 50, 50),
            anchor=self.anchor,
            font_size=self.font_size,
            font_bold=True,
        )

    def update(self):
        current_player = self.game_manager.client_manager.get_player()
        if current_player:
            self.current_val = len(self.game_manager.game_state.enemies.get_list())
            self.floor_enemy_left.change_text(
                f"Étage {current_player.world_layer-1}\nEnemis restant : {self.current_val}"
            )

    def on_resize(self):
        self.boss_bar.on_resize()
        self.boss_name.on_resize()
        self.floor_enemy_left.on_resize()

    def draw(
        self,
        surface,
    ):
        current_player = self.game_manager.client_manager.get_player()
        if not current_player:
            return

        boss = self.game_manager.game_state.enemies.filter_by(
            is_boss=True, world_layer=current_player.world_layer
        )

        if current_player and boss and len(boss) > 0:
            self.boss_bar.draw(surface, boss[0].hp, boss[0].max_hp)
            self.boss_name.draw(surface)
        else:
            if (
                current_player.world_layer.value > 1
                if isinstance(current_player.world_layer, Layer)
                else current_player.world_layer > 1
            ):
                self.floor_enemy_left.draw(surface)
