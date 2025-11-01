from typing import List, Tuple
import pygame
from server.classes.serializable import Serializable


class Player(Serializable):
    def __init__(
        self,
        x: float,
        y: float,
        color: Tuple[int, int, int],
        radius: int = 10,
        vx: float = 0,
        vy: float = 0,
        id: int = None,
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

        # Position affiché
        self.display_x = float(x)
        self.display_y = float(y)

        # Pour l'interpolation
        self.target_x = float(x)
        self.target_y = float(y)
        self.interpolation_speed = 0.1

    def update(self, keys=None):
        self.handle_input(keys)

        self.x += self.vx
        self.y += self.vy
        # Interpolation vers la position cible
        self._interpolate_position()

    def _interpolate_position(self):
        """Interpolation du mouvement vers le point cible"""
        self.display_x += (self.target_x - self.display_x) * self.interpolation_speed
        self.display_y += (self.target_y - self.display_y) * self.interpolation_speed

    def handle_input(self, keys=None):
        if keys is None:
            return

        speed = 5
        self.vx = 0
        self.vy = 0

        import pygame

        if keys[pygame.K_UP] or keys[pygame.K_z]:
            self.vy = -speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.vy = speed
        if keys[pygame.K_LEFT] or keys[pygame.K_q]:
            self.vx = -speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = speed

    def draw(self, surface):
        pygame.draw.circle(
            surface, self.color, (int(self.display_x), int(self.display_y)), self.radius
        )

    def set_target_position(self, x, y):
        """
        Applique une interpolation lors de l'application des positions recu du serveur
        permettant d'éviter des mouvements sacadés
        """
        self.target_x = float(x)
        self.target_y = float(y)

    @staticmethod
    def update_local_player(current_player: "Player"):
        """
        Met a jour le joueur avec les touches préssées
        """
        keys = pygame.key.get_pressed()
        current_player.update(keys)

    @staticmethod
    def draw_all(surface, current_player: "Player", other_players: List["Player"]):
        """
        Dessine met a jour tout les joueurs
        """
        if other_players:
            if isinstance(other_players, list):
                for player in other_players:
                    player.draw(surface)
            else:
                other_players.draw(surface)

        if current_player:
            current_player.draw(surface)
