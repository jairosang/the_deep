import pygame
from pathlib import Path
from .base_menu import BaseMenu
from ..components.button import Button
from config import game as g_config


class UpgradeMenu(BaseMenu):
    # switch windows for each upgrade, each window has a different upgrade
    def __init__(self, get_preview, on_buy, on_close, upgrade_order: list[str] | None = None) -> None:
        super().__init__()
        self.get_preview = get_preview
        self.on_buy = on_buy
        self.on_close = on_close
        self.upgrade_order = upgrade_order if upgrade_order is not None else ["weapon", "scanner", "suit"]
        self.selected_index = 0
        self.status_text = ""

        self.title_font = pygame.font.SysFont("Segoe Print", 44)
        self.section_font = pygame.font.SysFont("Segoe Print", 34)
        self.level_font = pygame.font.SysFont("Segoe Print", 48)
        self.cost_font = pygame.font.SysFont("Segoe Print", 44)
        self.body_font = pygame.font.SysFont("Segoe Print", 24)
        self.small_font = pygame.font.SysFont("Segoe Print", 22)

        self._icons = self._load_icons()
        self._build_buttons()

    @property
    def selected_upgrade(self) -> str:
        return self.upgrade_order[self.selected_index]

    def _load_icons(self) -> dict[str, pygame.Surface]:
        icon_paths = {
            "weapon": Path("assets/holdables/weapon_asset.png"),
            "scanner": Path("assets/holdables/research_gun_asset.png"),
            "suit": Path("assets/holdables/suit_upgrade_icon.png"),
        }
        icons: dict[str, pygame.Surface] = {}
        for key, path in icon_paths.items():
            try:
                img = pygame.image.load(str(path)).convert_alpha()
                icons[key] = img
            except Exception:
                pass
        return icons

    def _build_buttons(self) -> None:
        screen_w, screen_h = g_config["SCREEN_SIZE"]
        cx = screen_w / 2
        cy = screen_h / 2

        self.prev_btn = Button((cx - 190, cy - 110), (70, 48), (85, 95, 110), (115, 130, 150), text="<", font_size=36, font_color=(230, 235, 245), border_radius=8, border_color=(180, 190, 210), border_width=2, func=self._prev_upgrade,)
        self.next_btn = Button((cx + 190, cy - 110), (70, 48), (85, 95, 110), (115, 130, 150), text=">", font_size=36, font_color=(230, 235, 245), border_radius=8, border_color=(180, 190, 210), border_width=2, func=self._next_upgrade,)

        self.close_btn = Button((cx - 120, cy + 210), (190, 58), (110, 110, 110), (145, 145, 145), text="Close", font_size=30, font_color=(35, 35, 35), border_radius=8, border_color=(210, 210, 210), border_width=2, func=self.on_close,)
        self.buy_btn = Button((cx + 120, cy + 210), (190, 58), (243, 186, 72), (255, 206, 92), text="Buy", font_size=33, font_color=(30, 30, 30), border_radius=8, border_color=(255, 228, 145), border_width=2, func=self._buy_selected,)

        self._all_buttons = [self.prev_btn, self.next_btn, self.close_btn, self.buy_btn]

    def _next_upgrade(self) -> None:
        self.selected_index = (self.selected_index + 1) % len(self.upgrade_order)
        self.status_text = ""

    def _prev_upgrade(self) -> None:
        self.selected_index = (self.selected_index - 1) % len(self.upgrade_order)
        self.status_text = ""

    def _buy_selected(self) -> None:
        self.status_text = self.on_buy(self.selected_upgrade)

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
            if e.key == pygame.K_LEFT:
                self._prev_upgrade()
            elif e.key == pygame.K_RIGHT:
                self._next_upgrade()
            elif e.key == pygame.K_RETURN:
                self._buy_selected()
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
    # dt stands for difference in time frames

    def _draw_icon(self, surface: pygame.Surface, key: str, center: tuple[int, int]) -> None:
        icon = self._icons.get(key)
        if icon is None:
            fallback = pygame.Rect(0, 0, 86, 86)
            fallback.center = center
            pygame.draw.rect(surface, (60, 85, 115), fallback, border_radius=8)
            pygame.draw.rect(surface, (170, 200, 230), fallback, width=2, border_radius=8)
            return

        max_size = (92, 92)
        iw, ih = icon.get_size()
        scale = min(max_size[0] / iw, max_size[1] / ih)
        new_size = (max(1, int(iw * scale)), max(1, int(ih * scale)))
        scaled = pygame.transform.smoothscale(icon, new_size)
        rect = scaled.get_rect(center=center)
        surface.blit(scaled, rect)

    def draw(self, surface: pygame.Surface) -> None:
        if not self.is_open:
            return

        info = self.get_preview(self.selected_upgrade)
        screen_w, screen_h = g_config["SCREEN_SIZE"]
        cx = screen_w / 2
        cy = screen_h / 2

        overlay = pygame.Surface((int(screen_w), int(screen_h)), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        surface.blit(overlay, (0, 0))

        panel_rect = pygame.Rect(cx - 280, cy - 180, 560, 360)
        inner_rect = panel_rect.inflate(-22, -22)
        pygame.draw.rect(surface, (20, 24, 32), panel_rect, border_radius=8)
        pygame.draw.rect(surface, (255, 195, 86), panel_rect, width=3, border_radius=8)
        pygame.draw.rect(surface, (12, 15, 21), inner_rect, border_radius=8)

        title = self.title_font.render("UPGRADE?", True, (255, 195, 86))
        title_rect = title.get_rect(center=(cx, cy - 142))
        surface.blit(title, title_rect)

        page_text = self.small_font.render(f"{self.selected_index + 1}/{len(self.upgrade_order)}", True, (185, 200, 220))
        page_rect = page_text.get_rect(center=(cx, cy - 110))
        surface.blit(page_text, page_rect)

        self._draw_icon(surface, info["key"], (cx, cy - 42))

        name = self.section_font.render(info["label"], True, (245, 245, 245))
        name_rect = name.get_rect(center=(cx, cy + 8))
        surface.blit(name, name_rect)

        level_text = self.level_font.render(f"LVL{info['level']} -> LVL{info['next_level']}", True, (245, 245, 245))
        level_rect = level_text.get_rect(center=(cx, cy + 52))
        surface.blit(level_text, level_rect)

        cost_text = self.cost_font.render(f"${info['cost']}", True, (245, 245, 245))
        cost_rect = cost_text.get_rect(center=(cx - 28, cy + 95))
        surface.blit(cost_text, cost_rect)

        desc = self.body_font.render(info["description"], True, (230, 230, 230))
        desc_rect = desc.get_rect(center=(cx, cy + 126))
        surface.blit(desc, desc_rect)

        wallet = self.small_font.render(f"You have: ${info['pesos']}", True, (180, 200, 220))
        wallet_rect = wallet.get_rect(center=(cx, cy + 154))
        surface.blit(wallet, wallet_rect)

        if self.status_text:
            status = self.small_font.render(self.status_text, True, (255, 220, 120))
            status_rect = status.get_rect(center=(cx, cy + 176))
            surface.blit(status, status_rect)
        
        # those are the upgrade stats notifications that appear when players interact with upgrades

        for button in self._all_buttons:
            button.draw(surface)
