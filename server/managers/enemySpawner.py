import random
from typing import Any, Dict, List, Tuple

from client.classes.enemy import EnemyList

DungeonEnemyList: List[List[Tuple[int, EnemyList, Dict[str, Any]]]] = [
    # Etage 1
    [(5, EnemyList.GOBELIN_MASSUE, {}), (5, EnemyList.GOBELIN_POIGNARD, {})],
    # Etage 2
    [
        (10, EnemyList.GOBELIN_MASSUE, {}),
        (7, EnemyList.GOBELIN_POIGNARD, {}),
        (1, EnemyList.BOSS, {}),
    ],
    # Etage 3
    [
        (12, EnemyList.GOBELIN_MASSUE, {}),
        (7, EnemyList.GOBELIN_POIGNARD, {}),
        (5, EnemyList.SKELETON, {}),
    ],
    # Etage 4
    [
        (14, EnemyList.GOBELIN_MASSUE, {}),
        (10, EnemyList.GOBELIN_POIGNARD, {}),
        (7, EnemyList.SKELETON, {}),
    ],
    # Etage 5
    [
        (14, EnemyList.GOBELIN_MASSUE, {}),
        (5, EnemyList.DARK_MAGE, {}),
        (11, EnemyList.SKELETON, {}),
    ],
    # Etage 6
    [
        (5, EnemyList.GOBELIN_MASSUE, {}),
        (5, EnemyList.GOBELIN_POIGNARD, {}),
        (10, EnemyList.SKELETON, {}),
        (7, EnemyList.DARK_MAGE, {}),
    ],
    # Etage 7
    [
        (5, EnemyList.GOBELIN_MASSUE, {}),
        (5, EnemyList.GOBELIN_POIGNARD, {}),
        (10, EnemyList.SKELETON, {}),
        (10, EnemyList.DARK_MAGE, {}),
    ],
    # Etage 8
    [
        (5, EnemyList.SKELETON, {}),
        (7, EnemyList.DARK_MAGE, {}),
        (3, EnemyList.DRAGON, {}),
    ],
    # Etage 9
    [
        (7, EnemyList.SKELETON, {}),
        (9, EnemyList.DARK_MAGE, {}),
        (6, EnemyList.DRAGON, {}),
    ],
    # Etage Boss
    [(8, EnemyList.DRAGON, {})],
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
                position_valid = False
                max_attempts = 10
                attempts = 0

                while not position_valid and attempts < max_attempts:
                    rand = (
                        random.randint(area[0][0], area[1][0]),
                        random.randint(area[0][1], area[1][1]),
                    )

                    # Créer temporairement l'ennemi pour tester
                    test_enemy = Enemy.get_enemy_type(
                        enemy_type,
                        x=rand[0],
                        y=rand[1],
                        world_layer=world_layer,
                        is_server=True,
                        **kwargs
                    )

                    # Vérifier si la position collide avec un mur
                    if not test_enemy.hitbox.get_server_collided():
                        position_valid = True
                        self.network.game_state.enemies.addEntity(test_enemy)

                    attempts += 1

    def spawn_night_surface(
        self, world_layer=1, count=3, area=((-400, -400), (400, 400))
    ):
        from client.classes.enemy import Enemy
        from client.classes.enemy import EnemyList

        for _ in range(count):
            position_valid = False
            max_attempts = 10
            attempts = 0

            while not position_valid and attempts < max_attempts:
                rand = (
                    random.randint(area[0][0], area[1][0]),
                    random.randint(area[0][1], area[1][1]),
                )

                # Créer temporairement l'ennemi pour tester
                test_enemy = Enemy.get_enemy_type(
                    EnemyList.GOBELIN_MASSUE,
                    x=rand[0],
                    y=rand[1],
                    world_layer=world_layer,
                    is_server=True,
                )

                # Vérifier si la position collide avec un mur
                if not test_enemy.hitbox.get_server_collided():
                    position_valid = True
                    self.network.game_state.enemies.addEntity(test_enemy)

                attempts += 1
