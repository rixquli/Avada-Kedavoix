import os
import socket
import time
import pygame
import sys
from _thread import *


# To import module from other folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from client.classes.spell import Spell
from server.gameManager import GameManager
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
        self.game_manager = GameManager()
        self.my_player_id = None
        self.state = State.MAIN_MENU

    def get_player(self):
        return self.game_manager.players.get(self.my_player_id)

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
                        self.game_manager.apply_state(msg.data)
                        # for player_id, player_data in msg.data["players"].items():
                        #     # Ne pas écraser les données du joueur local
                        #     if player_id == self.my_player_id:
                        #         # Si le joueur local n'existe pas encore, on le crée
                        #         if player_id not in self.game_manager.players.entities:
                        #             player = Player(
                        #                 player_data["x"],
                        #                 player_data["y"],
                        #                 player_data["color"],
                        #                 player_data["radius"],
                        #             )
                        #             player.vx = player_data.get("vx", 0)
                        #             player.vy = player_data.get("vy", 0)
                        #             self.game_manager.players.update(player_id, player)
                        #         # Sinon on garde la position locale (pas de mise à jour)
                        #     else:
                        #         # Mettre à jour les autres joueurs
                        #         player = Player(
                        #             player_data["x"],
                        #             player_data["y"],
                        #             player_data["color"],
                        #             player_data["radius"],
                        #         )
                        #         player.vx = player_data.get("vx", 0)
                        #         player.vy = player_data.get("vy", 0)
                        #         self.game_manager.players.update(player_id, player)

                        # # On traite les données des spells recues depuis le serveur
                        # for spell_id, spell_data in msg.data["spells"].items():
                        #     if not spell_data:
                        #         # Sort inexistant, on le supprime
                        #         if spell_id in self.game_manager.spells.entities:
                        #             self.game_manager.spells.remove(spell_id)
                        #         continue

                        #     spell_player_id = spell_data.get("player_id")

                        #     # Si c'est un autre joueur qui a lancé le sort alors
                        #     # On le fait apparaitre si non existant sinon on le met a jour
                        #     if spell_player_id != self.my_player_id:
                        #         if spell_id not in self.game_manager.spells.entities:
                        #             self.game_manager.spells.addEntity(
                        #                 Spell(
                        #                     spell_data["x"],
                        #                     spell_data["y"],
                        #                     spell_data["player_id"],
                        #                     spell_data["color"],
                        #                     spell_data["dir"],
                        #                     spell_data["radius"],
                        #                 )
                        #             )
                        #         else:
                        #             self.game_manager.spells.update(
                        #                 spell_id, spell_data
                        #             )
                    # case MessageType.PLAYER_CAST_SPELL:

            except Exception as e:
                print(f"Error: {e}")
                break

    def send_my_position(self):
        if self.my_player_id in self.game_manager.players.entities:
            my_player = self.game_manager.players.get(self.my_player_id)
            msg = Message(MessageType.PLAYER_UPDATE, my_player.to_dict())
            self.network.send_message(msg)

    def cast_spell(self, spell):
        spell_id = self.game_manager.spells.addEntity(
            Spell(
                spell.x,
                spell.y,
                self.my_player_id,
                spell.color,
                spell.dir,
                spell.radius,
            )
        )
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
        time.sleep(1.5)
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

    # Draw Part

    def drawPlayer(self, surface, currentPlayer, otherPlayers):
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

    def updatePlayers(self, screen):
        # Dessine met a jour tout les joueurs
        if self.my_player_id in self.game_manager.players.entities:
            all_players = self.game_manager.players.get_list()
            currentPlayer = self.game_manager.players.get(self.my_player_id)
            otherPlayers = [
                player for player in all_players if player.id != self.my_player_id
            ]
            self.drawPlayer(screen, currentPlayer, otherPlayers)

            # Envoyer ma position
            self.send_my_position()

    def drawSpell(self, surface, player_spells, other_player_spells):
        if other_player_spells:
            if isinstance(other_player_spells, list):
                for spell in other_player_spells:
                    spell.draw(surface)
            else:
                other_player_spells.draw(surface)

        if isinstance(player_spells, list):
            for spell in player_spells:
                spell.draw(surface)
                spell.update()
        else:
            player_spells.draw(surface)
            player_spells.update()

    def send_my_spells_position(self):
        my_spells = self.game_manager.spells.filter_by(player_id=self.my_player_id)
        spells_dict = {spell.id: spell.to_dict() for spell in my_spells}
        msg = Message(MessageType.PLAYER_UPDATE_SPELL, spells_dict)
        self.network.send_message(msg)

    def updateSpells(self, screen):
        # Dessine met a jour tout les joueurs
        all_spells = self.game_manager.spells.get_list()

        player_spells = [s for s in all_spells if s.player_id == self.my_player_id]
        other_player_spells = [
            s for s in all_spells if s.player_id != self.my_player_id
        ]
        self.drawSpell(screen, player_spells, other_player_spells)

        # Envoyer la position de mes sorts
        self.send_my_spells_position()

    def update(self, screen):
        match self.state:
            case State.SOLO | State.HOST | State.INVITED:
                self.updatePlayers(screen)
                self.updateSpells(screen)
