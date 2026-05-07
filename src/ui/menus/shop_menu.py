import pygame
from .base_menu import BaseMenu
from ..components.button import Button
from config import game as g_config


class ShopMenu(BaseMenu):
    # Lists each species in the buffer inventory with its price and amount, can also sell all items at once
    def __init__(self, get_listings, get_total_value, get_wallet, on_sell_all, on_close) -> None:
        super().__init__()
        self.get_listings = get_listings
        self.get_total_value = get_total_value
        self.get_wallet = get_wallet
        self.on_sell_all = on_sell_all
        self.on_close = on_close
        self.status_text = ""

        self.title_font = pygame.font.SysFont("Segoe Print", 44)
        self.row_font = pygame.font.SysFont("Segoe Print", 26)
        self.body_font = pygame.font.SysFont("Segoe Print", 24)
        self.small_font = pygame.font.SysFont("Segoe Print", 22)

        self._build_buttons()

    def _build_buttons(self) -> None:
        screen_w, screen_h = g_config["SCREEN_SIZE"]
        cx = screen_w / 2
        cy = screen_h / 2

        self.close_btn = Button((cx - 120, cy + 210), (190, 58), (110, 110, 110), (145, 145, 145), text="Close", font_size=30, font_color=(35, 35, 35), border_radius=8, border_color=(210, 210, 210), border_width=2, func=self.on_close,)
        self.sell_btn = Button((cx + 120, cy + 210), (190, 58), (243, 186, 72), (255, 206, 92), text="Sell All", font_size=30, font_color=(30, 30, 30), border_radius=8, border_color=(255, 228, 145), border_width=2, func=self._sell_all,)

        self._all_buttons = [self.close_btn, self.sell_btn]

    def _sell_all(self) -> None:
        self.status_text = self.on_sell_all()

    def open(self) -> None:
        self.is_open = True
        self.status_text = ""
        self._build_buttons()

    def close(self) -> None:
        self.is_open = False
        self.status_text = ""

    def handle_event(self, e: pygame.event.Event) -> None:
        if not self.is_open:
            return

        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_RETURN:
                self._sell_all()
            elif e.key == pygame.K_ESCAPE:
                self.on_close()

        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            for button in self._all_buttons:
                if button.rect.collidepoint(e.pos):
                    button.call_back()
        elif e.type == pygame.MOUSEMOTION:
            for button in self._all_buttons:
                button.check_mouseover(e.pos)

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        if not self.is_open:
            return

        listings = self.get_listings()
        wallet = self.get_wallet()
        total_value = self.get_total_value()

        screen_w, screen_h = g_config["SCREEN_SIZE"]
        cx = screen_w / 2
        cy = screen_h / 2

        overlay = pygame.Surface((int(screen_w), int(screen_h)), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        surface.blit(overlay, (0, 0))

        panel_rect = pygame.Rect(cx - 280, cy - 220, 560, 460)
        inner_rect = panel_rect.inflate(-22, -22)
        pygame.draw.rect(surface, (20, 24, 32), panel_rect, border_radius=8)
        pygame.draw.rect(surface, (255, 195, 86), panel_rect, width=3, border_radius=8)
        pygame.draw.rect(surface, (12, 15, 21), inner_rect, border_radius=8)

        title = self.title_font.render("SELL", True, (255, 195, 86))
        title_rect = title.get_rect(center=(cx, cy - 175))
        surface.blit(title, title_rect)

        list_top = cy - 130
        list_bottom = cy + 100
        row_height = 34

        if not listings:
            empty = self.body_font.render("Inventory is empty.", True, (200, 210, 225))
            empty_rect = empty.get_rect(center=(cx, (list_top + list_bottom) / 2))
            surface.blit(empty, empty_rect)
        else:
            max_rows = int((list_bottom - list_top) // row_height)
            visible = listings[:max_rows]

            for index, entry in enumerate(visible):
                y = list_top + index * row_height + row_height / 2

                left_text = f"{entry['label']} - {entry['amount']}"
                right_text = f"${entry['total']}"

                left_surf = self.row_font.render(left_text, True, (240, 240, 240))
                right_surf = self.row_font.render(right_text, True, (255, 220, 130))

                left_rect = left_surf.get_rect(midleft=(panel_rect.left + 50, y))
                right_rect = right_surf.get_rect(midright=(panel_rect.right - 50, y))

                surface.blit(left_surf, left_rect)
                surface.blit(right_surf, right_rect)

            if len(listings) > max_rows:
                more = self.small_font.render(f"+{len(listings) - max_rows} more...", True, (180, 200, 220))
                more_rect = more.get_rect(center=(cx, list_bottom - 8))
                surface.blit(more, more_rect)

        total_label = self.body_font.render(f"Total: ${total_value}", True, (255, 220, 130))
        total_rect = total_label.get_rect(center=(cx, cy + 130))
        surface.blit(total_label, total_rect)

        wallet_label = self.small_font.render(f"You have: ${wallet}", True, (180, 200, 220))
        wallet_rect = wallet_label.get_rect(center=(cx, cy + 158))
        surface.blit(wallet_label, wallet_rect)

        if self.status_text:
            status = self.small_font.render(self.status_text, True, (255, 220, 120))
            status_rect = status.get_rect(center=(cx, cy + 180))
            surface.blit(status, status_rect)

        for button in self._all_buttons:
            button.draw(surface)
