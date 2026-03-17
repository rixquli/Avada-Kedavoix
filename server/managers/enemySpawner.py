import random
from typing import Any, Dict, List, Tuple

DungeonEnemyList: List[List[Tuple[int, Dict[str, Any]]]] = [
    # Etage 1
    [(5, {"color": (0, 0, 0)}), (5, {"color": (255, 0, 0)})],
    # Etage 2
    [(10, {"color": (255, 0, 0)})],
    # Etage restant
    [(10, {"color": (255, 255, 255)})],
]


class EnemySpawner:
    def __init__(self, network):
        self.network = network

    def dungeon_generate(
        self,
        world_layer,
        level: int,
        area=(
            (-1000, -1000),
            (1000, 1000),
        ),  # le coin en haut a gauche et en bas a droite
    ):
        from client.classes.enemy import Enemy

        level = min(len(DungeonEnemyList) - 1, level)
        for levelEnemies in DungeonEnemyList[level]:
            count, kwargs = levelEnemies
            for _ in range(count):
                rand = (
                    random.randint(area[0][0], area[1][0]),
                    random.randint(area[0][1], area[1][1]),
                )
                enemy = Enemy(rand[0], rand[1], world_layer=world_layer, **kwargs)
                self.network.game_state.enemies.addEntity(enemy)
