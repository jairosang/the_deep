import pygame
import pygame_menu
from pygame_menu import themes
import math
import random
from src.states.base_state import BaseState
from config import game as g_config


# old main menu
# class StartScreen(BaseState):
#     def __init__(self) -> None:
#         super().__init__()
#         self.buttons: list[Button] = []
#         pass
#
#     #==== Abstract Methods from base class =====
#     def enter(self):
#         self.buttons += [
#             # Creation of play and quit buttons respectively
#             Button((g_config["SCREEN_SIZE"][0]/2, g_config["SCREEN_SIZE"][1]*2/3), (g_config["SCREEN_SIZE"][0]/2,70), (100,100,100), (130, 130, 130), text="Play Game", font_size=30, func=self.exit),
#             Button((g_config["SCREEN_SIZE"][0]/2, g_config["SCREEN_SIZE"][1]*4/5), (g_config["SCREEN_SIZE"][0]/2,70), (245, 96, 66), (209, 80, 54), text="QUIT", font_size=30, func=self.quit_game),
#         ]
#
#
#     def handle_event(self, e: pygame.event.Event):
#         if e.type == pygame.MOUSEBUTTONDOWN:
#             for button in self.buttons:
#                 if button.rect.collidepoint(pygame.mouse.get_pos()):
#                     if button.func is not None:
#                         button.func()
#
#     def update(self, dt):
#         pygame.display.flip()
#
#     def draw(self, screen: pygame.Surface):
#         screen.fill((0,0,0))
#         for button in self.buttons:
#             button.draw(screen)
#
#     def exit(self):
#         self.is_done = (True, "UNDERWATER")
#
#
#     #==== Own Methods ====
#     def quit_game(self):
#         self.is_quitting = True


# new start screen
class StartScreen(BaseState):
    def __init__(self) -> None:
        super().__init__()
        self.time = 0.0
        self.bubbles = []
        self.menu = None
        self.s_width = 0
        self.s_height = 0
        self.gradient_surf = None
        self.beam_base = None
        self.shimmer_surf = None
        self.bx = 0
        self.top_w = 0
        self.bot_w = 0

    # Abstract Methods from base class
    def enter(self):
        self.s_width, self.s_height = g_config["SCREEN_SIZE"]
        self._build_background()
        self._build_menu()
        self.bubbles = [self._Bubble(self.s_width, self.s_height) for _ in range(70)]

    def handle_event(self, e: pygame.event.Event):
        if self.menu and self.menu.is_enabled():
            self.menu.update([e])

    def update(self, dt):
        self.time += dt
        for b in self.bubbles:
            b.update()

    def draw(self, screen: pygame.Surface):
        screen.blit(self.gradient_surf, (0, 0))
        self._draw_beam(screen, self.time)
        for b in self.bubbles:
            b.draw(screen)

        if self.menu and self.menu.is_enabled():
            self.menu.draw(screen)

        pygame.display.flip()

    def exit(self):
        self.is_done = (True, "UNDERWATER")

    def quit_game(self):
        self.is_quitting = True

    def _build_background(self):
        w, h = self.s_width, self.s_height

        self.gradient_surf = pygame.Surface((w, h))
        for y in range(h):
            t = y / h
            self.gradient_surf.fill(
                (int(2 + t * 4), int(8 + t * 20), int(38 + t * 50)),
                rect=(0, y, w, 1),
            )

        self.bx = w // 2
        self.top_w = w // 14
        self.bot_w = w // 5
        self.beam_base = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.polygon(
            self.beam_base,
            (20, 90, 200, 10),
            [
                (self.bx - self.top_w, 0),
                (self.bx + self.top_w, 0),
                (self.bx + self.bot_w, h),
                (self.bx - self.bot_w, h),
            ],
        )
        self.shimmer_surf = pygame.Surface((w, h), pygame.SRCALPHA)

    def _draw_beam(self, surf, t):
        surf.blit(self.beam_base, (0, 0))
        self.shimmer_surf.fill((0, 0, 0, 0))
        for i in range(4):
            phase = (t * 0.35 + i * 0.25) % 1.0
            sy = int(phase * self.s_height)
            lw = int(self.top_w + (self.bot_w - self.top_w) * phase)
            pygame.draw.line(
                self.shimmer_surf, (100, 180, 255, 14),
                (self.bx - lw, sy), (self.bx + lw, sy), 1,
            )
        surf.blit(self.shimmer_surf, (0, 0))

    def _build_menu(self):
        w, h = self.s_width, self.s_height
        menu_w = int(w * 0.38)
        menu_h = int(h * 0.72)

        hub_theme = themes.THEME_DARK.copy()
        hub_theme.background_color = (5, 15, 40, 210)
        hub_theme.title_background_color = (0, 25, 70, 240)
        hub_theme.title_font_color = (0, 210, 255)
        hub_theme.title_font_size = max(28, h // 22)
        hub_theme.widget_font_size = max(20, h // 32)
        hub_theme.widget_selection_effect = pygame_menu.widgets.HighlightSelection(
            border_width=2, margin_x=18, margin_y=8
        )
        hub_theme.selection_color = (0, 210, 255)

        self.menu = pygame_menu.Menu("Welcome to Hub", menu_w, menu_h, theme=hub_theme)
        self.menu.add.button("Start the Dive", self.exit)
        self.menu.add.button("Quit", self.quit_game)

    class _Bubble:
        def __init__(self, s_width, s_height):
            self.s_width = s_width
            self.s_height = s_height
            self.x = self.y = self.r = 0
            self.speed = self.phase = self.wfreq = self.alpha = 0
            self.surf = None
            self.spawn()

        def spawn(self):
            self.x = random.uniform(0, self.s_width)
            self.y = random.uniform(self.s_height, self.s_height + 200)
            self.r = random.randint(2, 8)
            self.speed = random.uniform(0.5, 2.2)
            self.phase = random.uniform(0, math.tau)
            self.wfreq = random.uniform(0.02, 0.06)
            self.alpha = random.randint(45, 120)
            d = self.r * 2 + 6
            self.surf = pygame.Surface((d, d), pygame.SRCALPHA)
            c = d // 2
            pygame.draw.circle(self.surf, (160, 230, 255, self.alpha), (c, c), self.r, 2)
            hl_r = max(1, self.r // 4)
            hl_alpha = min(self.alpha + 60, 200)
            pygame.draw.circle(
                self.surf,
                (255, 255, 255, hl_alpha),
                (c - max(1, self.r // 3), c - max(1, self.r // 3)),
                hl_r,
            )

        def update(self):
            self.y -= self.speed
            self.phase += self.wfreq
            self.x += math.sin(self.phase) * 0.7
            if self.y < -self.r:
                self.spawn()

        def draw(self, surf):
            c = self.surf.get_width() // 2
            surf.blit(self.surf, (int(self.x) - c, int(self.y) - c))

