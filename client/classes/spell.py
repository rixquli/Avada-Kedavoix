"""
Classe pour la gestion des spells (sorts)
"""

import os
import time
import math
from enum import Enum

import pygame

from client.classes.animator import Animator
from client.layerList import Layer
from server.classes.serializable import Serializable
from client.classes.hitbox import HitBox


class SpellList(Enum):
    FIREBALL = 1
    ICE = 2
    HEAL = 3
    TELEPORTATION = 4
    PUNCH = 5
    BASIC = 6
    DARK_FIREBALL = 7


class Spell(Serializable):
    def __init__(
        self,
        x: float,
        y: float,
        player_id: int | None,
        color: tuple[int, int, int],
        dir: tuple[float, float],
        radius: int = 10,
        id: int = None,
        lifetime: float = 5.0,
        dmg: int = 1,
        thrower: str = "Enemy",
        speed: float = 20.0,
        world_layer: int | Layer = Layer.OVERWORLD,
        is_server: bool = False,
    ):
        self.id = id
        self.x = float(x)
        self.y = float(y)
        self.player_id = player_id
        self.color = tuple(color)
        self.dir = tuple(dir)
        self.radius = int(radius)
        self.lifetime = float(lifetime)
        self.creation_time = time.time()
        self.speed = float(speed)
        self.world_layer = (
            world_layer.value if isinstance(world_layer, Layer) else int(world_layer)
        )

        # Position affiché
        self.display_x = float(x)
        self.display_y = float(y)

        # Pour l'interpolation
        self.target_x = float(x)
        self.target_y = float(y)
        self.interpolation_speed = 0.5
        self.min_threshold = 0.01

        self.hitbox_size = (radius * 2, radius * 2)
        self.hitbox = HitBox(
            int(x), int(y), self.hitbox_size[0], self.hitbox_size[1], world_layer
        )

        # Pour gerer le systeme vie/degat
        self.dmg = int(dmg)

        # pour savoir a qui ne pas infliger de degat
        self.thrower = thrower

        self.spell_type = None
        match color:
            case (255, 0, 0):
                self.spell_type = SpellList.FIREBALL
            case (200, 200, 200):
                self.spell_type = SpellList.PUNCH
            case (0, 0, 255):
                self.spell_type = SpellList.ICE
            case (0, 0, 0):
                self.spell_type = SpellList.DARK_FIREBALL
            case _:
                self.spell_type = SpellList.BASIC

        # pour les animations
        # si l'anim existe
        self.animator = None
        self.spell_type = None
        match color:
            case (255, 0, 0):
                self.spell_type = SpellList.FIREBALL
            case (200, 200, 200):
                self.spell_type = SpellList.PUNCH
            case (0, 0, 255):
                self.spell_type = SpellList.ICE
            case (0, 0, 0):
                self.spell_type = SpellList.DARK_FIREBALL
            case _:
                self.spell_type = SpellList.BASIC

        # init l'animator côté client seulement
        self.sprite_base_angle = 180  # 0 si regarde à droite, 180 si regarde à gauche
        if not is_server and self.spell_type in [SpellList.FIREBALL, SpellList.ICE, SpellList.DARK_FIREBALL]:
            self._init_client_resources()

    def _init_client_resources(self):
        """Initialise les ressources graphiques côté client"""
        if self.animator is not None:
            return  # Déjà initialisé

        # Chemin vers la racine du projet
        PROJECT_ROOT = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..")
        )
        self.animator = Animator(
            size=(self.radius *2 , self.radius *2), animation_speed=10 / 60
        )
        self.animator.state_manager.add_state(
            "idle",
            os.path.join(
                PROJECT_ROOT,
                "client",
                "ressources",
                "Sorts",
                self.spell_type.name,
            ),
        )

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

    def set_target_position(self, x: float, y: float):
        """
        Applique une interpolation lors de l'application des positions recu du serveur
        permettant d'éviter des mouvements sacadés
        """
        self.target_x = float(x)
        self.target_y = float(y)
        self.hitbox.update(int(x), int(y), self.world_layer)

    def server_update(self):
        # le set_target_position est automatique
        # potentielle ia a ajouter (si nessecaire)
        self.x += self.dir[0] * self.speed
        self.y += self.dir[1] * self.speed

        self.hitbox.update(int(self.x), int(self.y), self.world_layer)

    def is_expired(self) -> bool:
        """Verifie si le sort a depasse sa duree de vie"""
        return time.time() - self.creation_time > self.lifetime

    def draw(self, surface, offset: tuple[float, float]):
        # si le sort est punch on ne le dessine pas
        if self.spell_type == SpellList.PUNCH:
            self.hitbox.draw(surface, offset)
            return
        # Interpolation vers la position cible
        # Permet d'eviter les mouvements sacadé
        self._init_client_resources()
        self.interpolate_position()

        if not self.animator:
            pygame.draw.circle(
                surface,
                self.color,
                (int(self.display_x + offset[0]), int(self.display_y + offset[1])),
                self.radius,
            )
        else:
            pos = (self.display_x + offset[0], self.display_y + offset[1])

            sprite = self.animator.state_manager.get_current_sprite()
            if sprite is not None:
                # pour tourner le spirte dans la direction ou il se dirige
                angle = (
                    -math.degrees(math.atan2(self.dir[1], self.dir[0]))
                    + self.sprite_base_angle
                )
                rotated_sprite = pygame.transform.rotate(sprite, angle)
                rect = rotated_sprite.get_rect(center=pos)
                surface.blit(rotated_sprite, rect)
            else:
                self.animator.blit_sprite(surface, pos)

        self.hitbox.draw(surface, offset)

    @staticmethod
    def draw_all(
        surface,
        offset: tuple[float, float],
        all_spells: list["Spell"],
        active_world_layer: int | None = None,
    ):
        """
        Dessine tout les spells
        """
        if all_spells:
            if isinstance(all_spells, list):
                for spell in all_spells:
                    if (
                        active_world_layer is not None
                        and spell.world_layer != active_world_layer
                    ):
                        continue
                    spell.draw(surface, offset)
            else:
                all_spells.draw(surface, offset)

    @staticmethod
    def get_spell_type(spell_type: SpellList, dmg_mult: int = 1, **keyargs):
        match spell_type:
            case SpellList.FIREBALL:
                return Spell(radius=10, color=(255, 0, 0), dmg=10 * dmg_mult, **keyargs)
            case SpellList.DARK_FIREBALL:
                return Spell(radius=10, color=(0, 0, 0), **keyargs)
            case SpellList.ICE:
                return Spell(radius=15, color=(0, 0, 255), **keyargs)
            case SpellList.PUNCH:
                return Spell(
                    radius=15,
                    color=(200, 200, 200),
                    speed=15,
                    lifetime=0.25,
                    dmg=15 * dmg_mult,
                    **keyargs,
                )
            case _:
                return Spell(
                    radius=8, color=(50, 150, 255), dmg=5 * dmg_mult, **keyargs
                )
