from pathlib import Path

import pygame

CLIENT_ROOT = Path(__file__).resolve().parents[1]
ASSETS_ROOT = CLIENT_ROOT / "ressources"


class SoundManager:
    def __new__(cls):
        """
        Permet de creer un singleton qui permet d'acceder aux valeurs et methodes
        de cette classe depuis n'importe ou
        """
        if not hasattr(cls, "instance"):
            cls.instance = super(SoundManager, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        """
        Executer __init__ apres chaque definition local du SoundManager
        """
        pass

    def setup(self):
        self.enabled = True
        # sounds = dico avec {sfx: {"nom": son}, music: {"nom": son}}
        self.sounds = {}

        self.master = 1
        self.sfx = 1
        self.music = 1

        try:
            pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
            pygame.mixer.init()

            self.sounds["sfx"] = self.preload_all_sfx_sounds()
            self.sounds["music"] = self.preload_all_music_sounds()
        except:
            self.enabled = False

    def load(self, path: str):
        try:
            path = SoundManager._resolve_texture_path(str(path))
            return pygame.mixer.Sound(path)
        except:
            return None

    def load_music(self, path: str):
        try:
            path = SoundManager._resolve_texture_path(str(path))
            return pygame.mixer.music.load(path)
        except:
            return None

    def preload_all_sfx_sounds(self):
        files = sorted(Path("client/ressources/sounds/sfx").rglob("*.mp3"))
        sfx_dico = {}
        for sound_file in files:
            snd = self.load(str(sound_file.relative_to("client")))
            snd.set_volume(self.master * self.sfx)
            sfx_dico[sound_file.stem] = snd
        return sfx_dico

    def preload_all_music_sounds(self):
        files = sorted(Path("client/ressources/sounds/music").rglob("*.mp3"))
        music_dict = {}
        for sound_file in files:
            music_dict[sound_file.stem] = str(sound_file.relative_to("client"))
        return music_dict

    def play_sfx(self, name):
        print("play: ", name)
        if self.enabled and name in self.sounds["sfx"]:
            self.sounds["sfx"][name].play()

    def play_music(self, name, loops=-1):
        if not self.enabled:
            return

        if name not in self.sounds["music"]:
            return

        path = self._resolve_texture_path(self.sounds["music"][name])
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(self.master * self.music)
        pygame.mixer.music.play(loops=loops)

    def set_volumes(self, master=None, sfx=None, music=None):
        if master is not None:
            self.master = max(0.0, min(1.0, master))
        if sfx is not None:
            self.sfx = max(0.0, min(1.0, sfx))
        if music is not None:
            self.music = max(0.0, min(1.0, music))

        for snd in self.sounds.values():
            snd.set_volume(self.master * self.sfx)
        pygame.mixer.music.set_volume(self.master * self.music)

    @staticmethod
    def _resolve_texture_path(texture_path: str) -> str:
        """
        Résout un chemin de texture de façon robuste, quel que soit l'OS
        et le dossier courant d'exécution.
        """
        texture_path = str(texture_path).replace("\\", "/")

        for prefix in ("client/ressources/", "ressources/"):
            if texture_path.startswith(prefix):
                texture_path = texture_path[len(prefix) :]
                break

        path = Path(texture_path)
        if path.is_file():
            return str(path)

        candidate = (ASSETS_ROOT / texture_path).resolve()
        if candidate.is_file():
            return str(candidate)
        else:
            raise FileNotFoundError(f"Asset introuvable: {candidate}")
