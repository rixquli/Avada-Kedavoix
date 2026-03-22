"""
Classe qui gere tout un type d'entité comme les joueurs ou les njs (voir gameState.py)
elle permet de gerer/mettre a jour toutes les entités du meme type et auusi d'en rajouter/supprimer
"""

import os
import sys
from typing import List, Tuple, Type
import uuid


# To import module from other folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from server.classes.serializable import Serializable


class EntityManager:
    def __init__(self, entity_type: Type[Serializable]):
        self.entity_type = entity_type
        self.entities = {}

    def addEntity(
        self,
        entity: Serializable,
        fixed_id=None,
    ):
        if fixed_id is not None:
            entity_id = str(fixed_id)
        else:
            entity_id = str(uuid.uuid4())
        entity.id = entity_id
        self.entities[entity_id] = entity
        return entity_id

    def remove_local_only_entity(self, entities_from_server):
        """
        Supprime les entitées qui n'existe que localement
        ex: un joueur s'est deconnecter il n'existe plus pour le serveur mais reste chez les clients
        """
        if not isinstance(entities_from_server, dict):
            return
        entities_from_server_list = entities_from_server.keys()

        to_delete = []
        for id, _ in self.get_all().items():
            if id not in entities_from_server_list:
                to_delete.append(id)

        for id in to_delete:
            self.remove(id)

    def remove(self, id: str):
        if id in self.entities:
            del self.entities[id]

    def get(self, id):
        if id not in self.entities:
            return None
        return self.entities[id]

    def get_except_list(self, id):
        """
        Renvoie une liste des élément qui ont un id différent du paramètre
        """
        return [e for e in self.get_list() if e.id != id]

    def get_except_list_layer(self, id, layer):
        """
        Renvoie une liste des élément qui ont un id différent du paramètre
        """
        return [e for e in self.get_list() if e.id != id and e.world_layer == layer]


    def get_all(self):
        return self.entities

    def get_list(self):
        return list(self.entities.values())

    def get_list_layer(self, layer):
        return [entity for entity in self.entities.values() if entity.world_layer == layer]

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
            if entity_id not in self.entities:
                # Si l'entité n'existe pas, la créer
                self.entities[entity_id] = self.entity_type.from_dict(entity_data)
                return

            entity = self.entities[entity_id]

            # Mise à jour classique: remplacer les anciennes valeurs par les nouvelles
            # mais seulement si elles sont présentes dans la nouvelle version.
            for key, value in entity_data.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)

            # Si l'entité supporte l'interpolation, il faut aussi gérer les mises à jour
            # partielles (x seul ou y seul) envoyées via diff_to_dict().
            if hasattr(entity, "set_target_position") and (
                "x" in entity_data or "y" in entity_data
            ):
                entity.set_target_position(entity.x, entity.y)

            # Cote serveur, garantir que la hitbox suit toujours la position logique
            # meme quand les updates recues sont partielles.
            if (
                hasattr(entity, "hitbox")
                and hasattr(entity, "x")
                and hasattr(entity, "y")
                and hasattr(entity.hitbox, "update")
            ):
                world_layer = getattr(entity, "world_layer", entity.hitbox.world_layer)
                entity.hitbox.update(int(entity.x), int(entity.y), world_layer)
        else:
            raise TypeError(f"entity_data doit être un Spell ou un dict")

    def to_dict(self, diff):
        return {eid: entity.to_dict(diff) for eid, entity in self.entities.items()}

    def diff_to_dict(self):
        return {eid: entity.diff_to_dict() for eid, entity in self.entities.items()}
