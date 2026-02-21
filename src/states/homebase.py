from src.states.base_state import BaseState
from src.entities.player import Player

class HomebaseState(BaseState):
    def __init__(self, ss, player: Player) -> None:
        super().__init__(ss)
        self.player = player

    def enter(self, data: dict = {}):
        self.player.movement_axis.y = 0  # Horizontal movement only

    def handle_event(self, e):
        pass
        
    def update(self, dt):
        self.player.update(dt)

    def draw(self, screen):
        self.player.draw(screen)

    def exit(self):
        self.player.movement_axis.y = 1  # Return full movement