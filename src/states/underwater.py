import pygame
from src.ui.components.button import Button
from src.states.base_state import BaseState

class UnderwaterState(BaseState):
    def __init__(self, ss) -> None:
        super().__init__(ss)
        pass

    #==== Abstract Methods from base class =====
    def enter(self, data: dict = {}):
        self.button = Button((self.screen_size[0]/16,20),(self.screen_size[0]/8,40), (245, 96, 66), (209, 80, 54), text="Return", func=self.exit)

    def handle_event(self, e: pygame.event.Event):
        if e.type == pygame.MOUSEBUTTONDOWN and self.button.rect.collidepoint(pygame.mouse.get_pos()):
            self.button.call_back()
        
    def update(self, dt):
        pygame.display.flip()

    def draw(self, screen: pygame.Surface):
        screen.fill((80, 128, 173))
        self.button.draw(screen)

    def exit(self):
        self.is_done = (True, "START_SCREEN")


    # ==== Own Methods ====
    def spawn_creatures(self):
        pass

    def check_return_point(self):
        pass

    def update_depth(self):
        pass

    def trigger_game_over(self):
        pass

    