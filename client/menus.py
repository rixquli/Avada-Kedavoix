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
import pygame

from client.ui.credit import Credit
from client.ui.dropdown import DropDownMenu
import pygame

from client.ui.dialogBox import DialogBox
from client.ui.ennemyLeftBar import EnnemyLeftBar
from client.ui.eventListener import UIEventListener
from client.ui.image import Image

from client.ui.image import Image
from client.ui.rect import UIRect

# To import module from other folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from client.ui.Loading.LoadingBar import LoadingBar
from client.enums.anchor import Anchor
from client.gameManager import GameManager
from client.ui.button import Button
from client.ui.text import Text
from client.ui.textInput import TextInput
from client.ui.hotbar import Hotbar

# Récupere l'instance du GameManager
game_manager = GameManager()

# Etat UI du HUD conservé entre les refresh.
hud_state = {"show_dialog": True}

solo_host_state = {"game_type": "solo"}

# Etat UI du Join Menu conservé entre les refresh.
join_menu_state = {"error_message": ""}

# Etat UI du Credit Menu conservé entre les refresh.
credit_menu_state = {"credit": None}

def back():
    game_manager.ui.show("MainMenu")

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
        solo_host_state["game_type"] = "solo"
        game_manager.ui.show("ContinueNewGameMenu")

    def hostButtonClicked():
        solo_host_state["game_type"] = "host"
        game_manager.ui.show("ContinueNewGameMenu")

    def joinButtonClicked():
        game_manager.ui.show("JoinMenu")

    def settingsButtonClicked():
        game_manager.ui.show("SettingsMenu")

    def creditButtonClicked():
        credit_menu_state["credit"] = None
        game_manager.ui.refresh("CreditMenu")
        game_manager.ui.show("CreditMenu")

    title = Text(
        "AVADA KEDAVOIX",
        (0, 100),
        font_size=100,
        color=(0, 0, 0),
        bg_alpha=0,
        width=1000,
        height=150,
        anchor=Anchor.MIDTOP,
        background=True,
        bg_border=False,
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
    start_settings = Button(
        "SETTINGS",
        250,
        50,
        (0, 200),
        onclickFunction=lambda: settingsButtonClicked(),
        anchor=Anchor.CENTER,
    )

    credit_btn = Button(
        "CREDIT",
        250,
        50,
        (0, 300),
        onclickFunction=lambda: close_and_exec(menu_name, creditButtonClicked),
        anchor=Anchor.CENTER,
    )
    quit_btn = Button(
        "QUIT",
        250,
        50,
        (0, 250),
        onclickFunction=game_manager.set_to_quit,
        anchor=Anchor.CENTER,
    )
    background = Image(
        path="UI/main_screen.png",
        width=game_manager.fullscreen_size[0],
        height=game_manager.fullscreen_size[1],
        position=(0, 0),
        anchor=Anchor.TOPLEFT,
    )

    return [
        background,
        title,
        start_single_player,
        start_hosting_player,
        start_join_player,
        start_settings,
        credit_btn,
        quit_btn,
        # Credit(),
    ]


def credit_menu(menu_name):
    def close_menu():
        credit_menu_state["credit"] = None
        game_manager.ui.show("MainMenu")

    if not credit_menu_state["credit"]:
        credit_menu_state["credit"] = Credit(
            lambda: close_and_exec(menu_name, close_menu)
        )

    if credit_menu_state["credit"]:
        return [credit_menu_state["credit"]]


def continue_new_game_menu(menu_name):
    def continue_btn():
        if solo_host_state["game_type"] == "solo":
            game_manager.client_manager.startSinglePlayer(newGame=False)
        else:
            game_manager.client_manager.startHosting(newGame=False)

    def new_btn():
        if solo_host_state["game_type"] == "solo":
            game_manager.client_manager.startSinglePlayer(newGame=True)
        else:
            game_manager.client_manager.startHosting(newGame=True)

    return [
        Image(
            path="UI/main_screen.png",
            width=game_manager.fullscreen_size[0],
            height=game_manager.fullscreen_size[1],
            position=(0, 0),
            anchor=Anchor.TOPLEFT,
        ),
        # title
        Text(
            "AVADA KEDAVOIX",
            (0, 100),
            font_size=100,
            color=(0, 0, 0),
            bg_alpha=0,
            width=1000,
            height=150,
            anchor=Anchor.MIDTOP,
            background=True,
            bg_border=False,
        ),
        Button(
            "CONTINUE GAME",
            300,
            50,
            position=(0, -50),
            onclickFunction=lambda: close_and_exec(menu_name, continue_btn),
            anchor=Anchor.CENTER,
        ),
        Button(
            "CREATE NEW GAME",
            300,
            50,
            position=(0, 50),
            onclickFunction=lambda: close_and_exec(menu_name, new_btn),
            anchor=Anchor.CENTER,
        ),
        Button(
            "Back",
            300,
            50,
            (0, 150),
            onclickFunction=lambda: close_and_exec(menu_name, back),
            anchor=Anchor.CENTER,
        ),
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
        join_menu_state["error_message"],
        (0, 200),
        color=(255, 0, 0),
        anchor=Anchor.CENTER,
        font_size=50,
        background=True,
        padding=(15, 15),
    )

    def joinGameButtonClicked():
        ip = adress[0]
        port = adress[1]
        have_joined = game_manager.client_manager.joinParty(ip, port)

        print("have_join: ", have_joined)

        if have_joined:
            # Remet un text vierge au cas ou
            join_menu_state["error_message"] = ""
            game_manager.ui.hide(menu_name)

            game_manager.ui.show("hud")
        else:
            # Met à jour le texte d'erreur
            join_menu_state["error_message"] = f"Error, can not join {ip}:{port}"
            # Rafraichir l'ui avec l'element d'erreur
            game_manager.ui.refresh(menu_name)

    return [
        Image(
            path="UI/main_screen.png",
            width=game_manager.fullscreen_size[0],
            height=game_manager.fullscreen_size[1],
            position=(0, 0),
            anchor=Anchor.TOPLEFT,
        ),
        # title
        Text(
            "AVADA KEDAVOIX",
            (0, 100),
            font_size=100,
            color=(0, 0, 0),
            bg_alpha=0,
            width=1000,
            height=150,
            anchor=Anchor.MIDTOP,
            background=True,
            bg_border=False,
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
        Button(
            "Back",
            100,
            50,
            (0, 100),
            onclickFunction=lambda: close_and_exec(menu_name, back),
            anchor=Anchor.CENTER,
        ),
        # text d'erreur réutilisable
        error_text,
    ]


def press_e(menu_name):
    return [
        Text(
            "PRESS E",
            (0, -150),
            font_size=50,
            color=(255, 255, 255),
            anchor=Anchor.MIDBOTTOM,
        ),
    ]

def hud(menu_name):
    print("Updating HUD")  # Debug print to check if the function is called
    elements = []
    player = game_manager.client_manager.get_player()

    if player is None:
        return elements

    wizard_type = player.wizard_type
    wizard_folder = {
        "fire": "wizard_fire",
        "ice": "wizard_ice",
    }.get(wizard_type, "wizard")

    PROJECT_ROOT = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
        )
    )
    path = os.path.join(
        "wizzard-test",
        "PNG",
        wizard_folder,
        "idle",
        "idle_1.png",
    )
    background = Image(
        path="UI/background.png",
        width=170,
        height=170,
        position=(5, -5),
        anchor=Anchor.BOTTOMLEFT,
    )
    avatar = Image(
        path=path,
        width=150,
        height=150,
        position=(15, -20),
        anchor=Anchor.BOTTOMLEFT,
    )
    hotbar = Hotbar(
        screen_width=game_manager.ui.screen.get_width(),
        screen_height=game_manager.ui.screen.get_height(),
    )
    settings_button = Button(
        "",
        50,
        50,
        (-10, 10),
        onclickFunction=open_settings,
        anchor=Anchor.TOPRIGHT,
        image_path="UI/settings_icon.png",
    )
    ennemyLeftBar = EnnemyLeftBar()

    elements.append(background)
    elements.append(avatar)
    elements.append(hotbar)
    elements.append(settings_button)
    elements.append(ennemyLeftBar)

    return elements


