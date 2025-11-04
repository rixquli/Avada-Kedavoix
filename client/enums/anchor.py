"""
Enum (liste) des valeurs possible pour les points d'ancrages
un point d'ancrage permet de placer un objet par rapport a ce point
Utilisation:
    Anchor.VALEUR
Ex:
    Text(
            text="AVADA KEDAVOIX",
            position=(0, 50),
            anchor=Anchor.MIDTOP,
        ),
    Pemet de placer un texte au centre et au milieu de l'ecran mais décaler de 50 pixel vers le bas
"""

from enum import Enum


class Anchor(Enum):
    TOPLEFT = "topleft"
    MIDTOP = "midtop"
    TOPRIGHT = "topright"
    MIDLEFT = "midleft"
    CENTER = "center"
    MIDRIGHT = "midright"
    BOTTOMLEFT = "bottomleft"
    MIDBOTTOM = "midbottom"
    BOTTOMRIGHT = "bottomright"
