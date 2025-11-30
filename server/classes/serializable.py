"""
Chaque classe doit hériter de Serializable cela permet de convertir plus simplement les données
du joueur ou du pnj en dictionnaire pour les envoyer au serveur ou au client.
Cela permet de ne pas envoyer des données inutiles elle agit aussi comme un filtre
en empechant d'envoyer des objet pygame complexe au serveur qui ne ferait que ralentir le serveur

Ex:
    joueur = Player(...)
    dico = joueur.to_dict()
"""

import inspect
import json
from typing import Any, Dict


class Serializable:
    """
    super classe pour les joueurs/ enemy/ spell ...
    permet d'effectuer des transformation d'objet a dictionnaireet inversement
    """
    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'objet en dictionnaire, en excluant les attributs non-sérialisables"""
        data = {}

        # Attributs à toujours exclure (objets Pygame, etc.)
        exclude = {
            "hitbox",  # HitBox (objet Pygame)
            "game_manager",  # Singleton GameManager
            "image",  # Surface Pygame
            "rect",  # Rect Pygame
        }

        for key, value in self.__dict__.items():
            # Ignorer les attributs privés et ceux à exclure
            if not key.startswith("_") and key not in exclude:
                # Vérifier si la valeur est sérialisable
                if self._is_serializable(value):
                    data[key] = value

        return data

    def _is_serializable(self, value) -> bool:
        """Vérifie si une valeur peut être sérialisée en JSON"""
        try:
            json.dumps(value)
            return True
        except (TypeError, ValueError):
            return False

    @classmethod
    def from_dict(cls, data):
        sig = inspect.signature(cls.__init__)
        params = {}

        for param_name in sig.parameters:
            if param_name == "self":
                continue

            if param_name in data:
                value = data[param_name]

                param_annotation = sig.parameters[param_name].annotation
                if "Tuple" in str(param_annotation) and isinstance(value, list):
                    value = tuple(value)

                params[param_name] = value
            elif sig.parameters[param_name].default != inspect.Parameter.empty:
                params[param_name] = sig.parameters[param_name].default

        return cls(**params)
