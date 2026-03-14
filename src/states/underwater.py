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
from src.utils.camera import Camera
from src.ui.menus.inventory_menu import InventoryMenu

class UnderwaterState(BaseState):
    def __init__(self, player: Player) -> None:
        super().__init__()
        self.player = player
        self.creatures: list[Creature] = []
        self.tile_map = TileMap(g_config["TILEMAP_PATH"])
        self.world_surface = pygame.Surface(self.tile_map.map_size, pygame.SRCALPHA)
        
        self.world_rect = pygame.Rect(0, 0, self.tile_map.map_size[0], self.tile_map.map_size[1])
        self.camera = Camera(g_config["SCREEN_SIZE"], self.world_rect)
        self.inventory = InventoryMenu(g_config["SCREEN_SIZE"][0], g_config["SCREEN_SIZE"][1])

    #==== Abstract Methods from base class =====
    def enter(self, data: dict = {}):
        self.button = Button((g_config["SCREEN_SIZE"][0]/16,20),(g_config["SCREEN_SIZE"][0]/8,40), (245, 96, 66), (209, 80, 54), text="Return", func=self.exit)
        self.spawn_creatures()

    def handle_event(self, e: pygame.event.Event):
        if e.type == pygame.KEYDOWN and e.key == pygame.K_e:
            self.inventory.toggle()
            return

        if self.inventory.is_open:
            self.inventory.handle_event(e)
            return

        if e.type == pygame.MOUSEBUTTONDOWN and self.button.rect.collidepoint(pygame.mouse.get_pos()):
            self.button.call_back()

    def update(self, dt):
        self.player.update(dt, bound_rect=self.world_rect)
        self.camera.update(dt, self.player.rect)
        bounds = pygame.Rect(
            0,
            0,
            int(g_config["SCREEN_SIZE"][0]),
            int(g_config["SCREEN_SIZE"][1]) # make creatures stay within bounds
        )
        player_pos = pygame.math.Vector2(self.player.rect.center)
        for c in self.creatures:
            c.update(dt, player_pos, bounds)

        if self.player.oxygen <= 0:
            self.is_done = (True, "GAME_OVER")
        pygame.display.flip()

    def draw(self, screen: pygame.Surface):
        self.world_surface.fill((80, 128, 173))
        self.tile_map.draw(self.world_surface, self.camera.rect)
        self.player.draw(self.world_surface)

        # Just telling the guys to draw themselves
        for c in self.creatures:
            c.draw(self.world_surface)
        
        self.camera.draw(self.world_surface, screen)
        self.button.draw(screen)

        # This thing is a temporary thing for displaying the oxygen thing in the bottom left corner of the screen thing
        oxygen_text = pygame.font.Font(None, 36).render(f"O2: {self.player.oxygen:.0f}", True, (255, 255, 255))
        screen.blit(oxygen_text, (10, g_config["SCREEN_SIZE"][1] - 50))

        self.inventory.draw(screen)
        pygame.display.flip()

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
        self.player.revert()   # go back to initial stats for the next run
        self.is_done = (True, "GAME_OVER")  #switch states

    