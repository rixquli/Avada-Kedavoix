"""
Classe pour la gestion des pnj
"""

import math

import pygame
from client.layerList import Layer
from server.classes.serializable import Serializable
from client.classes.hitbox import HitBox


class PNJ(Serializable):
    def __init__(
        self,
        x: float,
        y: float,
        color: tuple[int, int, int],
        size: int = 10,
        vx: float = 0,
        vy: float = 0,
        id: int = None,
        hp: int = 1,
        text="",
        name="",
        world_layer: int | Layer = Layer.OVERWORLD,
    ):
        self.id = id
        self.color = tuple(color)
        self.size = int(size)

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

        # Pour IA
        from server.managers.iaManager import Ia

        self.ia = Ia("pnj_ia", self)
        self.x_target = float(x)
        self.y_target = float(y)
        self.dist = 0
        self.dir_x = 0
        self.dir_y = 0

        self.hitbox_size = (10, 10)
        self.hitbox = HitBox(
            int(x), int(y), self.hitbox_size[0], self.hitbox_size[1], world_layer
        )

        # Pour gerer le systeme vie/degat
        self.hp = hp
        self.world_layer = (
            world_layer.value if isinstance(world_layer, Layer) else int(world_layer)
        )

        self.text = text
        self.name = name

        from client.gameManager import GameManager

        self.game_manager = GameManager()
        self.distance_trigger = 50
        self.shown = False

    def is_dead(self) -> bool:
        return self.hp <= 0

    def local_update(self):
        current_player = self.game_manager.client_manager.game_state.players.get(
            self.game_manager.client_manager.my_player_id
        )
        if not current_player:
            return

        if current_player.world_layer != self.world_layer:
            return

        distance = abs(
            math.sqrt(
                (current_player.x - self.x) ** 2 + (current_player.y - self.y) ** 2
            )
        )
        if (
            distance < self.distance_trigger
            and current_player.world_layer == self.world_layer
        ):
            self.shown = True
            self.game_manager.ui.show("press_e")
        elif self.shown:
            self.shown = False
            self.game_manager.ui.hide("press_e")

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

        # Mettre à jour la hitbox à la position finale
        self.hitbox.update(int(self.x), int(self.y), self.world_layer)

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

        # Dessine un losange (carré tourné de 45°) centré sur display_x/display_y + size/2
        cx = self.display_x + self.size / 2 + offset[0]
        cy = self.display_y + self.size / 2 + offset[1]
        half = self.size / 2
        points = [
            (int(cx), int(cy - half)),  # haut
            (int(cx + half), int(cy)),  # droite
            (int(cx), int(cy + half)),  # bas
            (int(cx - half), int(cy)),  # gauche
        ]
        pygame.draw.polygon(surface, self.color, points)
        self.hitbox.draw(surface, offset)

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
        surface,
        offset: tuple[float, float],
        pnjs: list["PNJ"],
        active_world_layer: int | None = None,
    ):
        """
        Dessine tout les pnj
        """
        if pnjs:
            if isinstance(pnjs, list):
                for pnj in pnjs:
                    if (
                        active_world_layer is not None
                        and pnj.world_layer != active_world_layer
                    ):
                        continue
                    pnj.draw(surface, offset)
            else:
                pnjs.draw(surface, offset)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            current_player = self.game_manager.client_manager.game_state.players.get(
                self.game_manager.client_manager.my_player_id
            )
            if not current_player:
                return

            if current_player.world_layer != self.world_layer:
                return

            distance = abs(
                math.sqrt(
                    (current_player.x - self.x) ** 2 + (current_player.y - self.y) ** 2
                )
            )
            if (
                distance < self.distance_trigger
                and current_player.world_layer == self.world_layer
            ):
                # Passer le nom et le texte du NPC au dialogue avant de l'afficher
                # Convertir self.text en liste si c'est une string
                self.game_manager.ui.set_dialog_data("dialog", self.text)
                self.game_manager.ui.show("dialog")
