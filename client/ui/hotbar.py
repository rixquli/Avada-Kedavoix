import pygame


class Hotbar:
    def __init__(self, screen_width, screen_height):
        self.slot_count = 9
        self.slot_size = 64
        self.spacing = 6

        total_width = (
            self.slot_count * self.slot_size + (self.slot_count - 1) * self.spacing
        )
        from client.gameManager import GameManager

        self.game_manager = GameManager()
        self.start_x = (screen_width - total_width) // 2
        self.y = screen_height - self.slot_size - 20

        self.selected_index = 0

        self.slots = []
        self.items = [None] * self.slot_count

        self.create_slots()

    def create_slots(self):
        self.slots.clear()

        for i in range(self.slot_count):
            x = self.start_x + i * (self.slot_size + self.spacing)
            rect = pygame.Rect(x, self.y, self.slot_size, self.slot_size)
            self.slots.append(rect)

    def set_item(self, index, image_path):
        if image_path and 0 <= index < self.slot_count:
            img = pygame.image.load(image_path).convert_alpha()
            img = pygame.transform.scale(img, (48, 48))
            self.items[index] = img

    def on_resize(self):
        #! TODO le plus simple est juste de faire comme le reste des composant et d'utiliser la fonction pour recalcluer dynamiquement la position en fonction de la taille de l'ecran
        pass

    def draw(self, window):
        long = len(self.game_manager.spellManager.hotbar_items)
        for i, rect in enumerate(self.slots):
            pygame.draw.rect(window, (50, 50, 50), rect, border_radius=6)

            if i == self.selected_index:
                pygame.draw.rect(window, (255, 255, 255), rect, 4, border_radius=6)
            else:
                pygame.draw.rect(window, (150, 150, 150), rect, 2, border_radius=6)

            if i < long:
                item = self.game_manager.spellManager.hotbar_items[i]["img"]
                if item:
                    img_rect = item.get_rect(center=rect.center)
                    window.blit(item, img_rect)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if pygame.K_1 <= event.key <= pygame.K_9:
                self.selected_index = event.key - pygame.K_1
                self.game_manager.spellManager.set_active_spell(self.selected_index)

        if event.type == pygame.MOUSEWHEEL:
            self.selected_index -= event.y
            self.selected_index %= self.slot_count
            self.game_manager.spellManager.set_active_spell(self.selected_index)
