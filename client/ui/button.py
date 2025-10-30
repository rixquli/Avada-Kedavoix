import pygame

from client.enums.anchor import Anchor


class Button:
    def __init__(
        self,
        text,
        width,
        height,
        position,
        onclickFunction=None,
        color=(20, 20, 20),
        bg_color=(200, 200, 200),
        hover_color=(150, 150, 150),
        font_size=35,
        font_name="Corbel",
        anchor: Anchor = Anchor.TOPLEFT,
    ):
        self.width = width
        self.height = height
        self.position = position
        self.onclickFunction = onclickFunction
        self.color = color
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.font_size = font_size
        self.font_name = font_name
        self.font = pygame.font.SysFont(self.font_name, self.font_size)
        self.text = self.font.render(text, True, self.color)
        self.anchor = anchor

        self._calculate_actual_position()

        self.buttonRect = pygame.Rect(
            self.actual_position[0], self.actual_position[1], self.width, self.height
        )

    def _calculate_actual_position(self):
        """
        Calcule la position réelle (topleft) en fonction de l'ancrage par rapport à l'écran.
        Si screen_size est fourni, utilise les positions d'ancrage relatives à l'écran.
        """
        rect_width = self.width
        rect_height = self.height

        # Extraire la valeur string de l'Enum
        anchor_value = (
            self.anchor.value if isinstance(self.anchor, Anchor) else self.anchor
        )

        if pygame.display.get_surface().get_size():
            screen_width, screen_height = pygame.display.get_surface().get_size()

            temp_rect = pygame.Rect(0, 0, rect_width, rect_height)

            screen_anchor_pos = self._get_screen_anchor_position(
                anchor_value, screen_width, screen_height
            )

            setattr(temp_rect, anchor_value, screen_anchor_pos)

            self.actual_position = (temp_rect.left, temp_rect.top)
        else:
            temp_rect = pygame.Rect(0, 0, rect_width, rect_height)
            setattr(temp_rect, anchor_value, self.position)
            self.actual_position = (temp_rect.left, temp_rect.top)

    def _get_screen_anchor_position(self, anchor_value, screen_width, screen_height):
        """
        Retourne la position du point d'ancrage sur l'écran.

        Args:
            anchor_value: Nom du point d'ancrage (ex: "midtop", "center")
            screen_width: Largeur de l'écran
            screen_height: Hauteur de l'écran

        Returns:
            Tuple (x, y) de la position d'ancrage sur l'écran
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
            self.position if isinstance(self.position, tuple) else (0, 0)
        )

        return (base_x + offset_x, base_y + offset_y)

    def draw(self, window):
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.buttonRect.collidepoint(mouse_pos)

        current_color = self.hover_color if is_hovered else self.bg_color

        pygame.draw.rect(window, current_color, self.buttonRect, border_radius=10)

        pygame.draw.rect(window, (255, 255, 255), self.buttonRect, 2, border_radius=10)

        text_x = (
            self.actual_position[0]
            + self.buttonRect.width / 2
            - self.text.get_rect().width / 2
        )
        text_y = (
            self.actual_position[1]
            + self.buttonRect.height / 2
            - self.text.get_rect().height / 2
        )

        window.blit(self.text, [text_x, text_y])

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.buttonRect.collidepoint(event.pos):
                if self.onclickFunction:
                    self.onclickFunction()

    def is_clicked(self):
        if pygame.mouse.get_pressed()[0]:
            if self.buttonRect.collidepoint(pygame.mouse.get_pos()):
                if self.onclickFunction:
                    self.onclickFunction()
                return True
        return False
