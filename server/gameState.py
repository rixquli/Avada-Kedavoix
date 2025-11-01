import os
import sys

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
            spell.update()
        for enemy in list(self.enemies.entities.values()):
            enemy.update()
        for pnj in list(self.pnjs.entities.values()):
            pnj.update()

    # Applique les mises à jour venant du serveur
    def apply_state(self, state):
        self.apply_state_for(state, "players", self.players)
        self.apply_state_for(state, "enemies", self.enemies)
        self.apply_state_for(state, "spells", self.spells)
        self.apply_state_for(state, "pnjs", self.pnjs)

    def apply_state_for(self, state, name, entities):
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
                entities.update(str(id), data)
        if state.get(name, {}):
            entities.remove_local_only_entity(state.get(name, {}))
