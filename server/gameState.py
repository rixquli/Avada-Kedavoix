import os
import sys
import time

from client.classes.pnj import PNJ


# To import module from other folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from client.classes.enemy import Enemy
from client.classes.player import Player
from client.classes.spell import Spell
from server.managers.entityManager import EntityManager


class GameState:
    def __init__(self):
        self.players = EntityManager(Player)
        self.spells = EntityManager(Spell)
        self.enemies = EntityManager(Enemy)
        self.pnjs = EntityManager(PNJ)

    def get_game_state(self):
        """Retourne l'état complet du jeu pour le broadcast"""
        return {
            "players": self.players.to_dict(),
            "spells": self.spells.to_dict(),
            "enemies": self.enemies.to_dict(),
            "pnjs": self.pnjs.to_dict(),
        }

    def update_all(self):
        for spell in list(self.spells.entities.values()):
            if spell.is_expired():
                self.spells.remove(spell.id)
            else:
                spell.update()
        for enemy in list(self.enemies.entities.values()):
            enemy.update()
        for pnj in list(self.pnjs.entities.values()):
            pnj.update()

    def apply_state(self, state, my_player_id=None):
        """Applique les mises à jour venant du serveur"""
        self.apply_state_for(state, "players", self.players, my_player_id=my_player_id)
        self.apply_state_for(state, "enemies", self.enemies)
        self.apply_state_for(state, "spells", self.spells)
        self.apply_state_for(state, "pnjs", self.pnjs)

    def apply_state_for(self, state, name, entities, my_player_id=None):
        for id, data in state.get(name, {}).items():
            if not data:
                # si l'entité n'existe plus on le supprime
                entities.remove(str(id))
            elif str(id) not in entities.entities:
                # si l'entité n'existe pas localement on l'ajoute
                entity = entities.entity_type.from_dict(data)
                entities.addEntity(entity, fixed_id=str(id))
            else:
                # si l'entité existe localement on le met a jour
                if my_player_id and str(id) == str(my_player_id):
                    # Pour le joueur local, on garde x, y, vx, vy calculés localement
                    # On met à jour seulement les autres propriétés
                    filtered_data = {
                        k: v
                        for k, v in data.items()
                        if k
                        not in [
                            "x",
                            "y",
                            "vx",
                            "vy",
                            "display_x",
                            "display_y",
                            "target_x",
                            "target_y",
                        ]
                    }
                    if filtered_data:
                        entities.update(str(id), filtered_data)
                else:
                    entities.update(str(id), data)
        # Verifie si tout les elements ont bien ete supprimer cote client
        entities.remove_local_only_entity(state.get(name, {}))
