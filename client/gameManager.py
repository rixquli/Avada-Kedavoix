"""
Classe principale pour le coté client elle correspond à la gestion de toute la partie
GameManager est un singloton c'est a dire que de n'importe ou dans le projet:
GameManager() renverra la meme chose donc GameManager().ui permet de n'importe d'acceder au menus/interfaces

Elle gere:
    - l'initialisation de pygame
    - le rendu de tout les objets (dont logique de la camera)
    - la gestion de tous les evenements ex: clique souris ou touche du clavier
    - la mise a jour des element locaux comme le joueur
"""

import os
import sys

from client.classes.enemy import Enemy
from client.classes.player import Player
from client.classes.pnj import PNJ
from client.classes.wall import Wall
from client.voice.realtimeVoice import get_voice_command, start_voice_recognition


# To import module from other folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pygame
from client.classes.spell import Spell
from client.clientManager import ClientManager
from client.ui.UI import UI


class GameManager:
    def __new__(cls):
        """
        Permet de creer un singleton qui permet d'acceder aux valeurs et methodes
        de cette classe depuis n'importe ou
        """
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

        # Setup voice recognition
        start_voice_recognition()

        # Setup pygame
        self.setup_pygame()

        # Setup ui/menus
        self.ui = UI(self.screen)

    def setup_pygame(self):
        """Initialise pygame et crée la fenetre"""
        pygame.init()
        self.width, self.height = 1920 // 2, 1080 // 2
        self.screen = pygame.display.set_mode(
            (self.width, self.height), pygame.RESIZABLE
        )
        pygame.display.set_caption("Avada Kedavoix")
        self.clock = pygame.time.Clock()
        self.clock.tick(60)
        self.running = True

        # Group pour gerer les collisions
        # self.groups = {"obstacle": pygame.sprite.Group()}

        # TODO: a enlever juste pour tester
        # self.walls = [
        #     Wall(-500, -500, 1000, 50),
        #     Wall(-500, 500, 1050, 50),
        #     Wall(-500, -500, 50, 1000),
        #     Wall(500, -500, 50, 1000),
        #     Wall(100,100,100,50)
        # ]
        # for wall in self.walls:
        #     self.groups["obstacle"].add(wall)

    def render(self):
        """Fait un rendu du jeu a executer a chaque tick"""
        if not self.running:
            pygame.quit()
            sys.exit()
            return

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            self.handle_event(event)
        self.handle_voice_event()

        self.screen.fill((0, 0, 0))  # Dessine le fond noir

        self.local_update()  # Met a jour les elements qui se mette a jour localement comme le joueur qui ses propres mouvements
        self.ui.update()  # Dessine les elements des interfaces
        self.draw_elements()  # Dessine les elements de la scene

        pygame.display.flip()  # Met a jour l'ecran

        self.deltatime = self.clock.tick(60)

    # TODO: déplacer ailleur:
    def cast_basic_spell(self):
        # Quand on clique ca lance un sort dans la direction de la souris
        my_player = self.client_manager.get_player()
        if not my_player:
            return

        # Calculer la direction normalisée vers le curseur de la souris
        mouse_x, mouse_y = pygame.mouse.get_pos()
        dx = mouse_x - (self.screen.get_width() / 2)
        dy = mouse_y - (self.screen.get_height() / 2)
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
            thrower=my_player.THROWER_TYPE,
        )

        self.client_manager.cast_spell(spell)

    def handle_event(self, event):
        """
        Gere le evennements (ex: touches claviers, souris, ...)
        """
        self.ui.handle_event(event)  # Gere les evenement des elements des interfaces

        # TODO: déplacer la logique dans une classe spécifique pour les actions
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.cast_basic_spell()

    def handle_voice_event(self):
        vocal_action = get_voice_command()

        if vocal_action:
            vocal_action = vocal_action.get("action", "")
        else:
            return

        if vocal_action == "SPELL":
            self.cast_basic_spell()

    def local_update(self):
        """
        Met a jour les elements qui ont besoin d'etre mis a jour localement
        ex: les joueurs qui gerent eux-meme leur déplacement
        """
        # Update local player
        self.update_local_player()

    def get_camera_offset(self) -> tuple[float, float]:
        """
        Renvoie un x et un y qui correspond au decalage pour placer le joueur au centre de la fenetre
        """
        current_player = self.client_manager.get_player()
        if not current_player:
            return 0, 0

        x, y = current_player.display_x, current_player.display_y
        # display_x et pas x car x = position reelle et display_x la position lors du draw
        # player.x + offset = screen.width/2 => offset = screen.width/2 - player.x
        return (
            self.screen.get_width() / 2 - x,
            self.screen.get_height() / 2 - y,
        )

    def draw_elements(self):
        """
        Dessine tout les elements de la scene
        Mais en appliquant un offset a tout les element pour centrer le joueur
        au milieu de l'ecran pour simuler une camera qui suit le joueur
        """
        current_player = self.client_manager.get_player()
        if (
            not current_player or not self.screen
        ):  # si le joueur n'existe pas alors la partie n'est pas lancé
            return

        offset: tuple[float, float] = self.get_camera_offset()

        # Dessine les joueurs
        other_players = self.client_manager.game_state.players.get_except_list(
            self.client_manager.my_player_id
        )
        Player.draw_all(self.screen, offset, current_player, other_players)

        # Dessine les spells
        Spell.draw_all(
            self.screen, offset, self.client_manager.game_state.spells.get_list()
        )

        # Dessine les ennemis
        Enemy.draw_all(
            self.screen, offset, self.client_manager.game_state.enemies.get_list()
        )

        # Dessine les PNJ
        PNJ.draw_all(
            self.screen, offset, self.client_manager.game_state.pnjs.get_list()
        )

        # Dessine les murs
        Wall.draw_all(
            self.screen, offset, self.client_manager.game_state.walls.get_list()
        )

    def update_local_player(self):
        # Met a jour tout les joueurs
        if (
            self.client_manager.my_player_id
            not in self.client_manager.game_state.players.entities
        ):
            return

        current_player = self.client_manager.game_state.players.get(
            self.client_manager.my_player_id
        )
        # Met a jour le joueur local
        Player.update_local_player(current_player)

        # Envoyer ma position
        self.client_manager.send_my_position()
