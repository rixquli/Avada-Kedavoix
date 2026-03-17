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

from client.classes.clientOnly.clientElements import ClientElements
from client.classes.clientOnly.dungeonEntrance import DungeonEntrance
from client.classes.enemy import Enemy
from client.classes.mapBackground import MapBackground
from client.classes.player import Player
from client.classes.pnj import PNJ
from client.classes.wall import Wall
from client.layerList import Layer
from client.spellsManager import SpellsManager
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
        return cls.instance

    def __init__(self):
        """
        Executer __init__ apres chaque definition local du GameManager
        """
        pass

    def setup(self):
        """
        Execute setup uniquement lors du lancement du programme mais client seulement
        """
        self.client_manager = ClientManager(self)

        # Setup voice recognition
        start_voice_recognition()

        self.spellManager = SpellsManager(self)

        # Setup pygame
        self.setup_pygame()

        # Setup ui/menus
        self.ui = UI(self.screen)

    def setup_server(self):
        """
        Execute setup uniquement lors du lancement du programme mais server seulement
        Pour ne pas init les partie graphique inutile au serveur
        """
        self.client_manager = ClientManager()

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

        self.world_layer = Layer.OVERWORLD.value
        self.layer_switch_cooldown_ms = 200
        self.last_layer_switch_ms = -self.layer_switch_cooldown_ms

        # TODO: à deplacer
        self.clientsElements = ClientElements()

        # TODO: enlever/deplacer
        self.maps = [
            MapBackground(
                os.path.normpath(
                    os.path.join(os.path.dirname(__file__), "tiles", "maps", "main.tmx")
                ),
                world_layer=Layer.OVERWORLD,
            )
        ]

        dungeonEntrance = DungeonEntrance(
            250, 0, world_layer=Layer.OVERWORLD, target_world_layer=Layer.DUNGEON_BASE
        )
        dungeonExit = DungeonEntrance(
            250,
            0,
            world_layer=Layer.DUNGEON_BASE,
            target_world_layer=Layer.OVERWORLD,
        )
        self.clientsElements.add(dungeonEntrance)
        self.clientsElements.add(dungeonExit)

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
        self.draw_elements()  # Dessine les elements de la scene
        self.ui.update()  # Dessine les elements des interfaces

        pygame.display.flip()  # Met a jour l'ecran

        self.deltatime = self.clock.tick(60)

    def handle_event(self, event):
        """
        Gere le evennements (ex: touches claviers, souris, ...)
        """
        if event.type == pygame.VIDEORESIZE:
            self.ui.on_resize()

        self.ui.handle_event(event)  # Gere les evenement des elements des interfaces

        self.clientsElements.handle_event(event)

        # TODO: déplacer la logique dans une classe spécifique pour les actions
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.spellManager.cast_basic_spell()

    def handle_voice_event(self):
        vocal_action = get_voice_command()

        if vocal_action:
            vocal_action = vocal_action.get("action", "")
        else:
            return

        self.spellManager.cast_spell(vocal_action)
        if vocal_action == "SPELL":
            self.spellManager.cast_basic_spell()

    def local_update(self):
        """
        Met a jour les elements qui ont besoin d'etre mis a jour localement
        ex: les joueurs qui gerent eux-meme leur déplacement
        """
        # Update local player
        self.update_local_player()
        self.clientsElements.local_update_all()

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
        self.world_layer = current_player.world_layer

        # Dessine la map de fond
        MapBackground.draw_all(
            self.screen, offset, self.maps, active_world_layer=self.world_layer
        )

        # Dessine les éléments cotés clients seulements
        self.clientsElements.draw_all(
            self.screen, offset, active_world_layer=self.world_layer
        )

        # Dessine les joueurs
        other_players = self.client_manager.game_state.players.get_except_list(
            self.client_manager.my_player_id
        )
        Player.draw_all(
            self.screen,
            offset,
            current_player,
            other_players,
            active_world_layer=self.world_layer,
        )

        # Dessine les spells
        Spell.draw_all(
            self.screen,
            offset,
            self.client_manager.game_state.spells.get_list(),
            active_world_layer=self.world_layer,
        )

        # Dessine les ennemis
        Enemy.draw_all(
            self.screen,
            offset,
            self.client_manager.game_state.enemies.get_list(),
            active_world_layer=self.world_layer,
        )

        # Dessine les PNJ
        PNJ.draw_all(
            self.screen,
            offset,
            self.client_manager.game_state.pnjs.get_list(),
            active_world_layer=self.world_layer,
        )

        # Dessine les murs
        Wall.draw_all(
            self.screen,
            offset,
            self.client_manager.game_state.walls.get_list(),
            active_world_layer=self.world_layer,
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

    @property
    def game_state(self):
        return self.client_manager.game_state

    @property
    def collision_manager(self):
        return self.client_manager.game_state.collision_manager

    # TODO: Move to specialized manager
    def switch_player_layer(self, target_layer):
        now_ms = pygame.time.get_ticks()
        if now_ms - self.last_layer_switch_ms < self.layer_switch_cooldown_ms:
            return False

        current_player = self.client_manager.get_player()
        if not current_player:
            return False

        target_layer_value = (
            target_layer.value if isinstance(target_layer, Layer) else int(target_layer)
        )

        if current_player.world_layer == target_layer_value:
            return False

        current_player.world_layer = target_layer_value
        self.last_layer_switch_ms = now_ms
        return True
