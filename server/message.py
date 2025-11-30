"""
Message permet d'encapsuler les requetes entre les clients et le serveur
Elle permet de simplement trier les requetes par type (MessageType)

Une requete possede alors un type et un payload (données envoyées)
"""

from enum import Enum
from typing import TypedDict, Union, Literal, cast
import pickle
import struct


class MessageType(Enum):
    PLAYER_UPDATE = "player_update"
    GAME_STATE = "game_state"
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    PLAYER_CAST_SPELL = "spell"
    PLAYER_UPDATE_SPELL = "spell_update"

class PlayerUpdateData(TypedDict):
    x: float
    y: float

class GameStateData(TypedDict):
    enemies: list[str]

class ConnectData(TypedDict):
    player_id: str

class DisconnectData(TypedDict):
    reason: str

class SpellCastData(TypedDict):
    id: int

class SpellUpdateData(TypedDict):
    cooldown: float


class MessageBase(TypedDict):
    type: MessageType

class PlayerUpdateMessage(MessageBase):
    type: Literal[MessageType.PLAYER_UPDATE]
    data: PlayerUpdateData

class GameStateMessage(MessageBase):
    type: Literal[MessageType.GAME_STATE]
    data: GameStateData

class ConnectMessage(MessageBase):
    type: Literal[MessageType.CONNECT]
    data: ConnectData

class DisconnectMessage(MessageBase):
    type: Literal[MessageType.DISCONNECT]
    data: DisconnectData

class SpellCastMessage(MessageBase):
    type: Literal[MessageType.PLAYER_CAST_SPELL]
    data: SpellCastData

class SpellUpdateMessage(MessageBase):
    type: Literal[MessageType.PLAYER_UPDATE_SPELL]
    data: SpellUpdateData

MessageTyped = Union[
    PlayerUpdateMessage,
    GameStateMessage,
    ConnectMessage,
    DisconnectMessage,
    SpellCastMessage,
    SpellUpdateMessage,
]

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

    def as_typed(self) -> MessageTyped:
        # Pylance va correctement analyser le match sur self.type
        match self.type:
            case MessageType.PLAYER_UPDATE:
                return cast(MessageTyped, {"type": self.type, "data": self.data})
            case MessageType.GAME_STATE:
                return cast(MessageTyped, {"type": self.type, "data": self.data})
            case MessageType.CONNECT:
                return cast(MessageTyped, {"type": self.type, "data": self.data})
            case MessageType.DISCONNECT:
                return cast(MessageTyped, {"type": self.type, "data": self.data})
            case MessageType.PLAYER_CAST_SPELL:
                return cast(MessageTyped, {"type": self.type, "data": self.data})
            case MessageType.PLAYER_UPDATE_SPELL:
                return cast(MessageTyped, {"type": self.type, "data": self.data})

        raise ValueError("Unknown message type")
