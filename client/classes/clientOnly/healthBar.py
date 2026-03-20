import pygame


class HealthBar:
    def __init__(
        self,
        width: int = 40,
        height: int = 6,
        y_offset: int = 12,
        bg_color: tuple[int, int, int] = (50, 50, 50),
        fg_color: tuple[int, int, int] = (40, 220, 40),
        border_color: tuple[int, int, int] = (0, 0, 0),
        is_pos_fixed: bool = False,
        pos_fixed: tuple[int, int] = (0, 0),
    ):
        self.width = width
        self.height = height
        self.y_offset = y_offset
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.border_color = border_color
        self.is_pos_fixed = is_pos_fixed
        self.pos_fixed = pos_fixed

    def draw(
        self,
        surface,
        x: float,
        y: float,
        current_hp: int,
        max_hp: int,
    ):
        if max_hp <= 0:
            return

        ratio = max(0.0, min(1.0, current_hp / max_hp))

        bar_x = int(x - self.width / 2)
        bar_y = int(y - self.y_offset)

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
