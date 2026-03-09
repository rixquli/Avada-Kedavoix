"""
Pour simplifier l'utilisation des menus/interfaces,
tous les menus et interfaces doivent etre dans la liste Menus

Pour en rajouter suivre les exemples deja present
ATTENTION: "content": fonction_qui_renvoie_la_liste_des_elements("NomDuMenu")

Ex:
    game_manager=GameManager()
    game_manager.ui.show("MainMenu") # affiche le menu principal present dans Menus
"""

import os
import sys

from client.ui.image import Image


# To import module from other folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from client.enums.anchor import Anchor
from client.gameManager import GameManager
from client.ui.button import Button
from client.ui.text import Text
from client.ui.textInput import TextInput

# Récupere l'instance du GameManager
game_manager = GameManager()


# fonction auxiliaire utilisé plus bas
def close_and_exec(menu_name, function, *params):
    """
    Exécute une fonction puis ferme un menu d'interface utilisateur.
    Appelle la fonction fournie en lui passant les paramètres fournis, puis masque
    le menu identifié par `menu_name` via game_manager.ui.hide.
    """
    if params:
        function(*params)
    else:
        function()
    game_manager.ui.hide(menu_name)


def main_menu(menu_name):
    """
    Fontion qui créer le Main Menu avec tout les evennements liés aux boutons
    """

    def singlePlayerButtonClicked():
        game_manager.client_manager.startSinglePlayer()

    def hostButtonClicked():
        game_manager.client_manager.startHosting()

    def joinButtonClicked():
        game_manager.ui.show("JoinMenu")

    title = Text(
        "AVADA KEDAVOIX",
        (0, 50),
        font_size=50,
        color=(255, 255, 255),
        anchor=Anchor.MIDTOP,
    )
    start_single_player = Button(
        "SOLO",
        250,
        50,
        (0, -100),
        onclickFunction=lambda: close_and_exec(menu_name, singlePlayerButtonClicked),
        anchor=Anchor.CENTER,
    )
    start_hosting_player = Button(
        "HOST",
        250,
        50,
        (0, 0),
        onclickFunction=lambda: close_and_exec(menu_name, hostButtonClicked),
        anchor=Anchor.CENTER,
    )
    start_join_player = Button(
        "JOIN",
        250,
        50,
        (0, 100),
        onclickFunction=lambda: close_and_exec(menu_name, joinButtonClicked),
        anchor=Anchor.CENTER,
    )
    background = Image(
        path="client/ressources/UI/main_screen.png",
        width=1920,
        height=1080,
        position=(0, 0),
        anchor=Anchor.TOPLEFT,
    )

    return [
        background,
        title,
        start_single_player,
        start_hosting_player,
        start_join_player,
    ]


def join_menu(menu_name):
    """
    Fontion qui créer le Join Menu avec tout les evennements liés aux boutons
    """

    adress = ["", 0]

    def set_val(index, val):
        adress[index] = val

    # Text d'erreur vide au depart
    error_text = Text(
        "",  # texte vide -> pas d'affichage initial
        (0, -50),
        color=(255, 0, 0),
        anchor=Anchor.MIDBOTTOM,
    )

    def joinGameButtonClicked():
        ip = adress[0]
        port = adress[1]
        have_joined = game_manager.client_manager.joinParty(ip, port)

        if have_joined:
            # Remet un text vierge au cas ou
            error_text.change_text("")
            game_manager.ui.hide(menu_name)
        else:
            # Met à jour le texte d'erreur
            error_text.change_text(f"Error, can not join {ip}:{port}")
            # Rafraichir l'ui avec l'element d'erreur
            game_manager.ui.refresh(menu_name)

    return [
        # title
        Text(
            "AVADA KEDAVOIX",
            (0, 50),
            font_size=50,
            color=(255, 255, 255),
            anchor=Anchor.MIDTOP,
        ),
        # adress_input
        TextInput(
            "Ip Address",
            (0, -100),
            200,
            50,
            onTextChanged=lambda x: set_val(0, x),
            anchor=Anchor.CENTER,
            initial_text="127.0.0.1",
        ),
        # port_input
        TextInput(
            "Port",
            (0, -50),
            200,
            50,
            onTextChanged=lambda x: set_val(1, x),
            anchor=Anchor.CENTER,
            initial_text="12345",
        ),
        # join_button
        Button(
            "JOIN",
            100,
            50,
            (0, 50),
            onclickFunction=lambda: joinGameButtonClicked(),
            anchor=Anchor.CENTER,
        ),
        # text d'erreur réutilisable
        error_text,
    ]


# Contient la liste de tout les menus accessibles dupuis GameManager().ui
# Pour en rajouter suivre les exemples deja presents
Menus = [
    {
        "name": "MainMenu",
        "content": main_menu("MainMenu"),
        "is_showing": True,  # permet au menu d'apparaitre au demarage de l'app de base is_showing = False
    },
    {
        "name": "JoinMenu",
        "content": join_menu("JoinMenu"),  # Version sans le message d'erreur
    },
]
