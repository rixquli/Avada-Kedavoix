"""
ClientManager permet la gestion du multijoueur mais coté client
et par extension le lancement d'une partie car meme une partie solo
correspond a un serveur avec un seul joueur
Ex:
    client_manager=ClientManager() # Creation d'une instance
    client_manager.startHosting()  # Lance l'hebergement d'une partie
"""

import os
import socket
import time
import sys
from _thread import *


# To import module from other folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from server.gameState import GameState
from server.NetworkManager import NetworkManager
from server.message import Message, MessageType
from server.main import start_game_server as server_main
from enum import Enum


class State(Enum):
    MAIN_MENU = 1
    SOLO = 2
    HOST = 3
    INVITED = 4


class ClientManager:
    def __init__(self):
        self.network = NetworkManager()
        self.game_state = GameState()
        self.my_player_id = None
        self.state = State.MAIN_MENU

        self.old_player_pos = None

    def get_player(self):
        return self.game_state.players.get(self.my_player_id)

    def connect_to_solo_server(self):
        self.my_player_id = self.network.connect_to_server(host="localhost")
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
                        # a partir de celles du serveur.
                        self.game_state.apply_state(
                            msg.data, my_player_id=self.my_player_id
                        )

            except Exception as e:
                print(f"Error: {e}")
                break

    def send_my_position(self):
        if self.my_player_id in self.game_state.players.entities:
            my_player = self.game_state.players.get(self.my_player_id)
            player_pos = [my_player.x, my_player.y]
            if self.old_player_pos != player_pos:
                msg = Message(MessageType.PLAYER_UPDATE, my_player.to_dict())
                self.network.send_message(msg)
                self.old_player_pos = player_pos

    def cast_spell(self, spell):
        # Ajouter localement
        spell_id = self.game_state.spells.addEntity(spell)

        # Envoyer au serveur pour les autres joueurs
        msg = Message(
            MessageType.PLAYER_CAST_SPELL,
            {"id": spell_id, "spell_data": spell.to_dict()},
        )
        self.network.send_message(msg)

    # Start Game Part

    def start_local_server(self, adress=None, port=None, max_player=5, is_solo=False):
        self.server_ready = False

        def run_server():
            try:
                print("Démarrage du serveur privé...")
                server_main(
                    adress=adress, port=port, max_player=max_player, is_solo=is_solo
                )
                self.server_ready = True
            except Exception as e:
                print(f"Erreur lors du démarrage du serveur: {e}")
                self.server_ready = True

        # Démarrer le serveur dans un thread
        start_new_thread(run_server, ())

    def startHosting(self, adress="0.0.0.0", port=12345):
        self.state = State.HOST

        self.start_local_server(adress, port)

        # Attendre que le serveur soit vraiment prêt
        timeout = time.time() + 10
        while time.time() < timeout:
            try:
                # Essaye de se connecter en boucle tant qu'il ne peut pas
                self.my_player_id = self.network.connect_to_server("localhost", port)
                if self.my_player_id:
                    print("Serveur prêt et connecté!")
                    break
            except:
                time.sleep(0.1)
        else:
            print("Timeout: impossible de se connecter au serveur")
            return

        start_new_thread(self.handle_reveice_message, ())

        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(f"Partie hébergée sur {local_ip}:{port}")
        print(f"Les autres joueurs peuvent rejoindre avec cette IP")

    def joinParty(self, host_ip, port=12345) -> bool:
        try:
            self.state = State.INVITED

            self.my_player_id = self.network.connect_to_server(host_ip, int(port))

            if self.my_player_id:
                print(f"Connecté à la partie de {host_ip}:{port}")
                start_new_thread(self.handle_reveice_message, ())
            else:
                print(f"Impossible de rejoindre {host_ip}:{port}")
                self.state = State.MAIN_MENU
                return False
            return True
        except:
            return False

    def startSinglePlayer(self):
        self.state = State.SOLO
        self.start_local_server(max_player=1, is_solo=True)
        # Attendre que le serveur soit vraiment prêt
        timeout = time.time() + 1
        while time.time() < timeout:
            try:
                # Essaye de se connecter en boucle tant qu'il ne peut pas
                self.my_player_id = self.connect_to_solo_server()
                if self.my_player_id:
                    print("Serveur prêt et connecté!")
                    break
            except:
                time.sleep(0.1)
        else:
            print("Timeout: impossible de se connecter au serveur")
            return
