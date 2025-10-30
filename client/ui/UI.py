class Menu:
    def __init__(self, name, is_showing):
        self.name = name
        self.is_showing = is_showing
        self.ui_components = []

    def add(self, ui_components):
        self.ui_components += ui_components

    def update(self, screen):
        for comp in self.ui_components:
            if hasattr(comp, "draw"):
                comp.draw(screen)

    def handle_event(self, event):
        for comp in self.ui_components:
            if hasattr(comp, "handle_event"):
                comp.handle_event(event)


class UI:
    def __init__(self, screen):
        self.menus = {}
        self.screen = screen

    def createMenu(self, name, is_showing=True):
        if name in self.menus:
            raise ValueError(name, ": this menu already exist")
        self.menus[name] = Menu(name, is_showing)
        return name

    def show(self, menu_name):
        if menu_name not in self.menus.keys():
            raise ValueError(menu_name, ": this menu do not exist")
        self.menus[menu_name].is_showing = True

    def hide(self, menu_name):
        if menu_name not in self.menus.keys():
            raise ValueError(menu_name, ": this menu do not exist")
        self.menus[menu_name].is_showing = False

    def toggle(self, menu_name):
        if menu_name not in self.menus.keys():
            raise ValueError(menu_name, ": this menu do not exist")
        self.menus[menu_name].is_showing = not self.menus[menu_name].is_showing

    def addTo(self, menu_name, ui_components):
        if menu_name not in self.menus.keys():
            raise ValueError(menu_name, ": this menu do not exist")
        self.menus[menu_name].add(ui_components)

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
        for menu_name in self.get_visible_menus():
            self.menus[menu_name].handle_event(event)
