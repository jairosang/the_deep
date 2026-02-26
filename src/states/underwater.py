import pygame
import random
from src.ui.components.button import Button
from src.states.base_state import BaseState
from src.entities.player import Player
from src.entities.creatures.base_creature import Creature

class UnderwaterState(BaseState):
    def __init__(self, ss, player: Player) -> None:
        super().__init__(ss)
        self.player = player
        self.creatures: list[Creature] = []

    #==== Abstract Methods from base class =====
    def enter(self, data: dict = {}):
        self.button = Button((self.screen_size[0]/16,20),(self.screen_size[0]/8,40), (245, 96, 66), (209, 80, 54), text="Return", func=self.exit)
        self.spawn_creatures()

    def handle_event(self, e: pygame.event.Event):
        if e.type == pygame.MOUSEBUTTONDOWN and self.button.rect.collidepoint(pygame.mouse.get_pos()):
            self.button.call_back()

    def update(self, dt):
        self.player.update(dt)
        for c in self.creatures:
            c.update(dt)
        pygame.display.flip()

    def draw(self, screen: pygame.Surface):
        screen.fill((80, 128, 173))
        for c in self.creatures:
            c.draw(screen)
        self.player.draw(screen)
        self.button.draw(screen)

    def exit(self):
        self.player.revert()
        self.is_done = (True, "START_SCREEN")


    # ==== Own Methods ====
    def spawn_creatures(self):
        self.creatures.clear()
        w, h = self.screen_size

        for _ in range(8):
            x = random.randint(40, int(w) - 40)
            y = random.randint(80, int(h) - 40)
            self.creatures.append(Creature((x, y), size=20))

    def check_return_point(self):
        pass

    def update_depth(self):
        pass

    def trigger_game_over(self):
        pass

    