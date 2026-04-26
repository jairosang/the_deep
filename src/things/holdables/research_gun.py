import pygame
from .base_holdable import Holdable

class ResearchGun(Holdable):
    continuous: bool = True

    def __init__(self, research_database=None) -> None:
        self.name = "Research Gun"
        self.description = "Scanner used to analyze underwater creatures"
        self.color = (90, 200, 160)
        self.image_path = None
        self.scan_rate = 1.0
        self.range = 35
        self.cooldown_s = 0.25
        self.is_available = False
        
        # Research gun specific
        self.research_database = research_database
        self.current_target = None  # Currently scanned creature
        self.scan_progress = 0.0  # Scan progress for current target (0-100%)
        self.scan_timer = 0.0  # Time spent on current target
        self.scan_just_completed = False  # Flag for completion animation
        self.completion_timer = 0.0  # Timer for completion animation (0.5 seconds)

        super().__init__()
    
    def set_research_database(self, research_database):
        # set the research database reference
        self.research_database = research_database
    
    def start_scan(self, target_creature):
        # start scanning a creature
        self.current_target = target_creature
        self.scan_progress = 0.0
        self.scan_timer = 0.0
        self.scan_just_completed = False
    
    def stop_scan(self):
        # stop scanning and reset progress
        self.current_target = None
        self.scan_progress = 0.0
        self.scan_timer = 0.0
        self.scan_just_completed = False
        self.completion_timer = 0.0
    
    def interrupt_scan(self):
        # interrupt scan due to player damage or being too far away, makes it reset to 0
        self.scan_progress = 0.0
        self.scan_timer = 0.0
        self.scan_just_completed = False
    
    def update_scan(self, dt: float):
        # update scanning progress
        if self.current_target is None or self.research_database is None:
            return
        
        # Get species and scan duration
        species = getattr(self.current_target, 'species', 'passive')
        is_alive = self.current_target.health > 0
        scan_duration = self.research_database.get_scan_duration(species)
        
        # Update scan timer
        self.scan_timer += dt
        
        # Calculate progress percentage
        raw_progress = (self.scan_timer / scan_duration) * 100.0
        self.scan_progress = min(100.0, raw_progress)
        
        # Cap progress based on creature state
        if not is_alive:
            self.scan_progress = min(self.scan_progress, 50.0)
        
        # Update database if scan is complete
        if self.scan_timer >= scan_duration and not self.scan_just_completed:
            creature_id = id(self.current_target)
            self.research_database.update_scan_progress(
                creature_id, species, is_alive, self.scan_progress
            )
            self.scan_just_completed = True
            self.completion_timer = 0.5  # Animation duration
        
        # Update completion timer
        if self.scan_just_completed:
            self.completion_timer -= dt
            if self.completion_timer <= 0:
                self.scan_just_completed = False
    
    def get_scan_visual_data(self):
        # get data for scan effect
        if self.current_target is None or self.scan_progress <= 0:
            return None
        
        return {
            'target_pos': self.current_target.rect.center,
            'progress': self.scan_progress,
        }
    
    def draw_things_on_screen(self, surface: pygame.Surface):
        # draw the green beam ray while scanning
        if self.current_target and self.scan_progress > 0:
            target = self.current_target
            player_center = self.player_center
            target_center = target.rect.center
            
            # draw green beam trapezoid from player gun to target
            beam_width_start = 8
            beam_width_end = 20
            
            # calculate direction
            dx = target_center[0] - player_center[0]
            dy = target_center[1] - player_center[1]
            distance = (dx**2 + dy**2)**0.5
            
            if distance > 0:
                # normalize direction
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
                
                # draw beam with transparency
                beam_surface = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
                pygame.draw.polygon(beam_surface, (0, 255, 100, 100), [p1, p2, p3, p4])
                surface.blit(beam_surface, (0, 0))
            
            # draw larger, more visible progress bar above creature
            bar_width = 60
            bar_height = 12
            bar_x = int(target.rect.centerx - bar_width/2)
            bar_y = int(target.rect.top - 25)
            
            # Background (dark)
            pygame.draw.rect(surface, (30, 30, 30), (bar_x, bar_y, bar_width, bar_height))
            
            # Progress (bright green)
            progress_width = int((self.scan_progress / 100.0) * bar_width)
            pygame.draw.rect(surface, (0, 255, 100), (bar_x, bar_y, progress_width, bar_height))
            
            # Border (bright green)
            pygame.draw.rect(surface, (0, 255, 150), (bar_x, bar_y, bar_width, bar_height), 2)
        
        # draw completion animation
        if self.scan_just_completed and self.current_target:
            target = self.current_target
            # flash green ring around creature
            ring_radius = int(40 + (0.5 - self.completion_timer) * 30)  # Expands
            alpha = int(255 * (self.completion_timer / 0.5))  # Fades out
            
            anim_surface = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
            pygame.draw.circle(anim_surface, (0, 255, 100, alpha), target.rect.center, ring_radius, 3)
            surface.blit(anim_surface, (0, 0))

    def shoot(self, pos: tuple[int, int]) -> bool:
        return False