import pygame
import pygame_menu
from pygame_menu import themes


class InventoryMenu:
    def __init__(self, screen_width=600, screen_height=400):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.items = []
        self.is_open = False
        self.create_inventory_menu()

    def create_inventory_menu(self):
        self.inventory_menu = pygame_menu.Menu('Inventory', self.screen_width, self.screen_height, theme=themes.THEME_DARK)

        # items
        self.inventory_menu.add.label('Your items:')
        self.inventory_menu.add.vertical_margin(20)

        self.add_inventory_item('Scanner', 'Tool', '* For Research Only')
        self.add_inventory_item('Weapon', 'Tool', '5 damage')
        self.add_inventory_item('Harpoon', 'Tool', '1 damage')

        self.inventory_menu.add.button('Back', self.close)

    def add_inventory_item(self, name, item_type, description):
        item_text = f"{name} - {item_type}: {description}"
        self.inventory_menu.add.button(item_text, self.select_item, name)

    def select_item(self, item_name):
        print(f"Selected: {item_name}")

    def open(self):
        self.is_open = True
        self.inventory_menu.enable()

    def close(self):
        self.is_open = False
        self.inventory_menu.disable()

    def toggle(self):
        if self.is_open:
            self.close()
        else:
            self.open()

    def handle_event(self, e):
        if self.is_open and self.inventory_menu.is_enabled():
            self.inventory_menu.update([e])

    def draw(self, screen):
        if self.is_open and self.inventory_menu.is_enabled():
            self.inventory_menu.draw(screen)

    def update_items(self, new_items):
        self.items = new_items
        self.inventory_menu.clear()
        self.inventory_menu.add.label('Your items:')
        self.inventory_menu.add.vertical_margin(20)
        for name, item_type, description in self.items:
            self.add_inventory_item(name, item_type, description)
        self.inventory_menu.add.button('Back', self.close)

    def get_menu(self):
        return self.inventory_menu
