import sys

import pygame

from client.Utils.ImageTool import ImageTool
from client.classes.spell import Spell, SpellList
from client.layerList import Layer

throwableSpells = [SpellList.FIREBALL, SpellList.ICE]

spells_img = {
    SpellList.FIREBALL: "client/ressources/Sorts/FIREBALL/idle_1.png",
    SpellList.ICE: "client/ressources/Sorts/ICE/idle_1.png",
    SpellList.DARK_FIREBALL: "client/ressources/Sorts/DARK_FIREBALL/idle_0.png",
}


class SpellsManager:
    def __init__(self, gameManager):
        self.gameManager = gameManager
        self.unlockSpell = {
            spell: {"unlock": False, "img": None} for spell in SpellList
        }
        self.unlockSpell[SpellList.FIREBALL]["unlock"] = True
        self.active_spell = SpellList.FIREBALL
        for key, val in spells_img.items():
            self.unlockSpell[key]["img"] = ImageTool.load(val, (48, 48))

        self.hotbar_items = self.get_items()

    def unlock(self, spell):
        for k in self.unlockSpell.keys():
            if spell == k or spell == k.value:
                self.unlockSpell[k]["unlock"] = True
        self.hotbar_items = self.get_items()

    def unlock_all(self):
        for k in self.unlockSpell.keys():
            self.unlockSpell[k]["unlock"] = True
        self.hotbar_items = self.get_items()

    def get_items(self):
        """Used to get items for the hotbar"""
        l = []
        for key, entry in self.unlockSpell.items():
            if entry["img"] and entry["unlock"]:
                dico = {"type": key, "img": entry["img"]}
                l.append(dico)
        return l

    def set_active_spell(self, hot_bar_list_index):
        if hot_bar_list_index < len(self.hotbar_items):
            self.active_spell = self.hotbar_items[hot_bar_list_index]["type"]
        else:
            self.active_spell = None

    def cast_spell(self, vocal_action):
        my_player = self.gameManager.client_manager.get_player()
        can_throw = (
            self.unlockSpell.get(vocal_action, {"unlock": False}).get("unlock", False)
            and self.active_spell
            and self.active_spell == vocal_action
        )
        if not my_player or not can_throw:
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
                    self.gameManager.quit()
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
