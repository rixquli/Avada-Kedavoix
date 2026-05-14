import time
import os
import pygame

from client.Utils.ImageTool import ImageTool
from server.classes.serializable import Serializable


class State(Serializable):
    def __init__(self, name, sprites_folder_path, size=(0, 0), animation_speed=1 / 30):
        self.name = name
        self.sprites_folder_path = sprites_folder_path
        self.sprites = []
        self.sprite_index = 0
        self.size = (int(size[0]), int(size[1]))
        self.animation_speed = animation_speed

        self.last_draw = None

        self._setup_sprites()

    def _setup_sprites(self):
        if not os.path.isdir(self.sprites_folder_path):
            raise FileNotFoundError(
                f"Sprites folder not found: {self.sprites_folder_path}"
            )

        exts = (".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp")
        files = [
            f
            for f in os.listdir(self.sprites_folder_path)
            if os.path.isfile(os.path.join(self.sprites_folder_path, f))
            and f.endswith(exts)
        ]
        files.sort()

        sprites = []

        try:
            for fname in files:
                path = os.path.join(self.sprites_folder_path, fname)
                img = ImageTool.load(path, self.size)
                if img is not None:
                    sprites.append(img)
        except Exception:
            print("Error parsing sprites")

        self.sprites = sprites

    def resize(self, new_size):
        self.size = new_size
        for img in self.sprites:
            img = pygame.transform.smoothscale(img, self.size)

    def get_sprite(self):
        t = time.time()
        if self.last_draw is None or t - self.last_draw > self.animation_speed:
            self.last_draw = t

            self.sprite_index = (self.sprite_index + 1) % len(self.sprites)
        return self.sprites[self.sprite_index]


class StateManager(Serializable):
    def __init__(self, animation_speed=1 / 30, size=(0, 0), default_state=None):
        self.size = size
        self.animation_speed = animation_speed

        self.states: dict[str, State] = {}

        self.default_state = default_state
        self.current_state = default_state

    def add_state(self, name, sprites_folder_path):
        self.states[name] = State(
            name,
            sprites_folder_path,
            size=self.size,
            animation_speed=self.animation_speed,
        )
        if self.default_state is None:
            self.default_state = name
        if self.current_state is None:
            self.current_state = name

    def get_current_sprite(self):
        if self.current_state is None or self.current_state not in self.states.keys():
            return None
        return self.states[self.current_state].get_sprite()

    def set_state(self, name):
        if (
            name == self.current_state
            or self.current_state is None
            or self.current_state not in self.states.keys()
        ):
            return None
        self.current_state = name


class Animator(Serializable):
    def __init__(
        self,
        animation_speed=15 / 60,
        size: tuple[int, int] = (0, 0),
        sprite_offset: tuple[float, float] = (0, 0),
        base_dir = -1 # la direction que regarde le personnage de base -1 pour la gauche et 1 pour la droite
    ):
        self.size = (int(size[0]), int(size[1]))
        self.animation_speed = animation_speed
        self.sprite_offset = sprite_offset
        self.base_dir = base_dir

        self.state_manager = StateManager(
            size=self.size, animation_speed=self.animation_speed
        )

        self.orientation = 1

    def set_state(self, state_name):
        self.state_manager.set_state(state_name)

    def flip_y(self, side):
        """
        Retourne l'image dans l'axe y selon le coté
        Arg:
            side: 'left' or 'right'
        """
        if side == "left":
            self.orientation = -self.base_dir
        else:
            self.orientation = self.base_dir

    def blit_sprite(self, surface, position):
        sprite = self.state_manager.get_current_sprite()
        if sprite is None:
            return
        position_with_sprite_offset = (
            position[0] + self.sprite_offset[0],
            position[1] + self.sprite_offset[1],
        )
        rect = sprite.get_rect(center=position_with_sprite_offset)

        if self.orientation == 1:
            surface.blit(sprite, rect)
        else:
            surface.blit(pygame.transform.flip(sprite, True, False), rect)

    # def _setup_state_sprites(self, state_name, folder_path):
