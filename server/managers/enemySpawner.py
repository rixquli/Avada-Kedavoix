import random
from typing import Any, Dict, List, Tuple

from client.classes.enemy import EnemyList

DungeonEnemyList: List[List[Tuple[int, EnemyList, Dict[str, Any]]]] = [
    # Etage 1
    [(5, EnemyList.GOBELIN_MASSUE, {}), (5, EnemyList.DRAGON, {})],
    # Etage 2
    [(10, EnemyList.GOBELIN_MASSUE, {})],
    # Etage 3
    [(10, EnemyList.DRAGON, {})],
    # Etage restant
    [(10, EnemyList.DRAGON, {}), (1, EnemyList.BOSS, {})]

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
            count, enemy_type, kwargs = levelEnemies
            for _ in range(count):
                rand = (
                    random.randint(area[0][0], area[1][0]),
                    random.randint(area[0][1], area[1][1]),
                )
                enemy = Enemy.get_enemy_type(
                    enemy_type, x=rand[0], y=rand[1], world_layer=world_layer, is_server=True, **kwargs
                )
                self.network.game_state.enemies.addEntity(enemy)
