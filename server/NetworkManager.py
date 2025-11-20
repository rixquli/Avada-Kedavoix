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
from server.message import Message, MessageType


class NetworkManager:
    def __init__(self, address="0.0.0.0", port=12345, is_server=False):
        self.server_address = (address, port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.player_connections = {}
        self.is_server = is_server

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

    # Méthode du client
    def connect_to_server(self, host="0.0.0.0", port=12345):
        my_player_id = None
        try:
            self.socket.settimeout(5)
            self.socket.connect((host, port))
            print(f"Connected to {host}:{port}")

            # Attend de recevoir la validation et l'id du serveur
            msg = self.receive_message()

            if not msg:
                raise RuntimeError("Pas de messages reçus")

            msg_t = msg.as_typed()

            if msg_t["type"] == MessageType.CONNECT:
                my_player_id = msg_t["data"]["player_id"]
                if my_player_id:
                    print(f"Je suis le joueur {my_player_id}")
                    self.socket.settimeout(None)
                    return my_player_id
                else:
                    raise RuntimeError("player_id reçu est vide")
        except Exception as e:
            # print(f"Connection failed: {e}")
            return my_player_id

    # Méthodes du serveur et du client
    def send_message(self, message: Message):
        if self.socket:
            try:
                self.socket.sendall(message.serialize())
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

    def receive_message(self, conn: socket.socket | None = None):
        target = conn if conn else self.socket
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
