import pygame
from src.states.base_state import BaseState

class GameOverState(BaseState):
    def __init__(self, ss) -> None:
        super().__init__(ss)

    def enter(self, data: dict = {}):
        pass

    def handle_event(self, e):
        pass

    def handle_inputs(self, keys: pygame.key.ScancodeWrapper, mouse_pos: tuple[int, int]):
        pass
        
    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill((20, 20, 30))   #fill with 1 color

        font = pygame.font.Font(None, 72)
        text = font.render("GAME OVER", True, (255, 80, 80))   # red text
        text_rect = text.get_rect(center=(self.screen_size[0] / 2, self.screen_size[1] / 2)) #centered on screen
        screen.blit(text, text_rect)

    def exit(self):
        pass