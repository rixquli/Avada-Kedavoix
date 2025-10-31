# To import module from other folder
import os
import sys


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pygame
from client.classes.spell import Spell
from client.clientManager import ClientManager
from client.ui.UI import UI


def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


# @singleton
class GameManager:
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(GameManager, cls).__new__(cls)
            cls.instance.setup()
        return cls.instance

    def __init__(self):
        """
        Executer __init__ apres chaque definition local du GameManager
        """
        pass

    def setup(self):
        """
        Execute setup uniquement lors de la création du premier GameManager
        """
        self.client_manager = ClientManager()

        # Setup pygame
        self.setup_pygame()

        from client.menus import Menus

        self.ui = UI(self.screen)
        self.ui.import_menus(Menus)

    def setup_pygame(self):
        pygame.init()
        self.width, self.height = 1920 // 2, 1080 // 2
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Avada Kedavoix")
        self.clock = pygame.time.Clock()
        self.running = True

    def render(self):
        if not self.running:
            pygame.quit()
            sys.exit()
            return

        self.clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            self.handle_event(event)

        self.screen.fill((0, 0, 0))

        self.client_manager.update(self.screen)
        self.ui.update()

        pygame.display.flip()

    def singlePlayerButtonClicked(self, menu):
        self.ui.hide(menu)
        self.client_manager.startSinglePlayer()

    def hostButtonClicked(self, menu):
        self.ui.hide(menu)
        self.client_manager.startHosting()

    def joinButtonClicked(self, main_menu, join_menu):
        self.ui.hide(main_menu)
        self.ui.show(join_menu)

    def joinGameButtonClicked(self, menu, ip, port):
        self.ui.hide(menu)
        self.client_manager.joinParty(ip, port)

    def handle_event(self, event):
        self.ui.handle_event(event)

        # TODO: déplacer la logique dans une classe spécifique pour les actions
        if event.type == pygame.MOUSEBUTTONDOWN:
            my_player = self.client_manager.get_player()
            if not my_player:
                return

            # Calculer la direction normalisée vers le curseur de la souris
            mouse_x, mouse_y = event.pos
            dx = mouse_x - my_player.x
            dy = mouse_y - my_player.y
            length = (dx**2 + dy**2) ** 0.5

            if length > 0:
                dir_x = dx / length
                dir_y = dy / length
            else:
                dir_x, dir_y = 1, 0

            # Créer le sort localement (pour eviter les latences)
            spell = Spell(
                x=my_player.x,
                y=my_player.y,
                player_id=self.client_manager.my_player_id,
                color=(50, 150, 255),
                dir=(dir_x, dir_y),
                radius=8,
            )

            self.client_manager.cast_spell(spell)
