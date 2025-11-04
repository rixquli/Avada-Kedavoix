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

    def get_all(self):
        return self.entities

    def get_list(self):
        return list(self.entities.values())

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

            # Si l'entite supporte l'interpolation, utiliser set_target_position
            if (
                hasattr(entity, "set_target_position")
                and "x" in entity_data
                and "y" in entity_data
            ):
                # Mettre à jour les autres propriétés d'abord (sauf position et vélocité)
                for key, value in entity_data.items():
                    if hasattr(entity, key):
                        setattr(entity, key, value)

                # Ensuite, définir la position cible pour l'interpolation (affichage fluide)
                # Cela met à jour target_x et target_y pour l'interpolation visuelle
                entity.set_target_position(entity_data["x"], entity_data["y"])
            else:
                # Sinon, mise à jour classique en replacant les ancienne valeur par les nouvelles
                # mais seulement si elles sont présente dans la nouvelle version sinon on garde
                # les données locales
                for key, value in entity_data.items():
                    if hasattr(entity, key):
                        setattr(entity, key, value)
        else:
            raise TypeError(f"entity_data doit être un Spell ou un dict")

    def to_dict(self):
        return {eid: entity.to_dict() for eid, entity in self.entities.items()}
