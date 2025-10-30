import os
import pygame
import sys
from _thread import *


# To import module from other folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from client.classes.spell import Spell
from client.enums.anchor import Anchor
from client.clientManager import ClientManager
from client.ui.button import Button
from client.ui.text import Text
from client.ui.UI import UI
from client.ui.textInput import TextInput

client_manager = ClientManager()


def singlePlayerButtonClicked(ui, menu):
    ui.hide(menu)
    client_manager.startSinglePlayer()


def hostButtonClicked(ui, menu):
    ui.hide(menu)
    client_manager.startHosting()


def joinButtonClicked(ui, main_menu, join_menu):
    ui.hide(main_menu)
    ui.show(join_menu)


def joinGameButtonClicked(ui, menu, ip, port):
    ui.hide(menu)
    client_manager.joinParty(ip, port)


def main():
    pygame.init()
    width, height = 1920 / 2, 1080 / 2
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Avada Kedavoix")

    clock = pygame.time.Clock()
    running = True

    ui = UI(screen)
    menu = ui.createMenu("MainMenu")

    # Element du menu principal
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
        onclickFunction=lambda: singlePlayerButtonClicked(ui, menu),
        anchor=Anchor.CENTER,
    )
    start_hosting_player = Button(
        "HOST",
        250,
        50,
        (0, 0),
        onclickFunction=lambda: hostButtonClicked(ui, menu),
        anchor=Anchor.CENTER,
    )
    start_join_player = Button(
        "JOIN",
        250,
        50,
        (0, 100),
        onclickFunction=lambda: joinButtonClicked(ui, menu, "JoinMenu"),
        anchor=Anchor.CENTER,
    )

    # On les ajoute au menu principal
    ui.addTo(
        menu,
        [
            title,
            start_single_player,
            start_hosting_player,
            start_join_player,
        ],
    )

    # Création du mmenu join
    join_menu = ui.createMenu("JoinMenu", is_showing=False)

    address = ["", 0]

    def update_ip_address(new_address):
        address[0] = new_address

    def update_port(new_port):
        address[1] = new_port

    adress_input = TextInput(
        "Ip Address",
        (0, -100),
        200,
        50,
        onTextChanged=lambda x: update_ip_address(x),
        anchor=Anchor.CENTER,
        initial_text="127.0.0.1",
    )
    port_input = TextInput(
        "Port",
        (0, -50),
        200,
        50,
        onTextChanged=lambda x: update_port(x),
        anchor=Anchor.CENTER,
        initial_text="12345",
    )
    join_button = Button(
        "JOIN",
        100,
        50,
        (0, 50),
        onclickFunction=lambda: joinGameButtonClicked(
            ui, join_menu, address[0], address[1]
        ),
        anchor=Anchor.CENTER,
    )

    ui.addTo(
        join_menu,
        [title, adress_input, port_input, join_button],
    )

    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            client_manager.handle_event(event)
            ui.handle_event(event)

        screen.fill((0, 0, 0))

        client_manager.update(screen)
        ui.update()

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
