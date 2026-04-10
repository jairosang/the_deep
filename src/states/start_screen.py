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
            # Creation of play and quit buttons respectively (homebase and underwater buttons for now in order to test each state separately)
            Button((g_config["SCREEN_SIZE"][0]/8 * 3, g_config["SCREEN_SIZE"][1]*2/3), (g_config["SCREEN_SIZE"][0]/4,70), (100,100,100), (130, 130, 130), text="Go to Homebase", font_size=30, func= self._go_to_homebase),
            Button((g_config["SCREEN_SIZE"][0]/8 * 5, g_config["SCREEN_SIZE"][1]*2/3), (g_config["SCREEN_SIZE"][0]/4,70), (100,100,100), (130, 130, 130), text="Go Underwater", font_size=30, func=self._go_to_underwater),
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
        font = pygame.font.Font(None, 130)
        text = font.render("The Deep", True, (80, 80, 255))  # Blue temporary game name
        text_rect = text.get_rect(center=(g_config["SCREEN_SIZE"][0] / 2, g_config["SCREEN_SIZE"][1] / 3)) #centered on screen
        screen.blit(text, text_rect)

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