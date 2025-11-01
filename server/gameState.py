import os
import sys


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

    def get_game_state(self):
        """Retourne l'état complet du jeu pour le broadcast"""
        return {
            "players": self.players.to_dict(),
            "spells": self.spells.to_dict(),
            "enemies": self.enemies.to_dict(),
        }

    def update_all(self):
        for spell in list(self.spells.entities.values()):
            spell.update()
        for enemy in list(self.enemies.entities.values()):
            enemy.update()

    # Applique les mises à jour venant du serveur
    def apply_state(self, state):
        # Players
        for id, data in state.get("players", {}).items():
            if not data:
                # si le joueur n'existe plus on le supprime
                self.players.remove(id)
            elif str(id) not in self.players.entities:
                # si le joueur n'existe pas localement on l'ajoute
                player = Player.from_dict(data)
                self.players.addEntity(player, fixed_id=str(id))
            else:
                # si le joueur existe localement on le met a jour
                self.players.update(str(id), data)
        if state.get("players", {}):
            self.players.remove_local_only_entity(state.get("players", {}))

        # Spells
        for id, data in state.get("spells", {}).items():
            if not data:
                # si le spell n'existe plus on le supprime
                self.spells.remove(str(id))
            elif str(id) not in self.spells.entities:
                # si le spell n'existe pas localement on l'ajoute
                spell = Spell.from_dict(data)
                self.spells.addEntity(spell, fixed_id=str(id))
            else:
                # si le spell existe localement on le met a jour
                self.spells.update(str(id), data)
        if state.get("spells", {}):
            self.spells.remove_local_only_entity(state.get("spells", {}))

        # Enemies
        for id, data in state.get("enemies", {}).items():
            if not data:
                # si l'ennemi n'existe plus on le supprime
                self.enemies.remove(str(id))
            elif str(id) not in self.enemies.entities:
                # si l'ennemi n'existe pas localement on l'ajoute
                enemy = Enemy.from_dict(data)
                self.enemies.addEntity(enemy, fixed_id=str(id))
            else:
                # si l'ennemi existe localement on le met a jour
                self.enemies.update(str(id), data)
        if state.get("enemies", {}):
            self.enemies.remove_local_only_entity(state.get("enemies", {}))
