import os
import sys
from typing import List, Tuple, Type


# To import module from other folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from server.classes.serializable import Serializable


class EntityManager:
    def __init__(self, entity_type: Type[Serializable]):
        self.entity_type = entity_type
        self.entities = {}
        self.counter = 0

    def addEntity(
        self,
        entity: Serializable,
        fixed_id=None,
    ):
        if fixed_id is not None:
            id = fixed_id
        else:
            id = self.getId()
        entity.id = id
        self.entities[id] = entity
        return id

    def remove_local_only_entity(self, entities_from_server):
        """Supprime les entitées qui n'existe que localement"""
        """ex: un joueur s'est deconnecter il n'existe plus pour le serveur mais reste chez les clients"""
        if not isinstance(entities_from_server, dict):
            return
        entities_from_server_list = entities_from_server.keys()
        for id, _ in self.get_all().items():
            if id not in entities_from_server_list:
                self.remove(id)

    def remove(self, id: int):
        if id in self.entities:
            del self.entities[id]

    def getId(self):
        id = self.counter
        self.counter += 1
        return id

    def get(self, id):
        if id not in self.entities:
            return None
        return self.entities[id]

    def get_all(self):
        return self.entities

    def get_list(self):
        return list(self.entities.values())

    def get_local_entity(self):
        return self.filter_by()

    def filter_by(self, **kwargs) -> List[Serializable]:
        result = []
        for entity in self.entities.values():
            match = all(
                getattr(entity, key, None) == value for key, value in kwargs.items()
            )
            if match:
                result.append(entity)
        return result

    def update(self, entity_id, entity_data):
        if isinstance(entity_data, Serializable):
            self.entities[entity_id] = entity_data
        elif isinstance(entity_data, dict):
            self.entities[entity_id] = self.entity_type.from_dict(entity_data)
        else:
            raise TypeError(f"entity_data doit être un Spell ou un dict")

    def to_dict(self):
        return {eid: entity.to_dict() for eid, entity in self.entities.items()}
