import os
import pygame
import sys
from _thread import *

# To import module from other folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from server.message import Message, MessageType
from client.classes.player import Player


class ClientManager:
    def __init__(self, network, game_manager):
        self.network = network
        self.game_manager = game_manager
        self.my_player_id = None

    def connect_to_server(self):
        self.my_player_id = self.network.connect_to_server()
        start_new_thread(self.handle_reveice_message, ())
        return self.my_player_id

    def handle_reveice_message(self):
        while True:
            try:
                # Attend de recevoir des message de ce player
                msg = self.network.receive_message()

                if not msg:
                    break

                # La liste des messages traités
                match msg.type:
                    case MessageType.GAME_STATE:
                        # Met a jour les donnes de l'environnement local
                        # a partir de celles du serveur
                        for player_id, player_data in msg.data["players"].items():
                            # Ne pas écraser les données du joueur local
                            if player_id == self.my_player_id:
                                # Si le joueur local n'existe pas encore, on le crée
                                if (
                                    player_id
                                    not in self.game_manager.playersManager.players
                                ):
                                    player = Player(
                                        player_data["x"],
                                        player_data["y"],
                                        player_data["color"],
                                        player_data["radius"],
                                    )
                                    player.vx = player_data.get("vx", 0)
                                    player.vy = player_data.get("vy", 0)
                                    self.game_manager.playersManager.players[
                                        player_id
                                    ] = player
                                # Sinon on garde la position locale (pas de mise à jour)
                            else:
                                # Mettre à jour les autres joueurs
                                player = Player(
                                    player_data["x"],
                                    player_data["y"],
                                    player_data["color"],
                                    player_data["radius"],
                                )
                                player.vx = player_data.get("vx", 0)
                                player.vy = player_data.get("vy", 0)
                                self.game_manager.playersManager.players[player_id] = (
                                    player
                                )

            except Exception as e:
                print(f"Error: {e}")
                break

    def send_my_position(self):
        if self.my_player_id in self.game_manager.playersManager.players:
            my_player = self.game_manager.playersManager.players[self.my_player_id]
            msg = Message(MessageType.PLAYER_UPDATE, my_player)
            self.network.send_message(msg)

    def cast_spell(self, spell, intensity):
        msg = Message(
            MessageType.PLAYER_CAST_SPELL, {"spell": spell, "intensity": intensity}
        )
        self.network.send_message(msg)
