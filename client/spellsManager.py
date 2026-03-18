import sys

import pygame

from client.classes.spell import Spell, SpellList
from client.layerList import Layer


throwableSpells = [SpellList.FIREBALL, SpellList.ICE]


class SpellsManager:
    def __init__(self, gameManager):
        self.gameManager = gameManager
        self.unlockSpell = {spell: {"unlock": False} for spell in SpellList}
        self.unlockSpell[SpellList.FIREBALL]["unlock"] = True

    def cast_spell(self, vocal_action):
        my_player = self.gameManager.client_manager.get_player()
        if not my_player:
            return

        if vocal_action in throwableSpells:
            # Calculer la direction normalisée vers le curseur de la souris
            mouse_x, mouse_y = pygame.mouse.get_pos()
            dx = mouse_x - (self.gameManager.screen.get_width() / 2)
            dy = mouse_y - (self.gameManager.screen.get_height() / 2)
            length = (dx**2 + dy**2) ** 0.5

            if length > 0:
                dir_x = dx / length
                dir_y = dy / length
            else:
                dir_x, dir_y = 1, 0

            # Créer le sort localement (pour eviter les latences)
            spell = Spell.get_spell_type(
                vocal_action,
                x=my_player.x,
                y=my_player.y,
                player_id=self.gameManager.client_manager.my_player_id,
                dir=(dir_x, dir_y),
                thrower=my_player.THROWER_TYPE,
                world_layer=my_player.world_layer,
            )

            self.gameManager.client_manager.cast_spell(spell)
        else:
            # Sors spéciaux
            match vocal_action:
                case SpellList.HEAL:
                    self.gameManager.client_manager.heal()
                case SpellList.TELEPORTATION:
                    my_player.teleport(0, 0, Layer.OVERWORLD.value)
                case SpellList.CLOSE:
                    pygame.quit()
                    sys.exit()
                case _:
                    raise NotImplementedError(
                        "Need to implement or remove: " + vocal_action
                    )

    def cast_spell_type(self, type: SpellList, **kwargs):
        spell = Spell.get_spell_type(
            type,
            **kwargs,
        )

        self.gameManager.client_manager.cast_spell(spell)


    def cast_basic_spell(self):
        # Quand on clique ca lance un sort dans la direction de la souris
        my_player = self.gameManager.client_manager.get_player()
        if not my_player:
            return

        # Calculer la direction normalisée vers le curseur de la souris
        mouse_x, mouse_y = pygame.mouse.get_pos()
        dx = mouse_x - (self.gameManager.screen.get_width() / 2)
        dy = mouse_y - (self.gameManager.screen.get_height() / 2)
        length = (dx**2 + dy**2) ** 0.5

        if length > 0:
            dir_x = dx / length
            dir_y = dy / length
        else:
            dir_x, dir_y = 1, 0

        # Créer le sort localement (pour eviter les latences)
        spell = Spell(
            x=my_player.x,
            y=my_player.y,
            player_id=self.gameManager.client_manager.my_player_id,
            color=(50, 150, 255),
            dir=(dir_x, dir_y),
            radius=8,
            thrower=my_player.THROWER_TYPE,
            world_layer=my_player.world_layer,
        )

        self.gameManager.client_manager.cast_spell(spell)
