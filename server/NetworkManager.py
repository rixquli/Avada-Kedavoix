"""
Classe qui s'occupe du serveur sockets, la partie server
et aussi connect_to_server permettant de se connecter a celui-ci
"""

import os
import socket
from _thread import *
import struct
import sys

# To import module from other folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from server.gameState import GameState
from server.message import Message, MessageType


class NetworkManager:
    def __new__(cls):
        """
        Permet de creer un singleton qui permet d'acceder aux valeurs et methodes
        de cette classe depuis n'importe ou
        """
        if not hasattr(cls, "instance"):
            cls.instance = super(NetworkManager, cls).__new__(cls)
        return cls.instance

    def setup(self, address="0.0.0.0", port=12345, is_server=False):
        self.server_address = (address, port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.player_connections = {}
        self.is_server = is_server
        self.game_state = GameState()

    # Methodes du serveur
    def start_server(self, address=None, port=None, max_player=5, is_solo=False):
        if not self.is_server:
            return

        server_adress = list(self.server_address)

        if address is not None:
            server_adress[0] = address

        if port is not None:
            server_adress[1] = port

        try:
            self.socket.bind(tuple(server_adress))
            self.socket.listen(max_player)
            print("Waiting for connection, Server Started")
            print(
                f"Serveur accessible localement à: {server_adress[0]}:{server_adress[1]}"
            )

        except Exception as e:
            print(f"Error connecting to server: {e}")

        return tuple(server_adress)

    def close_server(self):
        self.socket.close()

    # Méthode du client
    def connect_to_server(self, host="0.0.0.0", port=12345):
        my_player_id = None
        try:
            # Créer un nouveau socket pour le client (séparé du socket serveur)
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.settimeout(5)
            self.client_socket.connect((host, port))
            print(f"Connected to {host}:{port}")

            # Attend de recevoir la validation et l'id du serveur
            msg = self.receive_message(self.client_socket)
            if msg and msg.type == MessageType.CONNECT:
                my_player_id = msg.data["player_id"]
                print(f"Je suis le joueur {my_player_id}")
                self.client_socket.settimeout(None)
                return my_player_id
        except Exception as e:
            # print(f"Connection failed: {e}")
            return my_player_id

    def close_client_socket(self):
        if hasattr(self, "client_socket"):
            self.client_socket.close()

    # Méthodes du serveur et du client
    def send_message(self, message: Message):
        # Utiliser client_socket si disponible (mode client), sinon socket (fallback)
        target = getattr(self, "client_socket", None) or self.socket
        if target:
            try:
                target.sendall(message.serialize())
            except Exception as e:
                print(f"Send error: {e}")

    def extract_header(self, conn: socket.socket, size):
        data = b""
        while len(data) < size:
            packet = conn.recv(size - len(data))
            if not packet:
                raise ConnectionError("Connection closed while receiving data")
            data += packet
        return data

    def receive_message(self, conn=None):
        # Si conn n'est pas fourni, utiliser client_socket (mode client) ou socket
        target = conn if conn else (getattr(self, "client_socket", None) or self.socket)
        if target:
            try:
                header = self.extract_header(target, 4)
                if not header:
                    return None

                message_size = struct.unpack(">I", header)[0]

                data = self.extract_header(target, message_size)
                if data:
                    return Message.deserialize(data)
            except Exception as e:
                # print(f"Receive error: {e}")
                return
        return None
