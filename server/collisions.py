"""
C'est le serveur qui s'occupe de gerer les evenements des collisions par exemple appliquer les degats
CollisionsList contient la liste des evenements quand entity1 touche entity2 cela declenche le handler
"""

from typing import TYPE_CHECKING, Dict, List
from client.classes.enemy import Enemy
from client.classes.spell import Spell


if TYPE_CHECKING:
    from server.managers.collisionManager import CollisionManager


def spell_enemy(collision_manager: "CollisionManager", spell: Spell, enemy: Enemy):
    # TODO: enemy.take_damage(spell.attack_damage)
    collision_manager.game_state.spells.remove(spell.id)
    enemy.take_dmg(spell.dmg)


CollisionsList = [{"entity1": Spell, "entity2": Enemy, "handler": spell_enemy}]
