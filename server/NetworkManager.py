import os
import socket
from _thread import *
import sys

# To import module from other folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from server.message import Message, MessageType


class NetworkManager:
    def __init__(self, address="localhost", port=12345, is_server=False):
        self.server_address = (address, port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.player_connections = {}
        self.is_server = is_server

    # Methodes du serveur
    def start_server(self, address=None, port=None):
        if not self.is_server:
            return

        server_adress = list(self.server_address)

        if address is not None:
            server_adress[0] = address

        if port is not None:
            server_adress[1] = port

        try:
            self.socket.bind(tuple(server_adress))
            self.socket.listen(5)
            print("Waiting for connection, Server Started")

        except Exception as e:
            print(f"Error connecting to server: {e}")

    # Méthode du client
    def connect_to_server(self, host="localhost", port=12345):
        my_player_id = None
        try:
            self.socket.settimeout(5)
            self.socket.connect((host, port))
            print(f"Connected to {host}:{port}")

            # Attend de recevoir la validation et l'id du serveur
            msg = self.receive_message()
            if msg and msg.type == MessageType.CONNECT:
                my_player_id = msg.data["player_id"]
                print(f"Je suis le joueur {my_player_id}")
                self.socket.settimeout(None)
                return my_player_id
        except Exception as e:
            print(f"Connection failed: {e}")
            return my_player_id

    # Méthodes du serveur et du client
    def send_message(self, message: Message):
        if self.socket:
            try:
                self.socket.sendall(message.serialize())
            except Exception as e:
                print(f"Send error: {e}")

    def receive_message(self, conn=None):
        target = conn if conn else self.socket
        if target:
            try:
                data = target.recv(4096)
                if data:
                    return Message.deserialize(data)
            except Exception as e:
                print(f"Receive error: {e}")
        return None
