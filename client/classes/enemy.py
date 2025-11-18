"""
Classe pour la gestion des ennemis
"""

from typing import List, Tuple

import pygame
import time

from client.classes.spell import Spell
from server.classes.serializable import Serializable
from client.classes.hitbox import HitBox


class Enemy(Serializable):
    def __init__(
        self,
        x: float,
        y: float,
        color: Tuple[int, int, int],
        size: int = 10,
        vx: float = 0,
        vy: float = 0,
        id: int = None,
        hp: int = 1,
        vitesse: int = 1,
        attack_delay: float = 5.0
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
        self.hitbox = HitBox(x, y, self.hitbox_size[0], self.hitbox_size[1])

        # Pour gerer le systeme vie/degat
        self.hp = hp

        # pour donner aux sorts et identifier le thrower
        self.THROWER_TYPE = "ennemy"

        self.attack_delay = float(attack_delay)
        self.prec_attack_time = time.time()

        from server.managers.iaManager import Ia
        self.ia = Ia("enemy_ia",self)
        self.path = None

        #pour interagir avec le reste
        from client.gameManager import GameManager
        self.game_manager = GameManager()

    def do_attack(self, dir: Tuple[float, float]) -> None:
        spell = Spell(
                x=self.x,
                y=self.y,
                player_id=None,
                color=(50, 150, 255),
                dir=dir,
                radius=4,
                thrower=self.THROWER_TYPE,
                speed=2
            )

        self.game_manager.client_manager.cast_spell(spell)

    def take_dmg(self,dmg: int) -> None:
        self.hp -= dmg

    def is_dead(self) -> bool:
        return self.hp <= 0

    def server_update(self):
        # TODO: Ajouter l'ia ici pour le comportement des créatures
        self.ia.update()
        # Appliquer le mouvement horizontal
        self.hitbox.update(self.x + self.vx, self.y)

        # Vérifier les collisions horizontales
        collided = self.hitbox.get_collided()
        if not collided:
            self.x += self.vx

        # Appliquer le mouvement vertical
        self.hitbox.update(self.x, self.y + self.vy)

        # Vérifier les collisions verticales
        collided = self.hitbox.get_collided()
        if not collided:
            self.y += self.vy

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

    def draw(self, surface, offset: Tuple[float, float]):
        # Interpolation vers la position cible
        # Permet d'eviter les mouvements sacadé
        self.interpolate_position()

        pygame.draw.rect(
            surface,
            self.color,
            pygame.Rect(
                self.display_x + offset[0],
                self.display_y + offset[1],
                self.size,
                self.size,
            ),
        )

    def set_target_position(self, x, y):
        """
        Applique une interpolation lors de l'application des positions recu du serveur
        permettant d'éviter des mouvements sacadés
        """
        self.target_x = float(x)
        self.target_y = float(y)

    @staticmethod
    def draw_all(surface, offset: Tuple[float, float], enemies: List["Enemy"]):
        """
        Dessine tout les ennemi
        """
        if enemies:
            if isinstance(enemies, list):
                for enemy in enemies:
                    enemy.draw(surface, offset)
            else:
                enemies.draw(surface, offset)
