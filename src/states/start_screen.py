import pygame
from pygame.key import ScancodeWrapper
from src.ui.components.button import Button
from src.states.base_state import BaseState
from config import game as g_config

class StartScreen(BaseState):
    def __init__(self) -> None:
        super().__init__()
        self.buttons: list[Button] = []
        pass
    
    #==== Abstract Methods from base class =====
    def enter(self):
        self.buttons += [
            # Creation of play and quit buttons respectively
            Button((g_config["SCREEN_SIZE"][0]/2, g_config["SCREEN_SIZE"][1]*2/3), (g_config["SCREEN_SIZE"][0]/2,70), (100,100,100), (130, 130, 130), text="Play Game", font_size=30, func=self.exit),
            Button((g_config["SCREEN_SIZE"][0]/2, g_config["SCREEN_SIZE"][1]*4/5), (g_config["SCREEN_SIZE"][0]/2,70), (245, 96, 66), (209, 80, 54), text="QUIT", font_size=30, func=self.quit_game),
        ]


    def handle_event(self, e: pygame.event.Event):
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            click_pos = e.pos
            print(f"Event of type: {e.type} detected:\n{e}\n")
            for button in self.buttons:
                if button.rect.collidepoint(click_pos):
                    button.call_back()

    def handle_inputs(self, keys: ScancodeWrapper, mouse_pos: tuple[int, int]):
        for button in self.buttons:
            button.check_mouseover(mouse_pos)
        
    def update(self, dt):
        pass

    def draw(self, screen: pygame.Surface, is_debug_on):
        screen.fill((0,0,0))
        for button in self.buttons:
            button.draw(screen)

    def exit(self):
        self.is_done = (True, "UNDERWATER")
    

    #==== Own Methods ====
    def quit_game(self):
        self.is_quitting = True

