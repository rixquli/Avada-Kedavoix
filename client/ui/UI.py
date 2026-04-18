"""
UI est la classe permettant de gerer toute les interface/menu du jeu accessible depuis le game_manager
Ex:
    game_manager.ui.show("MainMenu")

Menu est la classe correspondant a un menu/interface elle est utilisé dans UI et gere/affiche tout les element du menu
Ex:
    menu_name = game_manager.ui.createMenu("Nom")                     # Creer le menu
    game_manager.ui.addTo(menu_name, Text("AVADA KEDAVOIX",(0, 50)))  # Ajoute des elements dans le menu

!ATTENTION:
    Pour simplifier le processus tous les menus/interfaces doivent etre dans client/menus.py
    voir exemple por en rajouter, cela permet un acces plus rapide
!ATTENTION
"""

import pygame


class Menu:
    def __init__(self, name, is_showing):
        self.name = name
        self.is_showing = is_showing
        self.ui_components = []

    def add(self, ui_components):
        if isinstance(ui_components, list):
            for ui_element in ui_components:
                self.ui_components.append(ui_element)
        else:
            self.ui_components.append(ui_components)

    def update(self, screen):
        for comp in self.ui_components:
            if hasattr(comp, "update"):
                comp.update()
            if hasattr(comp, "draw"):
                comp.draw(screen)

    def handle_event(self, event):
        for comp in self.ui_components:
            if hasattr(comp, "handle_event"):
                comp.handle_event(event)

    def on_resize(self):
        for comp in self.ui_components:
            if hasattr(comp, "on_resize"):
                comp.on_resize()


class UI:
    def __init__(self, screen=None):
        self.menus = {}
        self.screen = screen
        from client.menus import Menus

        self.imported_menus = Menus
        self.import_menus(self.imported_menus)

    def createMenu(self, name, is_showing=True):
        if name in self.menus:
            raise ValueError(name, ": this menu already exist")
        self.menus[name] = Menu(name, is_showing)
        return name

    def show(self, menu_name):
        """
        Affiche le menu passé en argument si present dans dans la liste des menus enregistrés
        """
        if menu_name not in self.menus.keys():
            raise ValueError(menu_name, ": this menu do not exist")
        self.menus[menu_name].is_showing = True

    def hide(self, menu_name):
        """
        Désaffiche le menu passé en argument si present dans dans la liste des menus enregistrés
        """
        if menu_name not in self.menus.keys():
            raise ValueError(menu_name, ": this menu do not exist")
        self.menus[menu_name].is_showing = False

    def toggle(self, menu_name):
        """
        Affiche/Désaffiche le menu passé en argument si present dans dans la liste des menus enregistrés
        """
        if menu_name not in self.menus.keys():
            raise ValueError(menu_name, ": this menu do not exist")
        self.menus[menu_name].is_showing = not self.menus[menu_name].is_showing

    def addTo(self, menu_name, ui_components):
        if menu_name not in self.menus.keys():
            raise ValueError(menu_name, ": this menu do not exist")
        self.menus[menu_name].add(ui_components)

    def _resolve_menu_components(self, menu_def, menu_name):
        """Construit la liste des composants en supportant du contenu statique ou callable."""
        content = menu_def.get("content", [])

        if callable(content):
            try:
                components = content(menu_name)
            except TypeError:
                components = content()
        else:
            components = content

        if components is None:
            return []
        return components

    def on_resize(self):
        """Quand la taille de la fenetre change on recalcule les positions ancrées."""
        for menu_name in self.get_visible_menus():
            self.menus[menu_name].on_resize()

    def refresh(self, menu_name):
        """
        Ecrase le menu donné avec le meme
        Permet de le rafraichir si des valeurs ont changées
        """
        for menu_def in self.imported_menus:
            if menu_def["name"] != menu_name:
                continue

            # conserver l'état d'affichage actuel si présent
            existing = self.menus.get(menu_name)
            is_showing = (
                existing.is_showing if existing else menu_def.get("is_showing", False)
            )

            # créer nouvel objet Menu
            new_menu = Menu(menu_name, is_showing)

            # résoudre le contenu (accepte callable(menu_name) ou callable())
            components = self._resolve_menu_components(menu_def, menu_name)

            # ajouter les composants (ignorer None)
            for comp in components:
                if comp is None:
                    continue
                new_menu.add(comp)

            self.menus[menu_name] = new_menu
            return

    def get_visible_menus(self):
        res = []
        for name, menu in self.menus.items():
            if menu.is_showing:
                res += [name]
        return res

    def update(self):
        for name, menu in self.menus.items():
            if menu.is_showing:
                menu.update(self.screen)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.toggle("settings")
        for menu_name in self.get_visible_menus():
            self.menus[menu_name].handle_event(event)

    def set_dialog_data(self, dialog_name, text_list):
        """
        Met à jour les données du DialogBox (nom du NPC et texte du dialogue)
        """
        if dialog_name not in self.menus:
            raise ValueError(dialog_name, ": this dialog menu does not exist")

        # Parcourir les composants du menu pour trouver le DialogBox
        for component in self.menus[dialog_name].ui_components:
            # Vérifier si c'est un DialogBox en regardant ses attributs
            if hasattr(component, "nameComp") and hasattr(component, "textComp"):
                # Mettre à jour le texte et réinitialiser l'index
                component.text = text_list
                component.textIndex = 0
                component.nameComp.change_text(text_list[0].get("name", ""))
                component.textComp.change_text(text_list[0].get("text", ""))
                break

    def import_menus(self, menus):
        for menu in menus:
            name = menu["name"]
            is_showing = menu.get("is_showing", False)
            self.createMenu(name, is_showing)
            components = self._resolve_menu_components(menu, name)
            for component in components:
                self.addTo(name, component)

    def loading(self):
        loading_menu = self.menus.get("loading", None)
        if loading_menu:
            loading_menu.update(self.screen)
