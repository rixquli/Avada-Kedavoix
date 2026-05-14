from client.enums.anchor import Anchor
from client.layerList import Layer
from client.ui.text import Text


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

        self.text_to_render = Text(
            f"Ennemy left: {self.current_val}",
            self.position,
            color=(255, 255, 255),
            anchor=self.anchor,
            font_size=self.font_size,
        )

    def update(self):
        current_player = self.game_manager.client_manager.get_player()
        if current_player:
            self.current_val = len(self.game_manager.game_state.enemies.get_list())
            self.text_to_render.change_text(f"Ennemy left: {self.current_val}")

    def draw(
        self,
        surface,
    ):
        current_player = self.game_manager.client_manager.get_player()
        if (
            current_player and current_player.world_layer.value > 1
            if isinstance(current_player.world_layer, Layer)
            else current_player.world_layer > 1
        ):
            self.text_to_render.draw(surface)
