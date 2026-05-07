from world import TileMap, Camera, Interactable, Exit, Upgrades, Research, Shop
from things import Player
from ui import Button, PauseMenu, ResearchMenu, ShopMenu, UpgradeMenu
from .base_state import BaseState
from config import game as g_config
from config import player as p_config
from utils import ResearchDatabase, ResearchCatalog, ShopSystem, UpgradeSystem
import pygame


class HomebaseState(BaseState):
    def __init__(self, player: Player, research_database: ResearchDatabase | None = None) -> None:
        super().__init__()
        self.player = player
        self.research_database = research_database
        self.tile_map = TileMap(g_config["HOMEBASE_TILEMAP_PATH"])
        self.world_surface = pygame.Surface(self.tile_map.map_size, pygame.SRCALPHA)
        self.closest_interactable: Interactable | None = None

        self.world_rect = pygame.Rect(0, 0, self.tile_map.map_size[0], self.tile_map.map_size[1])
        self.camera = Camera(self.world_rect, 3)

        # Game systems used by the menus
        self.upgrade_system = UpgradeSystem(self.player)
        self.research_catalog = ResearchCatalog(self.research_database)
        self.shop_system = ShopSystem(self.player)

    def enter(self, data: dict = {}):
        g_config["DRAG"] = 2
        self.player.pos.xy = p_config["HOMEBASE_START_POS"]
        self.player.movement_axis.y = 0  # Horizontal movement only
        self.button = Button((g_config["SCREEN_SIZE"][0] - g_config["SCREEN_SIZE"][0] / 16, 20), (g_config["SCREEN_SIZE"][0] / 8, 40), (245, 96, 66), (209, 80, 54), text="Return", func=self._go_to_start)
        self.pause_menu = PauseMenu(self._resume_game, self._go_to_start)
        self.upgrade_menu = UpgradeMenu(self.upgrade_system.get_preview, self.upgrade_system.buy, self._close_upgrade_menu)
        self.research_menu = ResearchMenu(self.research_catalog, self._close_research_menu)
        self.shop_menu = ShopMenu(self.shop_system.get_listings, self.shop_system.get_total_value, self.shop_system.get_wallet, self.shop_system.sell_all, self._close_shop_menu)
        self._load_interactable_call_backs()
        self.player._current_anim = self.player.animations["walk"]

    def handle_event(self, e):
        # Esc closes overlays first
        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            if self.research_menu.is_open:
                self.research_menu.close()
            elif self.upgrade_menu.is_open:
                self.upgrade_menu.close()
            elif self.shop_menu.is_open:
                self.shop_menu.close()
            elif self.pause_menu.is_open:
                self.pause_menu.close()
            else:
                self.pause_menu.open()
            return

        # While upgrade menu is open only it handles events, works for other events below as well
        if self.upgrade_menu.is_open:
            self.upgrade_menu.handle_event(e)
            return


        if self.research_menu.is_open:
            self.research_menu.handle_event(e)
            return

        if self.shop_menu.is_open:
            self.shop_menu.handle_event(e)
            return

        if self.pause_menu.is_open:
            self.pause_menu.handle_event(e)
            return

        if e.type == pygame.MOUSEBUTTONDOWN and self.button.rect.collidepoint(pygame.mouse.get_pos()):
            self.button.call_back()
        elif e.type == pygame.KEYDOWN and e.key == pygame.K_e and self.closest_interactable:
            self.closest_interactable.interact()
        self.player.handle_event(e)

    def update(self, dt):
        # Freezes game while menus are active
        if self.research_menu.is_open:
            self.research_menu.update(dt)
            return

        if self.upgrade_menu.is_open:
            self.upgrade_menu.update(dt)
            return


        if self.shop_menu.is_open:
            self.shop_menu.update(dt)
            return

        if self.pause_menu.is_open:
            self.pause_menu.update(dt)
            return

        # Get rects of tiles surrounding player for calculating collisions with environment
        area_tiles = self.tile_map.get_tiles_at_area(self.player.rect.centerx, self.player.rect.centery, (4, 0))
        self.closest_interactable = self.tile_map.get_closest_interactable(self.player.rect.centerx, self.player.rect.centery, 30)
        if self.player.velocity.length() >= 5 or self.player._current_anim.finished is False:
            self.player.update_animation_homebase(dt)

        self.player.update(dt, self.world_rect, area_tiles)
        self.camera.update(dt, self.player.rect)

    def draw(self, screen, is_debug_on):
        self.world_surface.fill((80, 128, 173), self.camera.rect)
        self.tile_map.draw(self.world_surface, self.camera.rect)

        if self.closest_interactable is not None:
            self.closest_interactable.draw_prompt(self.world_surface, self.player.rect.center)

        self.player.draw(self.world_surface)
        if is_debug_on:
            # Grid with tile separation
            for row_i in range(self.tile_map.map_size[0] - 1):
                pygame.draw.line(self.world_surface, (0, 150, 0), (row_i * self.tile_map.tile_size[0], 0), (row_i * self.tile_map.tile_size[0], self.tile_map.map_size[1] * self.tile_map.tile_size[1]))
            for col_j in range(self.tile_map.map_size[1] - 1):
                pygame.draw.line(self.world_surface, (0, 150, 0), (0, col_j * self.tile_map.tile_size[1]), (self.tile_map.map_size[0] * self.tile_map.tile_size[0], col_j * self.tile_map.tile_size[1]))

            for interactable in self.tile_map.interactables:
                pygame.draw.rect(self.world_surface, (0, 0, 255), interactable.rect, 2)

            # Player hitbox
            pygame.draw.rect(self.world_surface, (255, 255, 0), self.player.rect, 2)

            # Player velocity (with direction)
            pygame.draw.line(self.world_surface, (255, 0, 0), self.player.rect.center, self.player.rect.center + self.player.velocity)
            pygame.draw.circle(self.world_surface, (0, 255, 0), self.player.pos, 1)

        self.camera.draw(self.world_surface, screen)

        if is_debug_on:
            from ui import get_font
            player_pos_text = get_font(36).render(f"Player_pos: {self.player.pos}", True, (255, 255, 255), (50, 50, 50))
            screen.blit(player_pos_text, (10, 5))
            self.button.draw(screen)

        self.research_menu.draw(screen)
        self.upgrade_menu.draw(screen)
        self.shop_menu.draw(screen)
        self.pause_menu.draw(screen)

    def exit(self):
        self.player.movement_axis.y = 1  # Return full movement

    def go_underwater(self):
        self.is_done = (True, "UNDERWATER")
        self.exit()

    def _go_to_start(self):
        self.is_done = (True, "START_SCREEN")
        self.exit()

    def _resume_game(self):
        self.pause_menu.close()

    def _open_upgrade_menu(self):
        self.upgrade_menu.open()

    def _close_upgrade_menu(self):
        self.upgrade_menu.close()

    def _open_research_menu(self):
        self.research_menu.open()

    def _close_research_menu(self):
        self.research_menu.close()

    def _open_shop_menu(self):
        self.shop_menu.open()

    def _close_shop_menu(self):
        self.shop_menu.close()

    # Interactable objects that load an external callback function
    def _load_interactable_call_backs(self) -> None:
        for interactable in self.tile_map.interactables:
            if isinstance(interactable, Exit):
                interactable.on_interact = self.go_underwater
            elif isinstance(interactable, Upgrades):
                interactable.on_interact = self._open_upgrade_menu
            elif isinstance(interactable, Research):
                interactable.on_interact = self._open_research_menu
            elif isinstance(interactable, Shop):
                interactable.on_interact = self._open_shop_menu
