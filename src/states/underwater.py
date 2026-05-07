from things import Player, Creature, Fish, BlueFish, FishDart, FishBig, Anglerfish
from things import Weapon, ResearchGun, Harpoon, Ray
from world import TileMap, Camera, Interactable, Exit, OxygenTank
from ui import Button, InventoryMenu, PauseMenu, HeldInventory, PlayerHud
from .base_state import BaseState
from config import game as g_config
from config import player as p_config
import utils as phy
from utils.research_database import ResearchDatabase
import pygame
import random


class UnderwaterState(BaseState):
    def __init__(self, player: Player, research_database: ResearchDatabase | None = None) -> None:
        super().__init__()
        self.player = player
        self.creatures: list[Creature] = []
        self.items = []
        self.oxygen_tanks: list[OxygenTank] = []
        self.tile_map = TileMap(g_config["UNDERWATER_TILEMAP_PATH"])
        self.world_surface = pygame.Surface(self.tile_map.map_size, pygame.SRCALPHA)
        self.closest_interactable: Interactable | None = None
        
        self.world_rect = pygame.Rect(0, 0, self.tile_map.map_size[0], self.tile_map.map_size[1])
        self.camera = Camera(self.world_rect, 2)
        self._load_interactable_call_backs()
        
        # Store research database reference
        self.research_database = research_database 
        
        # Create inventory with research database reference
        research_gun = ResearchGun(self.research_database)
        self.held_inventory = HeldInventory([Weapon(), research_gun])
        self.player_hud = PlayerHud(self.tile_map.map_size[1])

        # Store reference to research gun for scanning
        self.research_gun = research_gun
        
        # Research gun input tracking
        self.left_mouse_held = False
        self.f_key_held = False
        
        # Research gun state tracking
        self.player_last_health = self.player.health
        self.previous_holdable = None

    #==== Abstract Methods from base class =====
    def enter(self, data: dict = {}):
        g_config["DRAG"] = 0.9
        self.player.pos.xy = p_config["UNDERWATER_START_POS"]
        self.player.oxygen = self.player.max_oxygen
        self.player.health = self.player.max_health
        self.button = Button((g_config["SCREEN_SIZE"][0] - g_config["SCREEN_SIZE"][0]/16,20),(g_config["SCREEN_SIZE"][0]/8,40), (245, 96, 66), (209, 80, 54), text="Return", func=self._go_to_start)
        self.player.set_holdable(self.held_inventory.selected_holdable)
        self._apply_player_upgrades_to_holdables()
        self.player.movement_axis.update(1,1)
        # Inventory menu you can open it with E key
        self.inventory_menu = InventoryMenu(self.player.buffer_inventory)
        # Pause popup with resume and title options
        self.pause_menu = PauseMenu(self._resume_game, self._go_to_start)
        self._spawn_creatures()
        self._spawn_oxygen_tanks()

    def handle_event(self, e: pygame.event.Event):
        # Escape toggles pause
        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            if self.pause_menu.is_open:
                self.pause_menu.close()
            else:
                if self.inventory_menu.is_open:
                    self.inventory_menu.close()
                self.pause_menu.open()
            return

        # While paused only the pause menu handles events
        if self.pause_menu.is_open:
            self.pause_menu.handle_event(e)
            return

        prev_index = self.held_inventory.selected_index
        self.held_inventory.handle_event(e)
        if self.held_inventory.selected_index != prev_index:
            self.player.set_holdable(self.held_inventory.selected_holdable)

        if e.type == pygame.MOUSEBUTTONDOWN and self.button.rect.collidepoint(pygame.mouse.get_pos()):
            self.button.call_back()
        elif e.type == pygame.KEYDOWN and e.key == pygame.K_e:
            # E priority: close menu > interact > open menu
            if self.inventory_menu.is_open:
                self.inventory_menu.close()
            elif self.closest_interactable:
                self.closest_interactable.interact()
            else:
                self.inventory_menu.open()

        # Forward other events to the menu so it can hook the material later
        self.inventory_menu.handle_event(e)

        self.player.handle_event(e)

    def update(self, dt):
        # Freeze game during the pause being active
        if self.pause_menu.is_open:
            self.pause_menu.update(dt)
            return

        # Get rects of tiles surrounding player for calculating collisions with environment 
        player_area_tiles = self.tile_map.get_tiles_at_area(self.player.rect.centerx, self.player.rect.centery, (7,7))
        self.player.update(dt, self.world_rect, player_area_tiles)
        self.player.update_animation_underwater(dt)
        self.player_hud.update(self.player, dt)

        if self.player.current_holdable is not None:
            self.player.current_holdable._last_mouse_pos = self._screen_to_world_pos(pygame.mouse.get_pos())
        self.closest_interactable = self.tile_map.get_closest_interactable(self.player.rect.centerx, self.player.rect.centery, 100)
        
        # Check for closest oxygen tank
        for tank in self.oxygen_tanks:
            dist_to_tank = ((tank.rect.centerx - self.player.rect.centerx)**2 + (tank.rect.centery - self.player.rect.centery)**2)**0.5
            if self.closest_interactable is None or dist_to_tank < self._get_interactable_distance(self.closest_interactable):
                if dist_to_tank < 100:
                    self.closest_interactable = tank
        self.camera.update(dt, self.player.rect)
        player_pos = pygame.math.Vector2(self.player.rect.center)
        for c in self.creatures:
            area_tiles = self.tile_map.get_tiles_at_area(c.rect.centerx, c.rect.centery, (7,7))
            c.update(dt, self.world_rect, area_tiles, player_pos)

        if self.player.oxygen <= 0 or self.player.health <= 0:
            self._trigger_game_over()

        dropped_items = phy.resolve_player_creature_collisions(self.player, self.creatures, player_area_tiles)
        self.items.extend(dropped_items)

        phy.resolve_player_item_pickups(self.player, self.items, dt)
        self._update_shootables(dt)


    def draw(self, screen: pygame.Surface, is_debug_on):
        # Wiping the world surface, but only the camera area! This really improved the performance.
        self.world_surface.fill((80, 128, 173), self.camera.rect)
        self.tile_map.draw(self.world_surface, self.camera.rect, has_shading= True)
        if self.closest_interactable is not None:
            self.closest_interactable.draw_prompt(self.world_surface, self.player.rect.center)
        
        # Collect all drawable entities with their Y positions for depth sorting
        drawable_entities = []
        
        # Add player
        drawable_entities.append(('player', self.player, self.player.rect.centery))
        
        # Add oxygen tanks
        for tank in self.oxygen_tanks:
            drawable_entities.append(('tank', tank, tank.rect.centery))
        
        # Add creatures
        for c in self.creatures:
            drawable_entities.append(('creature', c, c.rect.centery))
        
        # Add items
        for item in self.items:
            drawable_entities.append(('item', item, item.rect.centery))
        
        # Sort by Y position (smaller Y = further away, drawn first)
        drawable_entities.sort(key=lambda x: x[2])
        
        for holdable in self.held_inventory.holdables:
            holdable.draw_things_on_screen(self.world_surface)     # Stuff like the research gun ray area nd stuff

        # Draw all entities in sorted order
        for entity_type, entity, _ in drawable_entities:
            entity.draw(self.world_surface)

        # IMPORTANT, DONT MOVE IT: Debug stuff that must be printed BEFORE camera is drawn !!!!
        if is_debug_on:
            for c in self.creatures:
                pygame.draw.line(self.world_surface, (0,0,255), c.rect.center, c.rect.center + c.velocity)
                pygame.draw.rect(self.world_surface, (255, 0, 255), c.rect, 2)
            for holdable in self.held_inventory.holdables:
                for shootable in holdable.get_shootables():
                    if not isinstance(shootable, Ray):
                        pygame.draw.line(self.world_surface, (0,0,255), shootable.rect.center, shootable.rect.center + shootable.velocity)
                        pygame.draw.rect(self.world_surface, (255, 0, 255), shootable.rect, 2)
            
            # Grid with tile separation
            for row_i in range(self.tile_map.map_size[0] - 1):
                pygame.draw.line(self.world_surface, (0,150,0), (row_i * self.tile_map.tile_size[0], 0),  (row_i * self.tile_map.tile_size[0], self.tile_map.map_size[1] * self.tile_map.tile_size[1]))
            for col_j in range(self.tile_map.map_size[1] - 1):
                pygame.draw.line(self.world_surface, (0,150,0), (0, col_j * self.tile_map.tile_size[1]),  (self.tile_map.map_size[0] * self.tile_map.tile_size[0], col_j * self.tile_map.tile_size[1]))
            for rect_row in self.tile_map.mid_layer.collisions_grid:
                for rect in rect_row:
                    if rect:
                        pygame.draw.rect(self.world_surface, (255,0,0), rect, 2)
                    
            # Player velocity (with direction)
            pygame.draw.line(self.world_surface, (255,0,0), self.player.rect.center, self.player.rect.center + self.player.velocity)
            pygame.draw.circle(self.world_surface, (0,255,0), self.player.pos, 1)
            pygame.draw.rect(self.world_surface, (255, 255, 0), self.player.rect, 2)
        
        self.camera.draw(self.world_surface, screen)

        self.player_hud.draw(screen, self.player, self.world_rect.height)
        
        self.held_inventory.draw(screen)

        # IMPORTANT, DONT MOVE IT: Debug stuff that must be printed AFTER camera is drawn !!!!
        if is_debug_on:
            from ui import get_font
            player_pos_text = get_font(36).render(f"Player_pos: {self.player.pos}", True, (255,255,255), (50,50,50))
            screen.blit(player_pos_text, (10, 5))
            self.button.draw(screen)

        # Inventory menu drawn last so it stays on top of everything
        self.inventory_menu.draw(screen)
        self.pause_menu.draw(screen)

    def exit(self):
        self.player.revert()
        self.player.movement_axis[1] = 0
        self._despawn_creatures()


    # ==== Own Methods ====
    def _spawn_creatures(self):
        self.creatures.clear()

        w, h = self.tile_map.map_size
        zone_height = h // 3

        passive_creatures_by_zone = [[Fish], [Fish, BlueFish], [BlueFish],]

        aggressive_creatures_by_zone = [[FishDart],[FishBig],[Anglerfish],]

        for zone in range(3):
            zone_top = 100 + zone * zone_height
            zone_bottom = min(int(h) - 100, (zone + 1) * zone_height)

            for i in range(4):
                cluster_x = random.randint(200, int(w) - 200)
                cluster_y = random.randint(zone_top, zone_bottom)

                for _ in range(random.randint(5, 8)):
                    x = random.randint(cluster_x - 40, cluster_x + 40)
                    y = random.randint(cluster_y - 40, cluster_y + 40)

                    creature_class = random.choice(passive_creatures_by_zone[zone])

                    if creature_class is BlueFish:
                        creature_size = random.randint(22, 30)
                    else:
                        creature_size = random.randint(10, 20)

                    creature = creature_class((x, y), size=creature_size)

                    creature.thrust = creature.thrust - round(
                        (creature_size % 10) * 8
                    )
                    creature.mass = creature.mass + round(
                        (creature_size % 10) * 1.5
                    )

                    self.creatures.append(creature)

            for i in range(5):
                x = random.randint(100, int(w) - 100)
                y = random.randint(zone_top, zone_bottom)

                creature_class = random.choice(aggressive_creatures_by_zone[zone])
                creature_size = random.randint(20, 30)

                creature = creature_class((x, y), size=creature_size)

                creature.thrust = creature.thrust - round(
                    (creature_size % 20) * 8
                )
                creature.mass = creature.mass + round(
                    (creature_size % 20) * 1.5
                )

                self.creatures.append(creature)

    def _despawn_creatures(self):
        self.creatures.clear()

    def _update_shootables(self, dt: float) -> None:
        for holdable in self.held_inventory.holdables:
            # The return value is for the projectiles, this is such bad design and will crash if return something we shouldn't but we dont have tiiiiiiiiiiime
            dropped_items, spent_shootables = holdable.update_shootables(dt, self.creatures, self.world_rect, self.tile_map.get_tiles_at_area)
            holdable.remove_shootables(spent_shootables)
            self.items.extend(dropped_items)

    def _check_return_point(self):
        pass

    def _screen_to_world_pos(self, screen_pos: tuple[int, int]) -> tuple[int, int]:
        zoom_x = g_config["SCREEN_SIZE"][0] / self.camera.rect.width
        zoom_y = g_config["SCREEN_SIZE"][1] / self.camera.rect.height
        world_x = self.camera.rect.left + (screen_pos[0] / zoom_x)
        world_y = self.camera.rect.top + (screen_pos[1] / zoom_y)
        return (int(world_x), int(world_y))

    def update_depth(self):
        pass

    def _trigger_game_over(self):
        self.is_done = (True, "GAME_OVER")  #switch states
        self.exit()

    def _go_to_start(self):
        self.is_done = (True, "START_SCREEN")
        self.exit()

    def _go_to_homebase(self):
        self.is_done = (True, "HOMEBASE")
        self.exit()

    def _resume_game(self):
        self.pause_menu.close()

    # Interactable objects that load an external callback function
    def _load_interactable_call_backs(self) -> None:
        for interactable in self.tile_map.interactables:
            if isinstance(interactable, Exit):
                interactable.on_interact = self._go_to_homebase
                interactable.prompt_text = "Press E to go back to Homebase"

    def _spawn_oxygen_tanks(self) -> None:
        """Spawn oxygen tanks randomly across the underwater map, avoiding walls."""
        self.oxygen_tanks.clear()
        w, h = self.tile_map.map_size
        num_tanks = 8  # Number of oxygen tanks to spawn
        spawned = 0
        max_attempts = 500  # Prevent infinite loops
        attempts = 0
        
        while spawned < num_tanks and attempts < max_attempts:
            attempts += 1
            x = random.randint(100, int(w) - 100)
            y = random.randint(100, int(h) - 100)
            
            # Check if position is not solid (not a wall)
            if not self.tile_map.is_tile_solid(x, y):
                tank = OxygenTank(x, y, oxygen_refill=30.0)
                tank.on_interact = lambda t=tank: self._refill_oxygen(t)
                self.oxygen_tanks.append(tank)
                spawned += 1
    
    def _refill_oxygen(self, tank: OxygenTank) -> None:
        # refill player oxygen from a tank 
        self.player.oxygen = min(self.player.oxygen + tank.oxygen_refill, self.player.max_oxygen)
        self.oxygen_tanks.remove(tank)

    def _get_interactable_distance(self, interactable: Interactable) -> float:
        # calculate distance from player to an interactable
        return ((interactable.rect.centerx - self.player.rect.centerx)**2 + 
                (interactable.rect.centery - self.player.rect.centery)**2)**0.5

    def _apply_player_upgrades_to_holdables(self) -> None:
        weapon_damage = getattr(self.player, "weapon_upgrade_damage", 10)
        scanner_rate = getattr(self.player, "scanner_upgrade_rate", 1.0)

        for holdable in self.held_inventory.holdables:
            if isinstance(holdable, Weapon):
                holdable.damage = weapon_damage
            elif isinstance(holdable, ResearchGun):
                holdable.scan_rate = scanner_rate