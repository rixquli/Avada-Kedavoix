import pygame

from client.enums.anchor import Anchor


class TextInput:
    def __init__(
        self,
        placeholder,
        position,
        width,
        height,
        onTextChanged,
        font_size=35,
        font_name="Corbel",
        color=(20, 20, 20),
        bg_color=(200, 200, 200),
        anchor: Anchor = Anchor.TOPLEFT,
    ):
        self.position = position
        self.width = width
        self.height = height
        self.onTextChanged = onTextChanged
        self.color = color
        self.bg_color = bg_color
        self.font_size = font_size
        self.font_name = font_name
        self.font = pygame.font.SysFont(self.font_name, self.font_size)
        self.placeholder = self.font.render(placeholder, True, self.color)
        self.text = ""
        self.previousText = ""
        self.textRenderer = self.font.render(self.text, True, self.color)
        self.active = False
        self.done = False
        self.anchor = anchor

        self._calculate_actual_position()

        self.input_box = pygame.Rect(
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

    def updateText(self):
        if self.text != self.previousText:
            self.textRenderer = self.font.render(self.text, True, self.color)
            self.previousText = self.text
            self.onTextChanged(self.text)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.input_box.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False

        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                result = self.text
                return result
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_ESCAPE:
                self.active = False
            else:
                self.text += event.unicode

        return None

    def draw(self, window):
        self.updateText()
        pygame.draw.rect(window, self.bg_color, self.input_box, border_radius=10)

        pygame.draw.rect(window, (255, 255, 255), self.input_box, 2, border_radius=10)

        text_to_render = self.placeholder if self.text == "" else self.textRenderer

        text_x = (
            self.actual_position[0]
            + self.input_box.width / 2
            - text_to_render.get_rect().width / 2
        )
        text_y = (
            self.actual_position[1]
            + self.input_box.height / 2
            - text_to_render.get_rect().height / 2
        )

        window.blit(text_to_render, [text_x, text_y])
