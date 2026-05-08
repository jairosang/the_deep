import pygame
from pathlib import Path
from ui import Button, get_font
from .base_state import BaseState
from config import game as g_config
from utils import Animation, load_frames_from_folder


class StartScreen(BaseState):
    def __init__(self) -> None:
        super().__init__()
        self.buttons: list[Button] = []
        self.anim = Animation(load_frames_from_folder("./assets/background/animated_test/", True), 15)

    #==== Abstract Methods from base class =====
    def enter(self):
        screen_w, screen_h = g_config["SCREEN_SIZE"]

        # Background
        bg_path = Path("assets/background/menu_background.png")
        # raw_bg = pygame.image.load(str(bg_path)).convert()
        # self.background = pygame.transform.smoothscale(raw_bg, (int(screen_w), int(screen_h)))

        self.overlay = pygame.Surface((int(screen_w), int(screen_h)), pygame.SRCALPHA)
        self.overlay.fill((0, 10, 25, 70))

        # Title
        title_font = get_font(128, "primary", bold=True)
        self.title_surf = title_font.render("THE DEEP", True, (216, 232, 252))
        self.title_outline = title_font.render("THE DEEP", True, (22, 34, 52))

        # Buttons
        cx = screen_w / 2
        btn_w = screen_w / 4
        btn_h = 70
        gap = 22
        first_btn_y = screen_h * 0.72

        # Free lists on each entery
        self.buttons = [
            Button((cx, first_btn_y), (btn_w, btn_h), (50, 105, 160), (85, 155, 210), text="Go Underwater", font_size=30, font_color=(240, 250, 255), border_radius=14, border_color=(130, 185, 230), border_width=2, func=self._go_to_underwater,),
            Button((cx, first_btn_y + (btn_h + gap)), (btn_w, btn_h), (50, 105, 160), (85, 155, 210), text="Go to Homebase", font_size=30, font_color=(240, 250, 255), border_radius=14, border_color=(130, 185, 230), border_width=2, func=self._go_to_homebase,),
            Button((cx, first_btn_y + 2 * (btn_h + gap)), (btn_w, btn_h), (200, 70, 60), (230, 95, 80), text="Quit", font_size=30, font_color=(255, 240, 235), border_radius=14, border_color=(255, 160, 140), border_width=2, func=self.quit_game,),
        ]

    def handle_event(self, e: pygame.event.Event):
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            click_pos = e.pos
            for button in self.buttons:
                if button.rect.collidepoint(click_pos):
                    button.call_back()
        elif e.type == pygame.MOUSEMOTION:
            for button in self.buttons:
                button.check_mouseover(e.pos)

    def update(self, dt):
        self.anim.update(dt)

    def draw(self, screen: pygame.Surface, is_debug_on):
        screen_w, screen_h = g_config["SCREEN_SIZE"]

        # Background
        screen.blit(self.anim.get_image(), (0, 0))
        screen.blit(self.overlay, (0, 0))

        # Title and outline
        title_rect = self.title_surf.get_rect(center=(screen_w / 2, screen_h * 0.30))
        for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            screen.blit(self.title_outline, title_rect.move(dx, dy))
        screen.blit(self.title_surf, title_rect)

        for button in self.buttons:
            button.draw(screen)

    def exit(self):
        pass


    #==== Own Methods ====
    def quit_game(self):
        self.is_quitting = True

    def _go_to_underwater(self):
        self.is_done = (True, "UNDERWATER")

    def _go_to_homebase(self):
        self.is_done = (True, "HOMEBASE")
