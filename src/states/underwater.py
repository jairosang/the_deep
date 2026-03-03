import pygame
import random
from src.ui.components.button import Button
from src.states.base_state import BaseState
from src.entities.player import Player
from src.entities.creatures.base_creature import Creature
from src.entities.creatures.creature_passive import PassiveCreature
from src.entities.creatures.creature_aggressive import AggressiveCreature
from config import game as g_config
from src.utils.tile_map import TileMap

class UnderwaterState(BaseState):
    def __init__(self, player: Player) -> None:
        super().__init__()
        self.player = player
        self.creatures: list[Creature] = []
        self.tile_map = TileMap(g_config["TILEMAP_PATH"])

    #==== Abstract Methods from base class =====
    def enter(self, data: dict = {}):
        self.button = Button((g_config["SCREEN_SIZE"][0]/16,20),(g_config["SCREEN_SIZE"][0]/8,40), (245, 96, 66), (209, 80, 54), text="Return", func=self.exit)
        self.spawn_creatures()

    def handle_event(self, e: pygame.event.Event):
        if e.type == pygame.MOUSEBUTTONDOWN and self.button.rect.collidepoint(pygame.mouse.get_pos()):
            self.button.call_back()

    def update(self, dt):
        self.player.update(dt)
        bounds = pygame.Rect(
            0,
            0,
            int(g_config["SCREEN_SIZE"][0]),
            int(g_config["SCREEN_SIZE"][1]) # make creatures stay within bounds
        )
        
        for c in self.creatures:
            c.update(dt, self.player, bounds)
        pygame.display.flip()

        if self.player.oxygen <= 0:
            self.is_done = (True, "GAME_OVER")

    def draw(self, screen: pygame.Surface):
        screen.fill((80, 128, 173))
        self.tile_map.draw(screen)
        # Just telling the guys to draw themselves
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
        w, h = g_config["SCREEN_SIZE"]

        for _ in range(6):
            x = random.randint(40, int(w) - 40)
            y = random.randint(80, int(h) - 40)
            self.creatures.append(PassiveCreature((x, y), size=18, speed=140, fear_radius=160))

        for _ in range(2):
            x = random.randint(40, int(w) - 40)
            y = random.randint(80, int(h) - 40)
            self.creatures.append(AggressiveCreature((x, y), size=18, speed=140, chase_radius=160))

    def check_return_point(self):
        pass

    def update_depth(self):
        pass

    def trigger_game_over(self):
        pass

    