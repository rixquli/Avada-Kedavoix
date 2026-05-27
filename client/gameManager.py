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

"""
3 choses a changer pour recuperer la reconaissance vocale:
    -enlever # ligne 33
    -enlever # ligne 68
    -enlever # ligne 153
"""

import os
import sys
import time

from client.classes.CameraBlackFade import CameraBlackFade
from client.classes.clientOnly.clientElements import ClientElements
from client.classes.clientOnly.dungeonEntrance import DungeonEntrance
from client.classes.enemy import Enemy
from client.classes.mapBackground import MapBackground
from client.classes.player import Player
from client.classes.pnj import PNJ
from client.classes.wall import Wall
from client.classes.house import House
from client.layerList import Layer
from client.sound.soundManager import SoundManager
from client.spellsManager import SpellsManager
from client.voice.realtimeVoice import get_voice_command, start_voice_recognition
from server.gameState import GameState
from server.world_elements.dungeonWalls import Dungeon

# To import module from other folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pygame
from client.classes.spell import Spell
from client.clientManager import ClientManager
from client.ui.UI import UI


def ease_in_out(t: float) -> float:
    if t <= 0.0:
        return 0.0
    if t >= 1.0:
        return 1.0
    return t * t * (3.0 - 2.0 * t)


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

        # Setup pygame
        self.setup_pygame()

        # Setup soundManager apres pygame important
        self.soundManager = SoundManager()
        self.soundManager.setup()
        self.soundManager.play_music("main")

        self.spellManager = SpellsManager(self)

        # Setup ui/menus
        self.ui = UI(self.screen)

    def setup_server(self):
        """
        Execute setup uniquement lors du lancement du programme mais server seulement
        Pour ne pas init les partie graphique inutile au serveur
        """
        self.client_manager = ClientManager(self)

    def setup_pygame(self):
        """Initialise pygame et crée la fenetre"""
        pygame.init()
        self.width, self.height = 1200, 800
        self.windowed_size = (self.width, self.height)
        desktop_sizes = pygame.display.get_desktop_sizes()
        if desktop_sizes:
            self.fullscreen_size = desktop_sizes[0]
        else:
            display_info = pygame.display.Info()
            self.fullscreen_size = (display_info.current_w, display_info.current_h)
        self.fullscreen = True
        self.screen = pygame.display.set_mode(self.fullscreen_size, pygame.NOFRAME)
        # Essayez de charger une icône pour la fenêtre (logo.png dans client/ressources)
        try:
            icon_path = os.path.normpath(
                os.path.join(os.path.dirname(__file__), "ressources", "logo.png")
            )
            self.icon_surface = pygame.image.load(icon_path)
            pygame.display.set_icon(self.icon_surface)
        except Exception as e:
            print("Warning: impossible de charger l'icône:", e)

        # self.screen = pygame.display.set_mode(
        #     (self.width, self.height), pygame.RESIZABLE
        # )
        pygame.display.set_caption("Avada Kedavoix")
        self.clock = pygame.time.Clock()
        self.clock.tick(60)
        self.running = True
        self.hold_for_loading_layer = False

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

        self.cameraBlackFade = CameraBlackFade()

        self.debug = False
        # self.base_ingame_time = time.time()
        # self.ingame_time = 0

    def back_to_main_menu(self):
        self.client_manager.close_connection()
        self.hold_for_loading_layer = False
        self.ui.hide_all()
        self.ui.show("MainMenu")

    def render(self):
        """Fait un rendu du jeu a executer a chaque tick"""
        t = time.time()
        if not self.running:
            self.quit()
            return

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            self.handle_event(event)

        self.handle_voice_event()

        self.screen.fill((0, 0, 0))  # Dessine le fond noir

        if self.hold_for_loading_layer:
            self.ui.loading()
        else:
            self.local_update()  # Met a jour les elements qui se mette a jour localement comme le joueur qui ses propres mouvements
            self.draw_elements()  # Dessine les elements de la scene
            self.ui.update()  # Dessine les elements des interfaces

        pygame.display.flip()  # Met a jour l'ecran

        self.deltatime = self.clock.tick(60)
        if self.debug:
            print(1 / (time.time() - t))
        # self.ingame_time = time.time() - self.base_ingame_time

    def set_to_quit(self):
        self.running = False

    def quit(self):
        self.client_manager.close_connection()
        pygame.quit()
        sys.exit()

    def handle_event(self, event):
        """
        Gere le evennements (ex: touches claviers, souris, ...)
        """
        if event.type == pygame.VIDEORESIZE:
            if not self.fullscreen:
                self.width, self.height = event.w, event.h
                self.windowed_size = (self.width, self.height)
            self.ui.on_resize()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                self.fullscreen = not self.fullscreen
                if self.fullscreen:
                    self.windowed_size = (self.width, self.height)
                    self.screen = pygame.display.set_mode(
                        self.fullscreen_size, pygame.NOFRAME
                    )
                else:
                    # la ligne juste en dessous permet de centré la fenetre quand on enleve le plein ecran
                    os.environ["SDL_VIDEO_CENTERED"] = "1"
                    self.screen = pygame.display.set_mode(
                        self.windowed_size, pygame.RESIZABLE
                    )
                self.ui.on_resize()

        self.ui.handle_event(event)  # Gere les evenement des elements des interfaces

        self.clientsElements.handle_event(event)

        for pnj in self.client_manager.game_state.pnjs.get_list():
            pnj.handle_event(event)

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
        for pnj in self.client_manager.game_state.pnjs.get_list():
            pnj.local_update()

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
        
        #Dessine les maisons
        House.draw_all(
            self.screen,
            offset,
            self.client_manager.game_state.houses.get_list(),
            active_world_layer=self.world_layer,
        )

        # Dessine les murs
        Wall.draw_all(
            self.screen,
            offset,
            self.client_manager.game_state.walls.get_list(),
            active_world_layer=self.world_layer,
        )

        if self.world_layer > Layer.OVERWORLD.value:
            self.cameraBlackFade.draw(
                self.screen,
                (self.screen.get_width() // 2, self.screen.get_height() // 2),
            )

        if (
            self.world_layer == Layer.OVERWORLD.value
            and self.client_manager.game_state.ingame_time != None
        ):
            # print(
            #     f"{(self.client_manager.game_state.ingame_time//60) //60}h {(self.client_manager.game_state.ingame_time//60)%60}min {(self.client_manager.game_state.ingame_time%60)}s"
            # )

            time_in_min = self.client_manager.game_state.ingame_time // 60
            time_in_s_night = self.client_manager.game_state.ingame_time % (
                60 * GameState.night_min
            )
            is_night = (
                time_in_min % (GameState.day_min + GameState.night_min)
                >= GameState.day_min
            )  # day_min min jour et night_min min nuit => cycle jour nuit
            if is_night:
                duration = 10.0  # en secondes durée transition jour/nuit et nuit/jour
                t = min(
                    min(1.0, (time_in_s_night) / duration),
                    min(1.0, (GameState.night_min * 60 - time_in_s_night) / duration),
                )

                intensity = min(0.4, ease_in_out(t))
                dark = pygame.Surface(self.screen.get_size()).convert()
                mul_value = int(255 * (1.0 - intensity))
                dark.fill(
                    (mul_value, mul_value, min(255, int(mul_value * 1.1)))
                )  # léger bleu
                self.screen.blit(dark, (0, 0), special_flags=pygame.BLEND_MULT)

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

        self.client_manager.send_changing_layer(target_layer_value)

        self.last_layer_switch_ms = now_ms
        return True
