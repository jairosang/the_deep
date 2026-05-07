import pygame
from .base_menu import BaseMenu
from ..components.button import Button
from config import game as g_config
from ..font import get_font


class PauseMenu(BaseMenu):
    # simple pause popup with Resume and Main Menu
    def __init__(self, on_resume, on_main_menu) -> None:
        super().__init__()
        self.on_resume = on_resume
        self.on_main_menu = on_main_menu
        self.title_font = get_font(42)
        self._build_buttons()

    def _build_buttons(self) -> None:
        screen_w, screen_h = g_config["SCREEN_SIZE"]
        center_x = screen_w / 2
        first_y = screen_h / 2
        btn_size = (280, 62)
        gap = 18

        self.buttons = [
            Button((center_x, first_y), btn_size, (50, 105, 160), (85, 155, 210), text="Resume", font_size=28, font_color=(240, 250, 255), border_radius=12, border_color=(130, 185, 230), border_width=2, func=self.on_resume,),
            Button((center_x, first_y + btn_size[1] + gap), btn_size, (200, 70, 60), (230, 95, 80), text="Main Menu", font_size=28, font_color=(255, 240, 235), border_radius=12, border_color=(255, 160, 140), border_width=2, func=self.on_main_menu,),
        ]

    def open(self) -> None:
        self.is_open = True
        # Rebuild buttons on open so they stay in the center of screen
        self._build_buttons()

    def close(self) -> None:
        self.is_open = False

    def handle_event(self, e: pygame.event.Event) -> None:
        if not self.is_open:
            return

        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            for button in self.buttons:
                if button.rect.collidepoint(e.pos):
                    button.call_back()
        elif e.type == pygame.MOUSEMOTION:
            for button in self.buttons:
                button.check_mouseover(e.pos)

    def update(self, dt: float) -> None:
        # abstract method from base class
        pass

    def draw(self, surface: pygame.Surface) -> None:
        if not self.is_open:
            return

        screen_w, screen_h = g_config["SCREEN_SIZE"]

        overlay = pygame.Surface((int(screen_w), int(screen_h)), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 155))
        surface.blit(overlay, (0, 0))

        title_surf = self.title_font.render("Paused", True, (240, 250, 255))
        title_rect = title_surf.get_rect(center=(screen_w / 2, screen_h / 2 - 95))
        surface.blit(title_surf, title_rect)

        for button in self.buttons:
            button.draw(surface)
