"""
C'est le serveur qui s'occupe de gerer les evenements des collisions par exemple appliquer les degats
CollisionsList contient la liste des evenements quand entity1 touche entity2 cela declenche le handler
"""

from typing import TYPE_CHECKING
from client.classes.enemy import Enemy
from client.classes.spell import Spell
from client.classes.player import Player
from client.classes.wall import Wall


if TYPE_CHECKING:
    from server.managers.collisionManager import CollisionManager


def spell_other(collision_manager: "CollisionManager", spell: Spell, other):
    """effectues la collision entre un spell et un autre type"""
    if hasattr(other, "THROWER_TYPE"):
        # tout ceux qui peuvent prendre des degats doivent avoir un thrower type et un take_dmg()
        if spell.thrower != other.THROWER_TYPE:
            collision_manager.game_state.spells.remove(spell.id)
            other.take_dmg(spell.dmg)
            print(other.hp)
    else:
        collision_manager.game_state.spells.remove(spell.id)


CollisionsList = [
    {"entity1": Spell, "entity2": Enemy, "handler": spell_other},
    {"entity1": Spell, "entity2": Player, "handler": spell_other},
    {"entity1": Spell, "entity2": Wall, "handler": spell_other},
]
