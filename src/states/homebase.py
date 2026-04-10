from src.states.base_state import BaseState
from src.entities.player import Player
from config import game as g_config
from config import player as p_config
from src.utils.tile_map import TileMap
from src.utils.camera import Camera
from src.ui.components.button import Button
import pygame

class HomebaseState(BaseState):
    def __init__(self, player: Player) -> None:
        super().__init__()
        self.player = player
        self.tile_map = TileMap(g_config["HOMEBASE_TILEMAP_PATH"])
        self.world_surface = pygame.Surface(self.tile_map.map_size, pygame.SRCALPHA)

        self.world_rect = pygame.Rect(0, 0, self.tile_map.map_size[0], self.tile_map.map_size[1])
        self.camera = Camera(self.world_rect,3)


    def enter(self, data: dict = {}):
        self.player.pos.xy = p_config["HOMEBASE_START_POS"]
        self.player.movement_axis.y = 0  # Horizontal movement only
        self.button = Button((g_config["SCREEN_SIZE"][0] - g_config["SCREEN_SIZE"][0]/16,20),(g_config["SCREEN_SIZE"][0]/8,40), (245, 96, 66), (209, 80, 54), text="Return", func=self.exit)


    def handle_event(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN and self.button.rect.collidepoint(pygame.mouse.get_pos()):
            self.button.call_back()

    def handle_inputs(self, keys: pygame.key.ScancodeWrapper, mouse_pos: tuple[int, int]):
        pass
        
    def update(self, dt):
        # Get rects of tiles surrounding player for calculating collisions with environment 
        area_tiles = self.tile_map.get_tiles_at_area(self.player.rect.centerx, self.player.rect.centery, (7,7))
        self.player.update(dt, self.world_rect, area_tiles)
        self.camera.update(dt, self.player.rect)

    def draw(self, screen, is_debug_on):
        self.world_surface.fill((80, 128, 173), self.camera.rect)
        self.tile_map.draw(self.world_surface, self.camera.rect)
        self.player.draw(self.world_surface)

        self.camera.draw(self.world_surface, screen)
        self.button.draw(screen)

    def exit(self):
        self.player.movement_axis.y = 1  # Return full movement
        self.is_done = (True, "START_SCREEN")