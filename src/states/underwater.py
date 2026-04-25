from things import Player, Creature, PassiveCreature, AggressiveCreature
from world import TileMap, Camera, Interactable, Exit
from things import Weapon, ResearchGun, Harpoon
from ui import Button, HeldInventory
from .base_state import BaseState
from config import game as g_config
from config import player as p_config
from utils.research_database import ResearchDatabase
import utils as phy
import pygame
import random


class UnderwaterState(BaseState):
    def __init__(self, player: Player) -> None:
        super().__init__()
        self.player = player
        self.creatures: list[Creature] = []
        self.items = []
        self.tile_map = TileMap(g_config["UNDERWATER_TILEMAP_PATH"])
        self.world_surface = pygame.Surface(self.tile_map.map_size, pygame.SRCALPHA)
        self.closest_interactable: Interactable | None = None
        
        self.world_rect = pygame.Rect(0, 0, self.tile_map.map_size[0], self.tile_map.map_size[1])
        self.camera = Camera(self.world_rect)
        self._load_interactable_call_backs()
        
        # Initialize research database
        self.research_database = ResearchDatabase()
        
        # Create inventory with research database reference
        research_gun = ResearchGun(self.research_database)
        self.held_inventory = HeldInventory([Weapon(), research_gun, Harpoon()])
        
        # Track player's last health for damage detection
        self.player_last_health = self.player.health
        
        # Track previous holdable to detect weapon switches
        self.previous_holdable = self.held_inventory.selected_holdable
        
        # Store reference to research gun for scanning
        self.research_gun = research_gun
        
        # Track if left mouse button is held for scanning
        self.left_mouse_held = False
        
        # Track if F key is held for scanning
        self.f_key_held = False

    #==== Abstract Methods from base class =====
    def enter(self, data: dict = {}):
        self.player.pos.xy = p_config["UNDERWATER_START_POS"]
        self.button = Button((g_config["SCREEN_SIZE"][0] - g_config["SCREEN_SIZE"][0]/16,20),(g_config["SCREEN_SIZE"][0]/8,40), (245, 96, 66), (209, 80, 54), text="Return", func=self._go_to_start)
        self.spawn_creatures()

    def handle_event(self, e: pygame.event.Event):
        prev_index = self.held_inventory.selected_index
        self.held_inventory.handle_event(e)
        if self.held_inventory.selected_index != prev_index:
            self.player.set_holdable(self.held_inventory.selected_holdable)

        if e.type == pygame.MOUSEBUTTONDOWN and self.button.rect.collidepoint(pygame.mouse.get_pos()):
            self.button.call_back()
        elif e.type == pygame.KEYDOWN and e.key == pygame.K_e and self.closest_interactable:
            self.closest_interactable.interact()
        # ===== RESEARCH GUN ACTIVATION =====
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:  # Left click held
            self.left_mouse_held = True
        elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:  # Left click released
            self.left_mouse_held = False
            # Stop scanning when mouse button released
            if isinstance(self.held_inventory.selected_holdable, ResearchGun):
                self.research_gun.stop_scan()
        elif e.type == pygame.KEYDOWN and e.key == pygame.K_f:  # F key held
            self.f_key_held = True
        elif e.type == pygame.KEYUP and e.key == pygame.K_f:  # F key released
            self.f_key_held = False
            # Stop scanning when F key released
            if isinstance(self.held_inventory.selected_holdable, ResearchGun):
                self.research_gun.stop_scan()

        if e.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
            world_mouse_pos = self._screen_to_world_pos(e.pos)
            self.player.handle_event(e, world_mouse_pos)
        else:
            self.player.handle_event(e)

    def update(self, dt):
        # Get rects of tiles surrounding player for calculating collisions with environment 
        player_area_tiles = self.tile_map.get_tiles_at_area(self.player.rect.centerx, self.player.rect.centery, (7,7))
        self.player.update(dt, self.world_rect, player_area_tiles)
        player_area_tiles = self.tile_map.get_tiles_at_area(self.player.rect.centerx, self.player.rect.centery, (7,7))
        self.closest_interactable = self.tile_map.get_closest_interactable(self.player.rect.centerx, self.player.rect.centery, 100)
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
        
        # ===== RESEARCH GUN SCANNING LOGIC =====
        # Check if player took damage - interrupt scanning
        if self.player.health < self.player_last_health:
            self.research_gun.interrupt_scan()
        self.player_last_health = self.player.health
        
        # Check if player switched weapons - stop scanning
        if self.held_inventory.selected_holdable != self.previous_holdable:
            self.research_gun.stop_scan()
        self.previous_holdable = self.held_inventory.selected_holdable
        
        # ===== HOLD-TO-RESEARCH: Only scan if mouse button is held and gun equipped
        if (self.left_mouse_held or self.f_key_held) and isinstance(self.held_inventory.selected_holdable, ResearchGun):
            mouse_world_pos = self._screen_to_world_pos(pygame.mouse.get_pos())
            
            # Find closest creature to mouse within range
            target_creature = None
            min_distance = self.research_gun.range
            
            for creature in self.creatures:
                dist_to_creature = ((creature.rect.centerx - mouse_world_pos[0])**2 + 
                                   (creature.rect.centery - mouse_world_pos[1])**2)**0.5
                if dist_to_creature < min_distance:
                    target_creature = creature
                    min_distance = dist_to_creature
            
            # Start or continue scanning
            if target_creature:
                if self.research_gun.current_target != target_creature:
                    self.research_gun.start_scan(target_creature)
                self.research_gun.update_scan(dt)
            else:
                # No creature in range - stop scanning
                self.research_gun.stop_scan()
        else:
            # Not holding mouse button or gun not equipped - stop scanning
            if self.research_gun.current_target:
                self.research_gun.stop_scan()


    def draw(self, screen: pygame.Surface, is_debug_on):
        # Wiping the world surface, but only the camera area! This really improved the performance.
        self.world_surface.fill((80, 128, 173), self.camera.rect)
        self.tile_map.draw(self.world_surface, self.camera.rect)
        if self.closest_interactable is not None:
            self.closest_interactable.draw_prompt(self.world_surface)
        self.player.draw(self.world_surface)

        # Just telling the guys to draw themselves
        for c in self.creatures:
            c.draw(self.world_surface)

        for item in self.items:
            item.draw(self.world_surface)

        # ===== DRAW RESEARCH SCANNING EFFECTS =====
        if self.research_gun.current_target and self.research_gun.scan_progress > 0:
            target = self.research_gun.current_target
            player_center = self.player.rect.center
            target_center = target.rect.center
            
            # Draw green beam trapezoid from player gun to target
            beam_width_start = 8
            beam_width_end = 20
            
            # Calculate direction
            dx = target_center[0] - player_center[0]
            dy = target_center[1] - player_center[1]
            distance = (dx**2 + dy**2)**0.5
            
            if distance > 0:
                # Normalize direction
                dx_norm = dx / distance
                dy_norm = dy / distance
                
                # Perpendicular direction for trapezoid width
                perp_x = -dy_norm
                perp_y = dx_norm
                
                # Calculate trapezoid corners
                p1 = (int(player_center[0] + perp_x * beam_width_start/2), 
                      int(player_center[1] + perp_y * beam_width_start/2))
                p2 = (int(player_center[0] - perp_x * beam_width_start/2), 
                      int(player_center[1] - perp_y * beam_width_start/2))
                p3 = (int(target_center[0] - perp_x * beam_width_end/2), 
                      int(target_center[1] - perp_y * beam_width_end/2))
                p4 = (int(target_center[0] + perp_x * beam_width_end/2), 
                      int(target_center[1] + perp_y * beam_width_end/2))
                
                # Draw beam with transparency
                beam_surface = pygame.Surface((self.world_surface.get_width(), self.world_surface.get_height()), pygame.SRCALPHA)
                pygame.draw.polygon(beam_surface, (0, 255, 100, 100), [p1, p2, p3, p4])
                self.world_surface.blit(beam_surface, (0, 0))
            
            # Draw larger, more visible progress bar above creature
            bar_width = 60
            bar_height = 12
            bar_x = int(target.rect.centerx - bar_width/2)
            bar_y = int(target.rect.top - 25)
            
            # Background (dark)
            pygame.draw.rect(self.world_surface, (30, 30, 30), (bar_x, bar_y, bar_width, bar_height))
            
            # Progress (bright green)
            progress_width = int((self.research_gun.scan_progress / 100.0) * bar_width)
            pygame.draw.rect(self.world_surface, (0, 255, 100), (bar_x, bar_y, progress_width, bar_height))
            
            # Border (bright green)
            pygame.draw.rect(self.world_surface, (0, 255, 150), (bar_x, bar_y, bar_width, bar_height), 2)
        
        # ===== DRAW COMPLETION ANIMATION =====
        if self.research_gun.scan_just_completed and self.research_gun.current_target:
            target = self.research_gun.current_target
            # Flash green ring around creature
            ring_radius = int(40 + (0.5 - self.research_gun.completion_timer) * 30)  # Expands
            alpha = int(255 * (self.research_gun.completion_timer / 0.5))  # Fades out
            
            anim_surface = pygame.Surface((self.world_surface.get_width(), self.world_surface.get_height()), pygame.SRCALPHA)
            pygame.draw.circle(anim_surface, (0, 255, 100, alpha), target.rect.center, ring_radius, 3)
            self.world_surface.blit(anim_surface, (0, 0))

        # IMPORTANT, DONT MOVE IT: Debug stuff that must be printed BEFORE camera is drawn !!!!
        if is_debug_on:
            for c in self.creatures:
                pygame.draw.line(self.world_surface, (0,0,255), c.rect.center, c.rect.center + c.velocity)
                pygame.draw.rect(self.world_surface, (255, 0, 255), c.rect, 2)
            
            # Grid with tile separation
            for row_i in range(self.tile_map.map_size[0] - 1):
                pygame.draw.line(self.world_surface, (0,150,0), (row_i * self.tile_map.tile_size[0], 0),  (row_i * self.tile_map.tile_size[0], self.tile_map.map_size[1] * self.tile_map.tile_size[1]))
            for col_j in range(self.tile_map.map_size[1] - 1):
                pygame.draw.line(self.world_surface, (0,150,0), (0, col_j * self.tile_map.tile_size[1]),  (self.tile_map.map_size[0] * self.tile_map.tile_size[0], col_j * self.tile_map.tile_size[1]))
            
            # Player velocity (with direction)
            pygame.draw.line(self.world_surface, (255,0,0), self.player.rect.center, self.player.rect.center + self.player.velocity)
            pygame.draw.circle(self.world_surface, (0,255,0), self.player.pos, 1)
            pygame.draw.rect(self.world_surface, (255, 255, 0), self.player.rect, 2)
        
        self.camera.draw(self.world_surface, screen)

        # This thing is a temporary thing for displaying the oxygen thing in the bottom left corner of the screen thing
        oxygen_text = pygame.font.Font(None, 36).render(f"O2: {self.player.oxygen:.0f}", True, (255, 255, 255))
        health_text = pygame.font.Font(None, 36).render(f"Health: {self.player.health:.0f}", True, (255, 255, 255))
        screen.blit(oxygen_text, (10, g_config["SCREEN_SIZE"][1] - 70))
        screen.blit(health_text, (10, g_config["SCREEN_SIZE"][1] - 40))
        self.held_inventory.draw(screen)

        # IMPORTANT, DONT MOVE IT: Debug stuff that must be printed AFTER camera is drawn !!!!
        if is_debug_on:
            player_pos_text = pygame.font.Font(None, 36).render(f"Player_pos: {self.player.pos}", True, (255,255,255), (50,50,50))
            screen.blit(player_pos_text, (10, 5))
            self.button.draw(screen)

    def exit(self):
        self.player.revert()
        self.player.movement_axis[1] = 0


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


        for i in range(15):
            x = random.randint(100, int(w) - 100)
            y = random.randint(100, int(h) - 100)

            creature_size = random.randint(20,30)

            sprite = "fish-dart" if i % 2 == 0 else "fish-big"
            c = AggressiveCreature((x, y), size=creature_size, chase_radius=200, sprite = sprite)
            c.thrust = c.thrust - round((creature_size % 20) * 8)
            c.mass = c.mass + round((creature_size % 20) * 1.5)
            self.creatures.append(c)

    def check_return_point(self):
        pass

    def _screen_to_world_pos(self, screen_pos: tuple[int, int]) -> tuple[int, int]:
        zoom_x = g_config["SCREEN_SIZE"][0] / self.camera.rect.width
        zoom_y = g_config["SCREEN_SIZE"][1] / self.camera.rect.height
        world_x = self.camera.rect.left + (screen_pos[0] / zoom_x)
        world_y = self.camera.rect.top + (screen_pos[1] / zoom_y)
        return (int(world_x), int(world_y))

    def update_depth(self):
        pass

    def _activate_research_scan(self):
        """Activate scanning when player clicks/presses F near a creature."""
        mouse_world_pos = self._screen_to_world_pos(pygame.mouse.get_pos())
        
        # Find closest creature to mouse position within range
        target_creature = None
        min_distance = self.research_gun.range
        
        for creature in self.creatures:
            dist_to_creature = ((creature.rect.centerx - mouse_world_pos[0])**2 + 
                               (creature.rect.centery - mouse_world_pos[1])**2)**0.5
            if dist_to_creature < min_distance:
                target_creature = creature
                min_distance = dist_to_creature
        
        # Start scanning if found a creature in range
        if target_creature:
            self.research_gun.start_scan(target_creature)

    def _trigger_game_over(self):
        self.is_done = (True, "GAME_OVER")  #switch states
        self.exit()

    def _go_to_start(self):
        self.is_done = (True, "START_SCREEN")
        self.exit()

    def _go_to_homebase(self):
        self.is_done = (True, "HOMEBASE")
        self.exit()

    # Interactable objects that load an external callback function
    def _load_interactable_call_backs(self) -> None:
        for interactable in self.tile_map.interactables:
            if isinstance(interactable, Exit):
                interactable.on_interact = self._go_to_homebase
                interactable.prompt_text = "Press E to go back to Homebase"