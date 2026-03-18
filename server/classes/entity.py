import pygame
import time

from client.classes.spell import Spell
from server.classes.serializable import Serializable
from client.classes.hitbox import HitBox

class Entity:
    def do_attack(self, dir: tuple[float, float]) -> None:
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
        # le set_target_position est automatique
        # actualises la position et les datas de l'ia
        self.ia.update()

        # Appliquer le mouvement horizontal
        self.hitbox.update(int(self.x + self.vx), int(self.y))

        # Vérifier les collisions horizontales
        collided = self.hitbox.get_collided()
        if not collided:
            self.x += self.vx

        # Appliquer le mouvement vertical
        self.hitbox.update(int(self.x), int(self.y + self.vy))

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

    def draw(self, surface, offset: tuple[float, float]):
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
    def draw_all(surface, offset: tuple[float, float], enemies: list["Enemy"]):
        """
        Dessine tout les ennemi
        """
        if enemies:
            if isinstance(enemies, list):
                for enemy in enemies:
                    enemy.draw(surface, offset)
            else:
                enemies.draw(surface, offset)

