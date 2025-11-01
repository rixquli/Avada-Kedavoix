# To import module from other folder
import os
import sys


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from client.enums.anchor import Anchor
from client.gameManager import GameManager
from client.ui.button import Button
from client.ui.text import Text
from client.ui.textInput import TextInput

game_manager = GameManager()


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

    return [
        title,
        start_single_player,
        start_hosting_player,
        start_join_player,
    ]


def join_menu(menu_name):
    adress = ["", 0]

    def set_val(index, val):
        adress[index] = val

    def joinGameButtonClicked(ip, port):
        print(ip)
        print(port)
        game_manager.client_manager.joinParty(ip, port)

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
            onclickFunction=lambda: close_and_exec(
                menu_name, joinGameButtonClicked, adress[0], adress[1]
            ),
            anchor=Anchor.CENTER,
        ),
    ]


Menus = [
    # Contient la liste de menus pour en rajouter suivre les exemples deja presents
    {
        "name": "MainMenu",
        "content": main_menu("MainMenu"),
        "is_showing": True,  # permet au menu d'apparaitre au demarage de l'app de base is_showing = False
    },
    {
        "name": "JoinMenu",
        "content": join_menu("JoinMenu"),
    },
]
