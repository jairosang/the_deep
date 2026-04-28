import pygame
from .base_menu import BaseMenu
from config import game as g_config


class InventoryMenu(BaseMenu):
    # inventory grid, empty squares for now
    def __init__(self, rows: int = 4, cols: int = 8, slot_size: tuple[int, int] = (60, 60), padding: int = 8) -> None:
        super().__init__()
        self.rows = rows
        self.cols = cols
        self.slot_size = slot_size
        self.padding = padding
        self.title_font = pygame.font.SysFont("Segoe Print", 28)

    def open(self) -> None:
        self.is_open = True

    def close(self) -> None:
        self.is_open = False

    def toggle(self) -> None:
        # Convenience flip so the state can call one method
        if self.is_open:
            self.close()
        else:
            self.open()

    def handle_event(self, e: pygame.event.Event) -> None:
        # Empty for now
        pass

    def update(self, dt: float) -> None:
        # No animation, later
        pass

    def draw(self, surface: pygame.Surface) -> None:
        if not self.is_open:
            return

        screen_w, screen_h = g_config["SCREEN_SIZE"]

        # the menu pops
        overlay = pygame.Surface((int(screen_w), int(screen_h)), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        surface.blit(overlay, (0, 0))

        # Total grid size and the gap between slots
        grid_w = self.cols * self.slot_size[0] + (self.cols - 1) * self.padding
        grid_h = self.rows * self.slot_size[1] + (self.rows - 1) * self.padding

        # Outer panel wraps the grid + room for the title at the top
        panel_pad = 24
        title_room = 40
        panel_w = grid_w + panel_pad * 2
        panel_h = grid_h + panel_pad * 2 + title_room

        # Center the panel
        panel_x = (screen_w - panel_w) / 2
        panel_y = (screen_h - panel_h) / 2

        # Panel background and border
        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        pygame.draw.rect(surface, (30, 40, 55), panel_rect, border_radius=12)
        pygame.draw.rect(surface, (130, 185, 230), panel_rect, width=2, border_radius=12)

        # Title at the top of the panel
        title_surf = self.title_font.render("Inventory", True, (240, 250, 255))
        title_rect = title_surf.get_rect(midtop=(panel_x + panel_w / 2, panel_y + 8))
        surface.blit(title_surf, title_rect)

        grid_x0 = panel_x + panel_pad
        grid_y0 = panel_y + panel_pad + title_room

        # Empty square slots, they will be filled later when items picked up
        for row in range(self.rows):
            for col in range(self.cols):
                x = grid_x0 + col * (self.slot_size[0] + self.padding)
                y = grid_y0 + row * (self.slot_size[1] + self.padding)
                slot_rect = pygame.Rect(x, y, self.slot_size[0], self.slot_size[1])
                pygame.draw.rect(surface, (50, 65, 85), slot_rect, border_radius=6)
                pygame.draw.rect(surface, (110, 140, 170), slot_rect, width=1, border_radius=6)
