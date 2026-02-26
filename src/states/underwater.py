import pygame
from src.ui.components.button import Button
from src.states.base_state import BaseState
from src.entities.player import Player

class UnderwaterState(BaseState):
    def __init__(self, ss, player: Player) -> None:
        super().__init__(ss)
        self.player = player

    #==== Abstract Methods from base class =====
    def enter(self, data: dict = {}):
        self.button = Button((self.screen_size[0]/16,20),(self.screen_size[0]/8,40), (245, 96, 66), (209, 80, 54), text="Return", func=self.exit)

    def handle_event(self, e: pygame.event.Event):
        if e.type == pygame.MOUSEBUTTONDOWN and self.button.rect.collidepoint(pygame.mouse.get_pos()):
            self.button.call_back()

    def update(self, dt):
        # Just telling the guys to update themselves now
        self.player.update(dt)
        pygame.display.flip()

    def draw(self, screen: pygame.Surface):
        screen.fill((80, 128, 173))
        # Just telling the guys to draw themselves
        self.player.draw(screen)
        self.button.draw(screen)

        # This thing is a temporary thing for displaying the oxygen thing in the bottom left corner of the screen thing
        oxygen_text = pygame.font.Font(None, 36).render(f"O2: {self.player.oxygen:.0f}", True, (255, 255, 255))
        screen.blit(oxygen_text, (10, self.screen_size[1] - 50))

    def exit(self):
        self.player.revert()
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

    