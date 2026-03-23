from src.states.base_state import BaseState
from src.entities.player import Player
import pygame

class HomebaseState(BaseState):
    def __init__(self, player: Player) -> None:
        super().__init__()
        self.player = player

    def enter(self, data: dict = {}):
        self.player.movement_axis.y = 0  # Horizontal movement only

    def handle_event(self, e):
        pass

    def handle_inputs(self, keys: pygame.key.ScancodeWrapper, mouse_pos: tuple[int, int]):
        pass
        
    def update(self, dt):
        self.player.update(dt)

    def draw(self, screen, is_debug_on):
        self.player.draw(screen)

    def exit(self):
        self.player.movement_axis.y = 1  # Return full movement