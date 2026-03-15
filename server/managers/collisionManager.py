from typing import TYPE_CHECKING, Callable

import pygame

from server.classes.serializable import Serializable

if TYPE_CHECKING:
    from server.gameState import GameState


class CollisionManager:
    def __init__(self, game_state: "GameState"):
        self.game_state = game_state

        self.handled_collisions: list[
            tuple[
                type[Serializable],
                type[Serializable],
                Callable[[Serializable, Serializable], None],
            ]
        ] = []

        from server.collisions import CollisionsList

        for collision in CollisionsList:
            self.add_collision(
                collision["entity1"], collision["entity2"], collision["handler"]
            )

        """Contient la liste des objets que le joueurs peut toucher/ne pas traverser"""
        self.client_collider_groups = {"obstacle": pygame.sprite.Group()}

    def update_collision_group(self, group_name, entities_list):
        group = self.client_collider_groups.get(group_name)
        if group is None:
            return
        group.empty()
        for entity in entities_list:
            entity_list = entity.get_list()
            if entity_list:
                for e in entity_list:
                    group.add(e)

    def add_collision(self, entity1_type, entity2_type, handler):
        self.handled_collisions.append((entity1_type, entity2_type, handler))

    @staticmethod
    def do_collide(entity1, entity2) -> bool:
        if (
            not entity1.world_layer
            or not entity2.world_layer
            or entity1.world_layer != entity2.world_layer
        ):
            return False
        return entity1.hitbox.collide(entity2)

    def get_handler_collision_between(self, entity_type1, entity_type2):
        for collision in self.handled_collisions:
            if collision[0] == entity_type1 and collision[1] == entity_type2:
                return collision[2]
        return None

    def handle_collision(
        self, entity_list: list[tuple[type[Serializable], list[Serializable]]]
    ):
        for entity_type1, entities1 in entity_list:
            for entity_type2, entities2 in entity_list:
                handler = self.get_handler_collision_between(entity_type1, entity_type2)
                if handler is not None:
                    for entity1 in entities1:
                        for entity2 in entities2:
                            if (
                                not entity1.world_layer
                                or not entity2.world_layer
                                or entity1.world_layer != entity2.world_layer
                            ):
                                continue

                            if self.do_collide(entity1, entity2):
                                handler(self, entity1, entity2)
