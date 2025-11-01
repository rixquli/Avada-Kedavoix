import os
import socket
import time
import pygame
import sys
from _thread import *


# To import module from other folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from client.classes.enemy import Enemy
from client.classes.spell import Spell
from server.gameState import GameState
from server.NetworkManager import NetworkManager
from server.message import Message, MessageType
from client.classes.player import Player
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

    def get_player(self):
        return self.game_state.players.get(self.my_player_id)

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
            msg = Message(MessageType.PLAYER_UPDATE, my_player.to_dict())
            self.network.send_message(msg)

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

    def start_local_server(self, adress=None, port=None, max_player=5):
        def run_server():
            try:
                print("Démarrage du serveur privé...")
                server_main(adress=adress, port=port, max_player=max_player)
            except Exception as e:
                print(f"Erreur lors du démarrage du serveur: {e}")

        # Démarrer le serveur dans un thread
        start_new_thread(run_server, ())

        # Attendre que le serveur soit prêt
        time.sleep(1.5)

    def startHosting(self, adress="0.0.0.0", port=12345):
        self.state = State.HOST

        self.start_local_server(adress, port)

        # Se connecter à son propre serveur
        time.sleep(0.5)
        self.my_player_id = self.network.connect_to_server("localhost", port)

        start_new_thread(self.handle_reveice_message, ())

        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(f"Partie hébergée sur {local_ip}:{port}")
        print(f"Les autres joueurs peuvent rejoindre avec cette IP")

    def joinParty(self, host_ip, port=12345):
        self.state = State.INVITED

        self.my_player_id = self.network.connect_to_server(host_ip, int(port))

        if self.my_player_id:
            print(f"Connecté à la partie de {host_ip}:{port}")
            start_new_thread(self.handle_reveice_message, ())
        else:
            print(f"Impossible de rejoindre {host_ip}:{port}")
            self.state = State.MAIN_MENU

    def startSinglePlayer(self):
        self.state = State.SOLO
        self.start_local_server(max_player=1)
        self.my_player_id = self.connect_to_server()

    # Game Loop Part

    def update(self):
        match self.state:
            case State.SOLO | State.HOST | State.INVITED:
                # Pour eviter de mettre a jour dans le menu principal
                # Si besoin pour plus tard pour executer du code dans certains cas seulement
                pass
