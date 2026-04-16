from src.states.base_state import BaseState
from src.entities.player import Player
from config import game as g_config
from config import player as p_config
from src.utils.tile_map import TileMap
from src.utils.camera import Camera
from src.utils.interactables import Interactable, Exit, Upgrades, Research
from src.ui.components.button import Button
import pygame

class HomebaseState(BaseState):
    def __init__(self, player: Player) -> None:
        super().__init__()
        self.player = player
        self.tile_map = TileMap(g_config["HOMEBASE_TILEMAP_PATH"])
        self.world_surface = pygame.Surface(self.tile_map.map_size, pygame.SRCALPHA)
        self.closest_interactable: Interactable | None = None

        self.world_rect = pygame.Rect(0, 0, self.tile_map.map_size[0], self.tile_map.map_size[1])
        self.camera = Camera(self.world_rect,3)


    def enter(self, data: dict = {}):
        self.player.pos.xy = p_config["HOMEBASE_START_POS"]
        self.player.movement_axis.y = 0  # Horizontal movement only
        self.button = Button((g_config["SCREEN_SIZE"][0] - g_config["SCREEN_SIZE"][0]/16,20),(g_config["SCREEN_SIZE"][0]/8,40), (245, 96, 66), (209, 80, 54), text="Return", func=self._go_to_start)
        self._load_interactable_call_backs()


    def handle_event(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN and self.button.rect.collidepoint(pygame.mouse.get_pos()):
            self.button.call_back()
        elif e.type == pygame.KEYDOWN and e.key == pygame.K_e and self.closest_interactable:
            self.closest_interactable.interact()

    def handle_inputs(self, keys: pygame.key.ScancodeWrapper, mouse_pos: tuple[int, int]):
        self.player.handle_inputs(keys)
        
    def update(self, dt):
        # Get rects of tiles surrounding player for calculating collisions with environment 
        area_tiles = self.tile_map.get_tiles_at_area(self.player.rect.centerx, self.player.rect.centery, (4,0))
        self.closest_interactable = self.tile_map.get_closest_interactable(self.player.rect.centerx, self.player.rect.centery, 30)
        
        self.player.update(dt, self.world_rect, area_tiles)
        self.camera.update(dt, self.player.rect)

    def draw(self, screen, is_debug_on):
        self.world_surface.fill((80, 128, 173), self.camera.rect)
        self.tile_map.draw(self.world_surface, self.camera.rect)

        if self.closest_interactable is not None:
            self.closest_interactable.draw_prompt(self.world_surface)

        self.player.draw(self.world_surface)
        if is_debug_on:
            # Grid with tile separation
            for row_i in range(self.tile_map.map_size[0] - 1):
                pygame.draw.line(self.world_surface, (0,150,0), (row_i * self.tile_map.tile_size[0], 0),  (row_i * self.tile_map.tile_size[0], self.tile_map.map_size[1] * self.tile_map.tile_size[1]))
            for col_j in range(self.tile_map.map_size[1] - 1):
                pygame.draw.line(self.world_surface, (0,150,0), (0, col_j * self.tile_map.tile_size[1]),  (self.tile_map.map_size[0] * self.tile_map.tile_size[0], col_j * self.tile_map.tile_size[1]))
            
            for interactable in self.tile_map.interactables:
                pygame.draw.rect(self.world_surface, (0,0,255), interactable.rect, 2)

            # Player velocity (with direction)
            pygame.draw.line(self.world_surface, (255,0,0), self.player.rect.center, self.player.rect.center + self.player.velocity)
            pygame.draw.circle(self.world_surface, (0,255,0), self.player.pos, 1)

        self.camera.draw(self.world_surface, screen)
        self.button.draw(screen)

        if is_debug_on:
            player_pos_text = pygame.font.Font(None, 36).render(f"Player_pos: {self.player.pos}", True, (255,255,255), (50,50,50))
            screen.blit(player_pos_text, (10, 5))

    def exit(self):
        self.player.movement_axis.y = 1  # Return full movement

    def go_underwater(self):
        self.is_done = (True, "UNDERWATER")
        self.exit()

    def _go_to_start(self):
        self.is_done = (True, "START_SCREEN")
        self.exit()

    # Interactable objects that load an external callback function
    def _load_interactable_call_backs(self) -> None:
        for interactable in self.tile_map.interactables:
            if isinstance(interactable, Exit):
                interactable.on_interact = self.go_underwater
                interactable.prompt_text = "Press E to go underwater ~"