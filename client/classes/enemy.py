"""
Classe pour la gestion des ennemis
"""

from typing import Tuple
import pygame
import time
from enum import Enum

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from client.classes.animator import Animator
from client.classes.clientOnly.healthBar import HealthBar
from client.classes.spell import Spell, SpellList
from client.layerList import Layer
from server.classes.serializable import Serializable
from client.classes.hitbox import HitBox

class EnemyList(Enum):
    GOBELIN_MASSUE = 1
    SKELETON = 2
    DRAGON = 3

class Enemy(Serializable):
    def __init__(
        self,
        x: float,
        y: float,
        color: tuple[int, int, int],
        size: int = 10,
        vx: float = 0,
        vy: float = 0,
        id: int = None,
        hp: int = 5,
        vitesse: int = 1,
        attack_delay: float = 5.0,
        world_layer: int | Layer = Layer.OVERWORLD,
        spell_type: SpellList = SpellList.PUNCH,
    ):
        self.id = id
        self.color = tuple(color)
        self.size = int(size)
        self.vitesse = vitesse

        # Vértable position envoyées au serveur
        self.x = float(x)
        self.y = float(y)

        # Pour gérer les mouvements stoque la vitesse
        self.vx = float(vx)
        self.vy = float(vy)

        # Position affiché
        self.display_x = float(x)
        self.display_y = float(y)

        # Pour l'interpolation
        self.target_x = float(x)
        self.target_y = float(y)
        self.interpolation_speed = 0.1
        self.min_threshold = 0.1

        self.hitbox_size = (25, 25)
        self.hitbox = HitBox(
            int(x), int(y), self.hitbox_size[0], self.hitbox_size[1], world_layer
        )

        # Pour gerer le systeme vie/degat
        self.hp = hp
        self.max_hp = hp

        # pour donner aux sorts et identifier le thrower
        self.THROWER_TYPE = "ennemy"
        self.world_layer = (
            world_layer.value if isinstance(world_layer, Layer) else int(world_layer)
        )

        self.attack_delay = float(attack_delay)
        self.prec_attack_time = time.time()
        self.spell_type = spell_type

        from server.managers.iaManager import Ia

        self.ia = Ia("enemy_ia", self)
        self.path = None
        self.next_pos_vect = (0, 0)

        # pour interagir avec le reste
        from client.gameManager import GameManager

        self.game_manager = GameManager()
        self.healthBar = HealthBar(y_offset=20)

        #pour les animations
        self.animator = Animator(
                size=(self.size * 5, self.size * 5), animation_speed=10 / 60
        )

        ennemy_type = ""
        match color:
            case (0, 255, 255)|(0, 255, 0):
                ennemy_type = "Gobelin_massue"
            case _:
                ennemy_type = "Dragon"

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
                "Ennemy",
                ennemy_type,
                "idle",
            ),
        )


    #! Server Side
    def do_attack(self, dir: Tuple[float, float]) -> None:
        """
        Methode du serveur car le serveur s'occupe de tout mettre a jour donc il gere l'envoie des projectiles
        """
        self.game_manager.spellManager.cast_spell_type(
            self.spell_type,
            thrower = self.THROWER_TYPE,
            x = self.x,
            y = self.y,
            dir = dir,
            world_layer = self.world_layer,
            player_id = None,
        )


    def take_dmg(self, dmg: int) -> None:
        self.hp -= dmg

    def is_dead(self) -> bool:
        return self.hp <= 0

    def server_update(self):
        # le set_target_position est automatique
        # actualises la position et les datas de l'ia
        self.ia.update()
        # Appliquer le mouvement horizontal
        self.hitbox.update(int(self.x + self.vx), int(self.y), self.world_layer)

        # Vérifier les collisions horizontales
        collided = self.hitbox.get_server_collided()
        if not collided:
            self.x += self.vx

        # Appliquer le mouvement vertical
        self.hitbox.update(int(self.x), int(self.y + self.vy), self.world_layer)

        # Vérifier les collisions verticales
        collided = self.hitbox.get_server_collided()
        if not collided:
            self.y += self.vy
        """
        self.x += self.vx
        self.y += self.vy
        """

    def interpolate_position(self):
        """Interpolation du mouvement vers le point cible"""
        x_diff = self.target_x - self.display_x
        y_diff = self.target_y - self.display_y

        if abs(x_diff) > self.min_threshold:
            self.display_x += x_diff * self.interpolation_speed
        else:
            self.display_x = self.target_x
        if abs(y_diff) > self.min_threshold:
            self.display_y += y_diff * self.interpolation_speed
        else:
            self.display_y = self.target_y

    def draw(self, surface, offset: tuple[float, float]):
        # Interpolation vers la position cible
        # Permet d'eviter les mouvements sacadé
        self.interpolate_position()

      #  pygame.draw.rect(
      #      surface,
      #      self.color,
      #      pygame.Rect(
      #          self.display_x + offset[0],
      #          self.display_y + offset[1],
      #          self.size,
      #          self.size,
      #      ),
      #  )

        pos = (self.display_x + offset[0], self.display_y + offset[1])
        self.animator.blit_sprite(surface, pos)

        self.hitbox.draw(surface, offset)
        self.healthBar.draw(
            surface,
            self.display_x + offset[0],
            self.display_y + offset[1],
            self.hp,
            self.max_hp,
        )


    def set_target_position(self, x, y):
        """
        Applique une interpolation lors de l'application des positions recu du serveur
        permettant d'éviter des mouvements sacadés
        """
        self.target_x = float(x)
        self.target_y = float(y)
        self.hitbox.update(int(x), int(y), self.world_layer)

    @staticmethod
    def draw_all(
            surface, offset: tuple[float, float],
            enemies: list["Enemy"],
            active_world_layer: int | None = None,
            ):
        """
        Dessine tout les ennemi
        """
        if enemies:
            if isinstance(enemies, list):
                for enemy in enemies:
                    if (
                        active_world_layer is not None
                        and enemy.world_layer != active_world_layer
                    ):
                        continue
                    enemy.draw(surface, offset)
            else:
                enemies.draw(surface, offset)

    @staticmethod
    def get_enemy_type(enemy_type: EnemyList, **keyargs):
        match enemy_type:
            case EnemyList.GOBELIN_MASSUE:
                return Enemy(color=(0,255,0), spell_type = SpellList.PUNCH, **keyargs)
            case EnemyList.DRAGON:
                return Enemy(color=(255,0,0), spell_type = SpellList.FIREBALL, **keyargs)
            case EnemyList.SKELETON:
                return Enemy(color=(100, 100, 100), spell_type = SpellList.BASIC, **keyargs)
            case _:
                return Enemy(color=(255,255,255), **keyargs)