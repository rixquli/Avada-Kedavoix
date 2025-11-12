from typing import TYPE_CHECKING, Callable, List, Tuple, Type

from server.classes.serializable import Serializable


if TYPE_CHECKING:
    from server.gameState import GameState


class CollisionManager:
    def __init__(self, game_state: "GameState"):
        self.game_state = game_state

        self.handled_collisions: List[
            Tuple[
                Type[Serializable],
                Type[Serializable],
                Callable[[Serializable, Serializable], None],
            ]
        ] = []

        from server.collisions import CollisionsList

        for collision in CollisionsList:
            self.add_collision(
                collision["entity1"], collision["entity2"], collision["handler"]
            )

    def add_collision(self, entity1_type, entity2_type, handler):
        self.handled_collisions.append((entity1_type, entity2_type, handler))

    def do_collide(self, entity1, entity2) -> bool:
        """
        AABB vs. AABB collision
        https://developer.mozilla.org/en-US/docs/Games/Techniques/3D_collision_detection#aabb_vs._aabb
        """
        """
        x1, y1 = entity1.x, entity1.y
        w1, h1 = entity1.hitbox_size
        x2, y2 = entity2.x, entity2.y
        w2, h2 = entity2.hitbox_size  # (x_size, y_size)

        x_min_1 = x1 - (w1 / 2)
        x_max_1 = x1 + (w1 / 2)
        y_min_1 = y1 - (h1 / 2)
        y_max_1 = y1 + (h1 / 2)

        x_min_2 = x2 - (w2 / 2)
        x_max_2 = x2 + (w2 / 2)
        y_min_2 = y2 - (h2 / 2)
        y_max_2 = y2 + (h2 / 2)

        return (x_min_1 <= x_max_2 and x_max_1 >= x_min_2) and (
            y_min_1 <= y_max_2 and y_max_1 >= y_min_2
        )
        """
        return entity1.hitbox.collide(entity2)

    def get_handler_collision_between(self, entity_type1, entity_type2):
        for collision in self.handled_collisions:
            if collision[0] == entity_type1 and collision[1] == entity_type2:
                return collision[2]
        return None

    def handle_collision(
        self, entity_list: List[Tuple[Type[Serializable], Serializable]]
    ):
        for entity_type1, entities1 in entity_list:
            for entity_type2, entities2 in entity_list:
                handler = self.get_handler_collision_between(entity_type1, entity_type2)
                if handler is not None:
                    for entity1 in entities1:
                        for entity2 in entities2:
                            if self.do_collide(entity1, entity2):
                                handler(self, entity1, entity2)
