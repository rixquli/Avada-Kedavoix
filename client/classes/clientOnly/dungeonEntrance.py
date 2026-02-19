import math
import os
import pygame
from client.Utils.ImageTool import ImageTool
from client.classes.clientOnly.clientElements import CleintElementBehaviour


class DungeonEntrance(CleintElementBehaviour):
    def __init__(self, x, y):
        super().__init__(x, y)
        from client.gameManager import GameManager

        PROJECT_ROOT = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "..")
        )
        path = os.path.join(
            PROJECT_ROOT, "client", "ressources", "Dungeon", "Entrance.png"
        )
        self.image = ImageTool.load(path, (150, 150))
        self.game_manager = GameManager()
        self.distance_trigger = 50

    def draw(self, surface: pygame.Surface, offset):
        x = self.x + offset[0]
        y = self.y + offset[1]
        ImageTool.blit_centered(surface, self.image, (x, y))

    def local_update(self):
        current_player = self.game_manager.client_manager.game_state.players.get(
            self.game_manager.client_manager.my_player_id
        )
        if not current_player:
            return
        distance = abs(
            math.sqrt(
                (current_player.x - self.x) ** 2 + (current_player.y - self.y) ** 2
            )
        )
        if distance < self.distance_trigger:
            self.game_manager.ui.show("press_e")
        else:
            self.game_manager.ui.hide("press_e")

    def handle_event(self, event: pygame.event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            print("ENTER THE DUNGEON")