def dialog(menu_name):
    elements = []

    def closeDialog():
        # dialog.hide()
        # hud_state["show_dialog"] = False
        game_manager.ui.hide(menu_name)
        game_manager.ui.refresh(menu_name)

    # if hud_state["show_dialog"]:
    dialog = DialogBox(
        [{"name": "Jean Pormanov", "text": "Yokoso"}],
        position=(0, -10),
        close_callback=closeDialog,
    )

    elements.append(dialog)

    return elements


def loading(menu_name):
    return [LoadingBar(1000, 100, (0, 0), anchor=Anchor.CENTER)]


def settings(menu_name):
    return [
        UIRect(
            fullscreen=True,
            color=(0, 0, 0, 125),
            position=(0, 0),
            anchor=Anchor.CENTER,
        ),
        DropDownMenu(
            "quit",
            position=(0, 0),
            values=[("menu", game_manager.back_to_main_menu), ("quit", game_manager.set_to_quit)],
            width=250,
            heigth=75,
            values_width=250,
            values_heigth=75,
            anchor=Anchor.CENTER,
        ),
    ]

def open_settings():
    if game_manager.ui.menus["hud"].is_showing:
        game_manager.ui.show("settings")
        print("Opening settings menu")
    else:
        print("is not in game")

def settings_menu(menu_name):

    def back_to_main_menu():
        game_manager.ui.hide(menu_name)
        game_manager.ui.show("MainMenu")

    def quit_game():
        pygame.quit()
        sys.exit()

    return [

        Text(
            "SETTINGS",
            (0, 50),
            font_size=50,
            color=(255, 255, 255),
            anchor=Anchor.MIDTOP,
        ),

        Text(
            "MOVE UP : Z",
            (0, -100),
            font_size=30,
            color=(255, 255, 255),
            anchor=Anchor.CENTER,
        ),

        Text(
            "MOVE DOWN : S",
            (0, -50),
            font_size=30,
            color=(255, 255, 255),
            anchor=Anchor.CENTER,
        ),

        Text(
            "MOVE LEFT : Q",
            (0, 0),
            font_size=30,
            color=(255, 255, 255),
            anchor=Anchor.CENTER,
        ),

        Text(
            "MOVE RIGHT : D",
            (0, 50),
            font_size=30,
            color=(255, 255, 255),
            anchor=Anchor.CENTER,
        ),

        Button(
            "MAIN MENU",
            250,
            50,
            (0, 150),
            onclickFunction=back_to_main_menu,
            anchor=Anchor.CENTER,
        ),

        Button(
            "EXIT",
            250,
            50,
            (0, 225),
            onclickFunction=quit_game,
            anchor=Anchor.CENTER,
        ),
    ]


# Contient la liste de tout les menus accessibles dupuis GameManager().ui
# Pour en rajouter suivre les exemples deja presents
Menus = [
    {
        "name": "MainMenu",
        "content": main_menu,
        "is_showing": True,  # permet au menu d'apparaitre au demarage de l'app de base is_showing = False
    },
    {
        "name": "JoinMenu",
        "content": join_menu,  # Version sans le message d'erreur
    },
    {
        "name": "press_e",
        "content": press_e,
    },
    {
        "name": "hud",
        "content": hud,
        "is_showing": False,
    },
    {
        "name": "dialog",
        "content": dialog,
        "is_showing": False,
    },
    {
        "name": "loading",
        "content": loading,
        "is_showing": False,
    },
    {
        "name": "settings",
        "content": settings,
        "is_showing": False,
    },
    {
        "name": "CreditMenu",
        "content": credit_menu,
        "is_showing": False,
    },
    {
        "name": "ContinueNewGameMenu",
        "content": continue_new_game_menu,
        "is_showing": False,
    },
    {
    "name": "SettingsMenu",
    "content": settings_menu("SettingsMenu"),
    },
]
