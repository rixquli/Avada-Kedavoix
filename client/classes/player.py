from typing import List, Tuple
import pygame
from client.classes.hitbox import HitBox
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
        self.interpolation_speed = 0.5
        self.min_threshold = 0.1

        # Pour gerer les collisions
        #! Attention hibox_size sera envoyé au serveur mais pas hitbox (qui correspond a l'objet pygame de l'hitbox)
        self.hitbox_size = (25, 25)

        self.hitbox = HitBox(x, y, self.hitbox_size[0], self.hitbox_size[1])

    def update(self, keys=None):
        self.handle_input(keys)

        """
        Pour gerer les collision on va regarder les collision a la prochaine position sans l'appliquer a l'objet:
        Si on est dans un objet comme un mur alors on applique pas le mouvement dans cette direction
        Sinon si aucune collision n'est détectée a la prochaine position alors on applique le mouvement
        """
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

        # Mettre à jour la hitbox à la position finale
        self.hitbox.update(self.x, self.y)

        # Defini la target pour calculer l'interpolation
        self.set_target_position(self.x, self.y)

        # Interpolation vers la position cible
        self.interpolate_position()

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

    def draw(self, surface, offset: Tuple[float, float]):
        pygame.draw.circle(
            surface,
            self.color,
            (self.display_x + offset[0], self.display_y + offset[1]),
            self.radius,
        )

        self.hitbox.draw(surface, offset)

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
    def draw_all(
        surface,
        offset: Tuple[float, float],
        current_player: "Player",
        other_players: List["Player"],
    ):
        """
        Dessine met a jour tout les joueurs
        """
        if other_players:
            if isinstance(other_players, list):
                for player in other_players:
                    player.draw(surface, offset)
            else:
                other_players.draw(surface, offset)

        if current_player:
            current_player.draw(surface, offset)
