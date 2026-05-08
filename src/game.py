import pygame
from src.states.base_state import BaseState

class GameManager():
    def __init__(self, screen, states: dict[str, BaseState], current_state_name: str) -> None:
        self.is_running = True
        self.is_debug_on = False
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.fps = 30
        self.states = states
        self.current_state: BaseState = states[current_state_name]
        self.current_state.enter()

    # Gets events and delegates how to handle them to the state
    def get_whats_going_on(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_l:    # Toggling debug
                self.is_debug_on = not self.is_debug_on
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F6:    # Toggling fullscreen (Doesn't fully work, we would need to rebuild the display as not fullscreen and resizable but I got lazy)
                pygame.display.toggle_fullscreen()
                
            self.current_state.handle_event(event)

    # Checks if state done or game quit signals are sent by states to handle them. Then delegates updating to state.
    def update(self,dt):
        if self.current_state.is_quitting:
            self.is_running = False
        if self.current_state.is_done[0] == True:
            self.transition_states()
        self.current_state.update(dt)

    # Logic for switching states
    def transition_states(self):
        next_state = self.current_state.is_done[1]

        if next_state == None:
            return

        self.current_state.is_done = (False, None)
        self.current_state = self.states[next_state]
        self.current_state.enter()
        self.clock.tick()




    # MAIN LOOP OF THE GAME
    def run(self):
        while self.is_running:
            dt = self.clock.tick(self.fps) / 1000

            self.get_whats_going_on()
            self.update(dt)
            self.current_state.draw(self.screen, self.is_debug_on)
            pygame.display.flip()
        pygame.quit()

