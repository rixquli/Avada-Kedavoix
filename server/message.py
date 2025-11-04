"""
Message permet d'encapsuler les requetes entre les clients et le serveur
Elle permet de simplement trier les requetes par type (MessageType)

Une requete possede alors un type et un payload (données envoyées)
"""

from enum import Enum
import pickle
import struct


class MessageType(Enum):
    PLAYER_UPDATE = "player_update"
    GAME_STATE = "game_state"
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    PLAYER_CAST_SPELL = "spell"
    PLAYER_UPDATE_SPELL = "spell_update"


class Message:
    def __init__(self, msg_type: MessageType, data):
        self.type = msg_type
        self.data = data

    def serialize(self) -> bytes:
        payload = pickle.dumps({"type": self.type.value, "data": self.data})
        size = len(payload)
        header = struct.pack(">I", size)
        return header + payload

    @staticmethod
    def deserialize(data: bytes) -> "Message":
        obj = pickle.loads(data)
        return Message(MessageType(obj["type"]), obj["data"])
