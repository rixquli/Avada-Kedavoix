from pathlib import Path

import pygame


class ImageTool:
    load_buffer = {}

    @staticmethod
    def preload_images():
        files = sorted(Path("client/ressources").rglob("*.png")) + sorted(
            Path("client/ressources").rglob("*.jpg")
        )
        for img in files:
            ImageTool.load(img.relative_to("client"))

    @staticmethod
    def _resolve_texture_path(texture_path: str) -> str:
        """
        Résout un chemin de texture de façon robuste, quel que soit l'OS
        et le dossier courant d'exécution.
        """
        path = Path(texture_path)
        if path.is_file():
            return str(path)

        client_root = Path(__file__).resolve().parents[1]
        candidate = (client_root / texture_path).resolve()
        if candidate.is_file():
            return str(candidate)

        return texture_path

    @staticmethod
    def load(path: str, size: tuple[int, int] = (0, 0)) -> pygame.Surface:
        """
        Charge une image depuis un chemin et l'optimise pour pygame.
        Args:
            path: chemin vers l'image
            size: taille souhaitée, (0, 0) pour garder la taille originale
        """
        img_buffer = ImageTool.load_buffer.get(path, None)
        if img_buffer:
            if size and size[0] > 0 and size[1] > 0:
                return pygame.transform.smoothscale(img_buffer, size)
            return img_buffer

        path = ImageTool._resolve_texture_path(path)
        img = pygame.image.load(path)
        if size and size[0] > 0 and size[1] > 0:
            img = pygame.transform.smoothscale(img, size)
        try:
            img = img.convert_alpha()
        except Exception:
            img = img.convert()
        ImageTool.load_buffer[path] = img
        return img

    @staticmethod
    def scale(img: pygame.Surface, size: tuple[int, int]) -> pygame.Surface:
        """
        Redimensionne une image.
        Args:
            img: surface pygame à redimensionner
            size: nouvelle taille (largeur, hauteur)
        """
        return pygame.transform.smoothscale(img, size)

    @staticmethod
    def flip(
        img: pygame.Surface, flip_x: bool = False, flip_y: bool = False
    ) -> pygame.Surface:
        """
        Retourne une image horizontalement et/ou verticalement.
        Args:
            img: surface pygame
            flip_x: retourner sur l'axe horizontal
            flip_y: retourner sur l'axe vertical
        """
        return pygame.transform.flip(img, flip_x, flip_y)

    @staticmethod
    def blit_centered(
        surface: pygame.Surface, img: pygame.Surface, position: tuple[float, float]
    ):
        """
        Dessine une image centrée sur une position.
        Args:
            surface: surface de destination
            img: image à dessiner
            position: position du centre
        """
        rect = img.get_rect(center=position)
        surface.blit(img, rect)

    @staticmethod
    def blit(
        surface: pygame.Surface, img: pygame.Surface, position: tuple[float, float]
    ):
        """
        Dessine une image depuis son coin supérieur gauche.
        Args:
            surface: surface de destination
            img: image à dessiner
            position: position du coin supérieur gauche
        """
        surface.blit(img, position)
