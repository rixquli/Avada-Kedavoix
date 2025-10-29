import os
import pygame
import sys
from _thread import *


# To import module from other folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from server.NetworkManager import NetworkManager
from server.gameManager import GameManager
from client.clientManager import ClientManager

network = NetworkManager()
game_manager = GameManager()
client_manager = ClientManager(network, game_manager)


def draw(surface, currentPlayer, otherPlayers):
    """Dessine le joueur local et tous les autres joueurs"""
    keys = pygame.key.get_pressed()

    if otherPlayers:
        if isinstance(otherPlayers, list):
            for player in otherPlayers:
                player.draw(surface)
        else:
            otherPlayers.draw(surface)

    currentPlayer.update(keys)
    currentPlayer.draw(surface)

    pygame.display.flip()


def main():
    pygame.init()
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Avada Kedavoix")

    clock = pygame.time.Clock()
    running = True

    my_player_id = client_manager.connect_to_server()

    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))

        # Dessine met a jour tout les joueurs
        if my_player_id in game_manager.playersManager.players:
            currentPlayer = game_manager.playersManager.getPlayer(my_player_id)
            otherPlayers = game_manager.playersManager.getOtherPlayers(my_player_id)
            draw(screen, currentPlayer, otherPlayers)

            # Envoyer ma position
            client_manager.send_my_position()

    pygame.quit()


if __name__ == "__main__":
    main()
