from src.states.base_state import BaseState

class HomebaseState(BaseState):
    def __init__(self, ss) -> None:
        super().__init__(ss)
        pass

    def enter(self, data: dict = {}):
        pass

    def handle_event(self, e):
        pass
        
    def update(self, dt):
        pass

    def draw(self, screen):
        pass

    def exit(self):
        pass