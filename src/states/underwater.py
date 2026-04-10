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
import src.utils.physics_service as phy

class UnderwaterState(BaseState):
    def __init__(self, player: Player) -> None:
        super().__init__()
        self.player = player
        self.creatures: list[Creature] = []
        self.tile_map = TileMap(g_config["TILEMAP_PATH"])
        self.world_surface = pygame.Surface(self.tile_map.map_size, pygame.SRCALPHA)
        
        self.world_rect = pygame.Rect(0, 0, self.tile_map.map_size[0], self.tile_map.map_size[1])
        self.camera = Camera(self.world_rect)

    #==== Abstract Methods from base class =====
    def enter(self, data: dict = {}):
        self.button = Button((g_config["SCREEN_SIZE"][0] - g_config["SCREEN_SIZE"][0]/16,20),(g_config["SCREEN_SIZE"][0]/8,40), (245, 96, 66), (209, 80, 54), text="Return", func=self.exit)
        self.spawn_creatures()

    def handle_event(self, e: pygame.event.Event):
        if e.type == pygame.MOUSEBUTTONDOWN and self.button.rect.collidepoint(pygame.mouse.get_pos()):
            self.button.call_back()

    def handle_inputs(self, keys: pygame.key.ScancodeWrapper, mouse_pos: tuple[int, int]):
        self.player.handle_inputs(keys)

    def update(self, dt):
        # Get rects of tiles surrounding player for calculating collisions with environment 
        area_tiles = self.tile_map.get_tiles_at_area(self.player.rect.centerx, self.player.rect.centery, (7,7))
        self.player.update(dt, self.world_rect, area_tiles)
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

        if self.player.oxygen <= 0 or self.player.health <= 0:
            self.is_done = (True, "GAME_OVER")

        phy.check_entity_collisions(self.player, self.creatures)

    def draw(self, screen: pygame.Surface, is_debug_on):
        # Wiping the world surface, but only the camera area! This really improved the performance.
        self.world_surface.fill((80, 128, 173), self.camera.rect)
        self.tile_map.draw(self.world_surface, self.camera.rect)
        self.player.draw(self.world_surface)

        # Just telling the guys to draw themselves
        for c in self.creatures:
            c.draw(self.world_surface)

        # IMPORTANT, DONT MOVE IT: Debug stuff that must be printed BEFORE camera is drawn !!!!
        if is_debug_on:
            for c in self.creatures:
                pygame.draw.line(self.world_surface, (0,0,255), c.rect.center, c.rect.center + c.velocity)
            
            # Grid with tile separation
            for row_i in range(self.tile_map.mid_layer.width - 1):
                pygame.draw.line(self.world_surface, (0,150,0), (row_i * self.tile_map.tile_size[0], 0),  (row_i * self.tile_map.tile_size[0], self.tile_map.mid_layer.height * self.tile_map.tile_size[1]))
            for col_j in range(self.tile_map.mid_layer.height - 1):
                pygame.draw.line(self.world_surface, (0,150,0), (0, col_j * self.tile_map.tile_size[1]),  (self.tile_map.mid_layer.width * self.tile_map.tile_size[0], col_j * self.tile_map.tile_size[1]))
            
            # Player velocity (with direction)
            pygame.draw.line(self.world_surface, (255,0,0), self.player.rect.center, self.player.rect.center + self.player.velocity)
            pygame.draw.circle(self.world_surface, (0,255,0), self.player.pos, 1)
        
        self.camera.draw(self.world_surface, screen)
        self.button.draw(screen)

        # This thing is a temporary thing for displaying the oxygen thing in the bottom left corner of the screen thing
        oxygen_text = pygame.font.Font(None, 36).render(f"O2: {self.player.oxygen:.0f}", True, (255, 255, 255))
        health_text = pygame.font.Font(None, 36).render(f"Health: {self.player.health:.0f}", True, (255, 255, 255))
        screen.blit(oxygen_text, (10, g_config["SCREEN_SIZE"][1] - 70))
        screen.blit(health_text, (10, g_config["SCREEN_SIZE"][1] - 40))

        # IMPORTANT, DONT MOVE IT: Debug stuff that must be printed AFTER camera is drawn !!!!
        if is_debug_on:
            player_pos_text = pygame.font.Font(None, 36).render(f"Player_pos: {self.player.pos}", True, (255,255,255), (50,50,50))
            screen.blit(player_pos_text, (10, 5))

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
            self.creatures.append(PassiveCreature((x, y), size=18, fear_radius=160))

        for _ in range(2):
            x = random.randint(40, int(w) - 40)
            y = random.randint(80, int(h) - 40)
            self.creatures.append(AggressiveCreature((x, y), size=18, chase_radius=160))

    def check_return_point(self):
        pass

    def update_depth(self):
        pass

    def trigger_game_over(self):
        self.player.revert()   # go back to initial stats for the next run
        self.is_done = (True, "GAME_OVER")  #switch states

    # ========= Private Methods =======