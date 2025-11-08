"""
GameState ou WorldState correspond aux données du monde gerées par le serveur et envoyées aux clients.
Il y as plusieurs GameState durant une partie qui sont utilisées:
    - Une appartient au serveur
    - Chaque joueur possede une copie du monde qui est mise a jour par le serveur

GameState contient tous les jour tout les pnjs,...
Elle permet au serveur de mettre a jour toutes les entités puis d'envoyer les nouvelles données aux clients:

Ex:
    Le serveur a dans son gameState un ennemi que le joueur n'a pas encore dans son gameState local
    le serveur va envoyé son gameState avec ce nouvel ennemi
    le client/joueur va remarquer que dans sa copie du monde cet ennemi n'existe pas il va donc le rejouter dans son monde local
    si le joueur avait deja enregistrer cet ennemi il va le mettre a jour et faire en sorte que sa copie local soit la meme que celle du serveur

Pour résumer GameState = Une copie du monde partagée entre clients et serveur
"""

import os
import sys


# To import module from other folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from client.classes.wall import Wall
from server.managers.collisionManager import CollisionManager
from client.classes.pnj import PNJ
from client.classes.enemy import Enemy
from client.classes.player import Player
from client.classes.spell import Spell
from server.managers.entityManager import EntityManager


class GameState:
    def __init__(self):
        self.collision_manager = CollisionManager(self)

        self.players = EntityManager(Player)
        self.spells = EntityManager(Spell)
        self.enemies = EntityManager(Enemy)
        self.pnjs = EntityManager(PNJ)
        self.walls = EntityManager(Wall)

        self.all_entities_manager = [
            self.players,
            self.spells,
            self.enemies,
            self.pnjs,
            self.walls,
        ]

    def get_game_state(self):
        """Retourne l'état complet du jeu pour le broadcast"""
        return {
            "players": self.players.to_dict(),
            "spells": self.spells.to_dict(),
            "enemies": self.enemies.to_dict(),
            "pnjs": self.pnjs.to_dict(),
            "walls": self.walls.to_dict(),
        }

    # Executer cote serveur
    def get_entities_list(self):
        res = []
        for entities_manager in self.all_entities_manager:
            res.append((entities_manager.entity_type, entities_manager.get_list()))
        return res

    def update_all(self):
        for spell in list(self.spells.entities.values()):
            if spell.is_expired():
                self.spells.remove(spell.id)
            else:
                spell.server_update()
        for enemy in list(self.enemies.entities.values()):
            enemy.server_update()
        for pnj in list(self.pnjs.entities.values()):
            pnj.server_update()

        self.collision_manager.handle_collision(entity_list=self.get_entities_list())

    # Executer coté client
    def apply_state(self, state, my_player_id=None):
        """Applique les mises à jour venant du serveur"""
        self.apply_state_for(state, "players", self.players, my_player_id=my_player_id)
        self.apply_state_for(state, "enemies", self.enemies)
        self.apply_state_for(state, "spells", self.spells)
        self.apply_state_for(state, "pnjs", self.pnjs)
        self.apply_state_for(state, "walls", self.walls)

        self.collision_manager.update_collision_group("obstacle", [self.walls])

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
                    filtered_data = {
                        k: v
                        for k, v in data.items()
                        if k
                           not in [
                               "display_x",
                               "display_y",
                           ]
                    }
                    entities.update(str(id), filtered_data)
        # Verifie si tout les elements ont bien ete supprimer cote client
        entities.remove_local_only_entity(state.get(name, {}))
