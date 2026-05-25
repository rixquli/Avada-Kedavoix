"""
GameState ou WorldState correspond aux données du monde gerées par le serveur et envoyées aux clients.
Il y as plusieurs GameState durant une partie qui sont utilisées:
    - Une appartient au serveur
    - Chaque joueur possede une copie du monde qui est mise a jour par le serveur

GameState contient tous les joueur tout les pnjs,...
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
import time

# To import module from other folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from client.classes.wall import Wall
from server.managers.collisionManager import CollisionManager
from client.classes.pnj import PNJ
from client.classes.enemy import Enemy
from client.classes.player import Player
from client.classes.spell import Spell
from client.classes.house import House
from server.managers.entityManager import EntityManager
from server.classes.serializable import Serializable


class GameState:
    """permet d'avoir une copie partagee entre client et serveur"""

    day_min = 5
    night_min = 5

    def __init__(self):
        self.collision_manager = CollisionManager(self)

        self.players = EntityManager(Player)
        self.spells = EntityManager(Spell)
        self.enemies = EntityManager(Enemy)
        self.pnjs = EntityManager(PNJ)
        self.walls = EntityManager(Wall)
        self.houses = EntityManager(House)

        # self.base_ingame_time = None
        self.ingame_time = 0

        self.all_entities_manager = [
            self.players,
            self.spells,
            self.enemies,
            self.pnjs,
            self.walls,
            self.houses,
        ]

    def get_game_state(self, diff=True, layer=None):
        """Retourne l'état complet du jeu pour le broadcast"""
        players_state = self.players.to_dict(diff, layer)
        spells_state = self.spells.to_dict(diff, layer)
        enemies_state = self.enemies.to_dict(diff, layer)
        pnjs_state = self.pnjs.to_dict(diff, layer)
        walls_state = self.walls.to_dict(diff, layer)
        houses_state = self.houses.to_dict(diff, layer)

        return {
            "players": players_state,
            "spells": spells_state,
            "enemies": enemies_state,
            "pnjs": pnjs_state,
            "walls": walls_state,
            "houses": houses_state,
            "ingame_time": self.ingame_time,
        }

    # Executer cote serveur
    def get_entities_list(self) -> list[tuple[type[Serializable], list[Serializable]]]:
        res = []
        for entities_manager in self.all_entities_manager:
            res.append((entities_manager.entity_type, entities_manager.get_list()))
        return res

    def get_entities_list_layer(
        self, layer
    ) -> list[tuple[type[Serializable], list[Serializable]]]:
        res = []
        for entities_manager in self.all_entities_manager:
            res.append(
                (entities_manager.entity_type, entities_manager.get_list_layer(layer))
            )
        return res

    def update_all(self):
        """Update all entities here"""

        # Players
        for player in list(self.players.entities.values()):
            player.server_update()

        # Spells
        for spell in list(self.spells.entities.values()):
            if spell.is_expired():
                self.spells.remove(spell.id)
            else:
                spell.server_update()

        # Enemies
        for enemy in list(self.enemies.entities.values()):
            if enemy.is_dead():
                self.enemies.remove(enemy.id)
            else:
                enemy.server_update()

        # PNJ
        for pnj in list(self.pnjs.entities.values()):
            if pnj.is_dead():
                self.pnjs.remove(pnj.id)
            else:
                pnj.server_update()

        # update time
        self.ingame_time += 1 / 30

        # Collision handler (events)
        self.collision_manager.handle_collision(entity_list=self.get_entities_list())

    def update_all_layer(self, layer):
        """Update all entities here"""

        # Players
        for player in list(self.players.entities.values()):
            if layer == player.world_layer:
                player.server_update()

        # Spells
        for spell in list(self.spells.entities.values()):
            if spell.is_expired():
                self.spells.remove(spell.id)
            elif layer == spell.world_layer:
                spell.server_update()

        # Enemies
        for enemy in list(self.enemies.entities.values()):
            if enemy.is_dead():
                self.enemies.remove(enemy.id)
            elif layer == enemy.world_layer:
                enemy.server_update()

        # PNJ
        for pnj in list(self.pnjs.entities.values()):
            if pnj.is_dead():
                self.pnjs.remove(pnj.id)
            elif layer == pnj.world_layer:
                pnj.server_update()

        # update time
        self.ingame_time += 1 / 30

        # Collision handler (events)
        self.collision_manager.handle_collision(
            entity_list=self.get_entities_list_layer(layer)
        )

    # Executer coté client
    def apply_state(self, state, my_player_id=None, layer=None, server=False):
        """Applique les mises à jour venant du serveur"""
        self.apply_state_for(
            state,
            "players",
            self.players,
            my_player_id=my_player_id,
            layer=layer,
            server=server,
        )
        self.apply_state_for(state, "enemies", self.enemies, layer=layer, server=server)
        self.apply_state_for(state, "spells", self.spells, layer=layer, server=server)
        self.apply_state_for(state, "pnjs", self.pnjs, layer=layer, server=server)
        self.apply_state_for(state, "walls", self.walls, layer=layer, server=server)
        self.apply_state_for(state, "houses", self.houses, layer=layer, server=server)
        ingame_time = state.get("ingame_time", None)
        if ingame_time:
            self.ingame_time = ingame_time

        if not server:
            self.collision_manager.update_collision_group("obstacle", [self.walls, self.houses])

    def apply_state_for(
        self, state, name, entities, my_player_id=None, layer=None, server=False
    ):
        for id, data in state.get(name, {}).items():
            if server:
                if str(id) not in entities.entities:
                    entity = entities.entity_type.from_dict(data)
                    entities.addEntity(entity, fixed_id=str(id))
                else:
                    entities.update(str(id), data)
            elif str(id) not in entities.entities:
                # si l'entité n'existe pas localement on l'ajoute
                try:
                    entity = entities.entity_type.from_dict(data)
                    entities.addEntity(entity, fixed_id=str(id))
                except TypeError:
                    # Un diff partiel peut arriver avant le snapshot initial.
                    # On attend un payload complet pour instancier l'entité.
                    continue
            else:
                # si l'entité existe localement on le met a jour
                if my_player_id and str(id) == str(my_player_id):
                    # Pour le joueur local, on garde x, y, vx, vy calculés localement
                    # On met à jour seulement les autres propriétés
                    # player = entities.get(my_player_id)
                    # if player:
                    # distance = (
                    #     (data.get("x", 0) - player.x) ** 2
                    #     + (data.get("y", 0) - player.y) ** 2
                    # ) ** 0.5
                    # if (
                    #     distance > 14
                    # ):  #! Si la difference avec les coordonnées actuel est trop grande alors on ecrase la position
                    #     print("DISTANCE > 14", distance)
                    #     filtered_data = {
                    #         k: v
                    #         for k, v in data.items()
                    #         if k
                    #         not in [
                    #             # "x",
                    #             # "y",
                    #             "vx",
                    #             "vy",
                    #             "display_x",
                    #             "display_y",
                    #             "target_x",
                    #             "target_y",
                    #         ]
                    #     }
                    #     if filtered_data:
                    #         entities.update(str(id), filtered_data)
                    # else:
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
                    # on met tout a jour sauf les display (evites des problemes de syncronisation de position d'image)
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
        if not server:
            entities.remove_local_only_entity(state.get(name, {}))
