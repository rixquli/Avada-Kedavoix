from typing import Tuple
import pygame

from client.enums.anchor import Anchor


class UIUtils:
    @staticmethod
    def calculate_position_with_anchor(
        width: float, height: float, anchor: Anchor, position: Tuple[float, float]
    ):
        """
        Calcule la position réelle (topleft) en fonction de l'ancrage par rapport à l'écran.
        Si screen_size est fourni, utilise les positions d'ancrage relatives à l'écran.
        """
        rect_width = width
        rect_height = height

        # Extraire la valeur string de l'Enum
        anchor_value = anchor.value

        if pygame.display.get_surface().get_size():
            screen_width, screen_height = pygame.display.get_surface().get_size()

            temp_rect = pygame.Rect(0, 0, rect_width, rect_height)

            screen_anchor_pos = UIUtils.get_screen_anchor_position(
                anchor_value, screen_width, screen_height, position
            )

            # ex: temp_rect.center = position permet de positionner le centre
            # du rect a la position voulue
            setattr(temp_rect, anchor_value, screen_anchor_pos)

            return (
                temp_rect.left,
                temp_rect.top,
            )  # Renvoie la vraie position a appliquer
        return (0, 0)

    @staticmethod
    def get_screen_anchor_position(
        anchor_value: Anchor,
        screen_width: float,
        screen_height: float,
        position: Tuple[float, float],
    ):
        """
        Retourne la position du point d'ancrage
        """
        anchor_positions = {
            "topleft": (0, 0),
            "midtop": (screen_width // 2, 0),
            "topright": (screen_width, 0),
            "midleft": (0, screen_height // 2),
            "center": (screen_width // 2, screen_height // 2),
            "midright": (screen_width, screen_height // 2),
            "bottomleft": (0, screen_height),
            "midbottom": (screen_width // 2, screen_height),
            "bottomright": (screen_width, screen_height),
        }

        base_x, base_y = anchor_positions.get(anchor_value, (0, 0))
        offset_x, offset_y = (
            position  # offset correspond ici a la position par rapport au point d'ancrage
        )

        return (base_x + offset_x, base_y + offset_y)
