import pygame
from src.ui.components.button import Button
from src.states.base_state import BaseState

class StartScreen(BaseState):
    def __init__(self, ss) -> None:
        super().__init__(ss)
        self.buttons: list[Button] = []
        pass
    
    #==== Abstract Methods from base class =====
    def enter(self):
        self.buttons += [
            # Creation of play and quit buttons respectively
            Button((self.screen_size[0]/2, self.screen_size[1]*2/3), (self.screen_size[0]/2,70), (100,100,100), (130, 130, 130), text="Play Game", font_size=30, func=self.exit),
            Button((self.screen_size[0]/2, self.screen_size[1]*4/5), (self.screen_size[0]/2,70), (245, 96, 66), (209, 80, 54), text="QUIT", font_size=30, func=self.quit_game),
        ]


    def handle_event(self, e: pygame.event.Event):
        if e.type == pygame.MOUSEBUTTONDOWN:
            for button in self.buttons:
                if button.rect.collidepoint(pygame.mouse.get_pos()):
                    if button.func is not None:
                        button.func()
        
    def update(self, dt):
        pygame.display.flip()

    def draw(self, screen: pygame.Surface):
        screen.fill((0,0,0))
        for button in self.buttons:
            button.draw(screen)

    def exit(self):
        self.is_done = (True, "UNDERWATER")
    
    def quit_game(self):
        self.is_quitting = True

