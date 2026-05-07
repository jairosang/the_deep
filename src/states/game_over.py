import pygame
from .base_state import BaseState
from ui import Button, get_font
from config import game as g_config

class GameOverState(BaseState):
    def __init__(self) -> None:
        super().__init__()
        self.buttons: list[Button] = []

    def enter(self, data: dict = {}):
        self.buttons += [
        Button((g_config["SCREEN_SIZE"][0]/2, g_config["SCREEN_SIZE"][1]*2/3), (g_config["SCREEN_SIZE"][0]/2,70), (100,100,100), (130, 130, 130), text="Respawn", font_size=30, func=self.exit),
        Button((g_config["SCREEN_SIZE"][0]/2, g_config["SCREEN_SIZE"][1]*4/5), (g_config["SCREEN_SIZE"][0]/2,70), (245, 96, 66), (209, 80, 54), text="QUIT", font_size=30, func=self.quit_game)
        ]

    def handle_event(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            click_pos = e.pos
            print(f"Event of type: {e.type} detected:\n{e}\n")
            for button in self.buttons:
                if button.rect.collidepoint(click_pos):
                    button.call_back()
        
    def update(self, dt):
        pass

    def draw(self, screen, is_debug_on):
        screen.fill((20, 20, 30))   #fill with 1 color

        font = get_font(72)
        text = font.render("GAME OVER", True, (255, 80, 80))   # red text
        text_rect = text.get_rect(center=(g_config["SCREEN_SIZE"][0] / 2, g_config["SCREEN_SIZE"][1] / 2)) #centered on screen
        screen.blit(text, text_rect)
        for button in self.buttons:
            button.draw(screen)

    def exit(self):
        self.is_done = (True, "START_SCREEN")

    def quit_game(self):
        self.is_quitting = True