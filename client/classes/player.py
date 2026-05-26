"""
Classe pour la gestion des joueurs
gestion de l'objet afficher a l'ecran
et de la gestion des déplacement pour le joueur local
"""

import os
import sys
import time

from client.classes.clientOnly.healthBar import HealthBar

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from client.classes.animator import Animator
from client.layerList import Layer
import pygame
from client.classes.hitbox import HitBox
from server.classes.serializable import Serializable


class Player(Serializable):
    def __init__(
        self,
        x: float,
        y: float,
        color: tuple[int, int, int],
        radius: int = 10,
        vx: float = 0,
        vy: float = 0,
        vitesse: int = 5,
        id: int = None,
        hp: int = 10000000,
        world_layer: int | Layer = Layer.OVERWORLD,
        is_server: bool = False,
    ):
        self.id = id
        self.color = tuple(color)
        self.radius = int(radius)

        # Vértable position envoyées au serveur
        self.x = float(x)
        self.y = float(y)

        # Pour gérer les mouvements stoque la vitesse
        self.vx = float(vx)
        self.vy = float(vy)
        self.vitesse = vitesse

        # Position affiché
        self.display_x = float(x)
        self.display_y = float(y)

        # Pour l'interpolation
        self.target_x = float(x)
        self.target_y = float(y)
        self.interpolation_speed = 0.5
        self.min_threshold = 0.1

        # Pour gerer les collisions
        #! Attention hibox_size sera envoyé au serveur mais pas hitbox (qui correspond a l'objet pygame de l'hitbox)
        self.hitbox_size = (25, 25)
        self.hitbox = HitBox(
            int(x), int(y), self.hitbox_size[0], self.hitbox_size[1], world_layer
        )

        # Pour gerer le systeme vie/degat
        self.max_hp = hp
        self.hp = hp
        self.heal_amount = 25

        # pour donner aux sorts et identifier le thrower
        self.THROWER_TYPE = "player"
        self.world_layer = (
            world_layer.value if isinstance(world_layer, Layer) else int(world_layer)
        )

        # Pour les animations - uniquement côté client
        self.animator = None
        self.healthBar = None
        
        if not is_server:
            self._init_client_resources()

        # self.serveur_pos = None

        # Initialiser game_manager uniquement côté client
        self.game_manager = None
        if not is_server:
            from client.gameManager import GameManager
            self.game_manager = GameManager()

        self.pending_network_event = None

        self.invinsibility_timer = 2

    def is_dead(self) -> bool:
        return self.hp <= 0

    def _init_client_resources(self):
        """Initialise les ressources graphiques côté client"""
        if self.animator is not None:
            return  # Déjà initialisé
        
        # Pour les animations
        self.animator = Animator(
            size=(self.radius * 5, self.radius * 5), animation_speed=10 / 60, base_dir= 1
        )

        self.wizard_type = ""
        match self.color:
            case (255, 0, 0):
                self.wizard_type = "wizard_fire"
            case (0, 0, 255):
                self.wizard_type = "wizard_ice"
            case _:
                self.wizard_type = "wizard"

        # Chemin vers la racine du projet
        PROJECT_ROOT = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..")
        )

        self.animator.state_manager.add_state(
            "idle",
            os.path.join(
                PROJECT_ROOT,
                "client",
                "ressources",
                "wizzard-test",
                "PNG",
                self.wizard_type,
                "idle",
            ),
        )
        self.animator.state_manager.add_state(
            "walk",
            os.path.join(
                PROJECT_ROOT,
                "client",
                "ressources",
                "wizzard-test",
                "PNG",
                self.wizard_type,
                "walk",
            ),
        )
        self.animator.state_manager.add_state(
            "run",
            os.path.join(
                PROJECT_ROOT,
                "client",
                "ressources",
                "wizzard-test",
                "PNG",
                self.wizard_type,
                "run",
            ),
        )

        if self.healthBar is None:
            self.healthBar = HealthBar(y_offset=20)

    def take_dmg(self, dmg: int) -> None:
        """Cette fonction est gérée par le serveur"""
        if self.invinsibility_timer > 0:
            return
        self.hp -= dmg
        self.hp = max(self.hp, 0)
        if self.is_dead():
            print("dead")
            # self.serveur_pos = (0, 0, 1, time.time_ns())
            self.heal_max()
            self.pending_network_event = {
                "type": "respawn",
                "x": 0,
                "y": 0,
                "layer": 1,
                "hp": self.hp,
            }

    def heal(self, heal_amount=None):
        if heal_amount is None:
            heal_amount = self.heal_amount
        self.hp = min(self.max_hp, heal_amount + self.hp)

    def heal_max(self):
        self.hp = self.max_hp

    def teleport(self, x, y, world_layer: int):
        self.x = x
        self.y = y
        if world_layer != self.world_layer and self.game_manager is not None:
            self.game_manager.switch_player_layer(world_layer)

    def server_update(self):
        if self.invinsibility_timer > 0:
            self.invinsibility_timer -= 1 / 30

    def update(self, keys=None):
        self.handle_input(keys)

        """
        Pour gerer les collision on va regarder les collision a la prochaine position sans l'appliquer a l'objet:
        Si on est dans un objet comme un mur alors on applique pas le mouvement dans cette direction
        Sinon si aucune collision n'est détectée a la prochaine position alors on applique le mouvement
        """
        # if self.serveur_pos is not None:
        #     self.x = self.serveur_pos[0]
        #     self.y = self.serveur_pos[1]
        #     self.world_layer = self.serveur_pos[2]
        #     self.serveur_pos = None

        collided = self.hitbox.get_server_collided()
        if collided: # si l'entitée est deja dans un mur on ignore les collision jusqu'a qu'elle sorte 
            # Appliquer les mouvement sans vérifier collision 
            self.hitbox.update(int(self.x + self.vx), int(self.y + self.vy), self.world_layer)
            self.x += self.vx
            self.y += self.vy
        else :
            # Appliquer le mouvement horizontal
            self.hitbox.update(int(self.x + self.vx), int(self.y), self.world_layer)

            # Vérifier les collisions horizontales
            collided = self.hitbox.get_local_collided()
            if not collided:
                self.x += self.vx

            # Appliquer le mouvement vertical
            self.hitbox.update(int(self.x), int(self.y + self.vy), self.world_layer)

            # Vérifier les collisions verticales
            collided = self.hitbox.get_local_collided()
            if not collided:
                self.y += self.vy

        # Mettre à jour la hitbox à la position finale
        self.hitbox.update(int(self.x), int(self.y), self.world_layer)

        # Defini la target pour calculer l'interpolation
        self.set_target_position(self.x, self.y)

        # Interpolation vers la position cible
        self.interpolate_position()

    def interpolate_position(self):
        """Interpolation du mouvement vers le point cible"""
        self._init_client_resources()
        
        x_diff = self.target_x - self.display_x
        y_diff = self.target_y - self.display_y

        if x_diff > 0:
            self.animator.flip_y("right")
        elif x_diff < 0:
            self.animator.flip_y("left")

        if x_diff != 0 or y_diff != 0:
            self.animator.set_state("run")
        else:
            self.animator.set_state("idle")

        if abs(x_diff) > self.min_threshold:
            self.display_x += x_diff * self.interpolation_speed
        else:
            self.display_x = self.target_x
        if abs(y_diff) > self.min_threshold:
            self.display_y += y_diff * self.interpolation_speed
        else:
            self.display_y = self.target_y

    def handle_input(self, keys=None):
        if keys is None:
            return

        self._init_client_resources()

        self.vx = 0
        self.vy = 0

        import pygame

        if keys[pygame.K_UP] or keys[pygame.K_z]:
            self.vy = -self.vitesse
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.vy = self.vitesse
        if keys[pygame.K_LEFT] or keys[pygame.K_q]:
            self.vx = -self.vitesse
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = self.vitesse

        if self.vx > 0:
            self.animator.flip_y("right")
        elif self.vx < 0:
            self.animator.flip_y("left")

        if self.vx != 0 or self.vy != 0:
            self.animator.set_state("run")
        else:
            self.animator.set_state("idle")

    def draw(self, surface, offset: tuple[float, float]):
        self._init_client_resources()
        self.interpolate_position()
        # pygame.draw.circle(
        #     surface,
        #     self.color,
        #     (self.display_x + offset[0], self.display_y + offset[1]),
        #     self.radius,
        # )
        pos = (self.display_x + offset[0], self.display_y + offset[1])

        self.animator.blit_sprite(surface, pos)

        self.hitbox.draw(surface, offset)
        self.healthBar.draw(surface, pos[0], pos[1], self.hp, self.max_hp)

    def set_target_position(self, x, y):
        """
        Applique une interpolation lors de l'application des positions recu du serveur
        permettant d'éviter des mouvements sacadés
        """
        self.target_x = float(x)
        self.target_y = float(y)
        self.hitbox.update(int(x), int(y), self.world_layer)

    @staticmethod
    def update_local_player(current_player: "Player"):
        """
        Met a jour le joueur avec les touches préssées
        """
        keys = pygame.key.get_pressed()
        current_player.update(keys)

    @staticmethod
    def draw_all(
        surface,
        offset: tuple[float, float],
        current_player: "Player",
        other_players: list["Player"],
        active_world_layer: int | None = None,
    ):
        """
        Dessine met a jour tout les joueurs
        """
        if other_players:
            if isinstance(other_players, list):
                for player in other_players:
                    if (
                        active_world_layer is not None
                        and player.world_layer != active_world_layer
                    ):
                        continue
                    player.draw(surface, offset)
            else:
                other_players.draw(surface, offset)

        if current_player:
            if (
                active_world_layer is not None
                and current_player.world_layer != active_world_layer
            ):
                return
            current_player.draw(surface, offset)
