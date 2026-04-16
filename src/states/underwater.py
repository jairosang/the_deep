import pygame
import random
from src.ui.components.button import Button
from src.states.base_state import BaseState
from src.entities.player import Player
from src.entities.creatures.base_creature import Creature
from src.entities.creatures.creature_passive import PassiveCreature
from src.entities.creatures.creature_aggressive import AggressiveCreature
from config import game as g_config
from config import player as p_config
from src.utils.tile_map import TileMap
from src.utils.camera import Camera
import src.utils.physics_service as phy


class UnderwaterState(BaseState):
    def __init__(self, player: Player) -> None:
        super().__init__()
        self.player = player
        self.creatures: list[Creature] = []
        self.items = []
        self.tile_map = TileMap(g_config["UNDERWATER_TILEMAP_PATH"])
        self.world_surface = pygame.Surface(self.tile_map.map_size, pygame.SRCALPHA)
        
        self.world_rect = pygame.Rect(0, 0, self.tile_map.map_size[0], self.tile_map.map_size[1])
        self.camera = Camera(self.world_rect)

    #==== Abstract Methods from base class =====
    def enter(self, data: dict = {}):
        self.player.pos.xy = p_config["UNDERWATER_START_POS"]
        self.button = Button((g_config["SCREEN_SIZE"][0] - g_config["SCREEN_SIZE"][0]/16,20),(g_config["SCREEN_SIZE"][0]/8,40), (245, 96, 66), (209, 80, 54), text="Return", func=self.exit_to_main_menu)
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
            area_tiles = self.tile_map.get_tiles_at_area(c.rect.centerx, c.rect.centery, (7,7))
            c.update(dt, self.world_rect, area_tiles, player_pos)

        if self.player.oxygen <= 0 or self.player.health <= 0:
            self.trigger_game_over()

        dropped_items = phy.check_entity_collisions(self.player, self.creatures)
        self.items.extend(dropped_items)

    def draw(self, screen: pygame.Surface, is_debug_on):
        # Wiping the world surface, but only the camera area! This really improved the performance.
        self.world_surface.fill((80, 128, 173), self.camera.rect)
        self.tile_map.draw(self.world_surface, self.camera.rect)
        self.player.draw(self.world_surface)

        # Just telling the guys to draw themselves
        for c in self.creatures:
            c.draw(self.world_surface)

        for item in self.items:
            item.draw(self.world_surface)

        # IMPORTANT, DONT MOVE IT: Debug stuff that must be printed BEFORE camera is drawn !!!!
        if is_debug_on:
            for c in self.creatures:
                pygame.draw.line(self.world_surface, (0,0,255), c.rect.center, c.rect.center + c.velocity)
            
            # Grid with tile separation
            for row_i in range(self.tile_map.map_size[0] - 1):
                pygame.draw.line(self.world_surface, (0,150,0), (row_i * self.tile_map.tile_size[0], 0),  (row_i * self.tile_map.tile_size[0], self.tile_map.map_size[1] * self.tile_map.tile_size[1]))
            for col_j in range(self.tile_map.map_size[1] - 1):
                pygame.draw.line(self.world_surface, (0,150,0), (0, col_j * self.tile_map.tile_size[1]),  (self.tile_map.map_size[0] * self.tile_map.tile_size[0], col_j * self.tile_map.tile_size[1]))
            
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


    # ==== Own Methods ====
    def spawn_creatures(self):
        self.creatures.clear()
        w, h = self.tile_map.map_size

        for _ in range(10):
            cluster_x = random.randint(200, int(w) - 200)
            cluster_y = random.randint(200, int(h) - 200)
            for _ in range(random.randint(5, 12)):
                x = random.randint(cluster_x - 40, cluster_x + 40)
                y = random.randint(cluster_y - 40, cluster_y + 40)

                creature_size = random.randint(10,20)
                c = PassiveCreature((x, y), size=creature_size, fear_radius=200)
                c.thrust = c.thrust - round((creature_size % 10) * 8)
                c.mass = c.mass + round((creature_size % 10) * 1.5)
                self.creatures.append(c)


        for _ in range(15):
            x = random.randint(100, int(w) - 100)
            y = random.randint(100, int(h) - 100)

            creature_size = random.randint(20,30)
            c = AggressiveCreature((x, y), size=creature_size, chase_radius=200)
            c.thrust = c.thrust - round((creature_size % 20) * 8)
            c.mass = c.mass + round((creature_size % 20) * 1.5)
            self.creatures.append(c)

    def check_return_point(self):
        pass

    def update_depth(self):
        pass

    def trigger_game_over(self):
        self.is_done = (True, "GAME_OVER")  #switch states
        self.exit()

    def exit_to_main_menu(self):
        self.is_done = (True, "START_SCREEN")
        self.exit()

    # ========= Private Methods =======