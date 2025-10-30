from enum import Enum
import pickle


class MessageType(Enum):
    PLAYER_UPDATE = "player_update"
    GAME_STATE = "game_state"
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    PLAYER_CAST_SPELL = "spell"


class Message:
    def __init__(self, msg_type: MessageType, data):
        self.type = msg_type
        self.data = data

    def serialize(self) -> bytes:
        return pickle.dumps({"type": self.type.value, "data": self.data})

    @staticmethod
    def deserialize(data: bytes) -> "Message":
        obj = pickle.loads(data)
        return Message(MessageType(obj["type"]), obj["data"])
