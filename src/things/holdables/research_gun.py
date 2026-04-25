import pygame
from .base_holdable import Holdable

class ResearchGun(Holdable):
    def __init__(self, research_database=None) -> None:
        self.name = "Research Gun"
        self.description = "Scanner used to analyze underwater creatures"
        self.color = (90, 200, 160)
        self.image_path = None  # Use placeholder
        self.scan_rate = 1.0
        self.range = 35  # doesnt really make the range smaller, need some help here...
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
        """Set the research database reference."""
        self.research_database = research_database
    
    def start_scan(self, target_creature):
        """Start scanning a creature."""
        self.current_target = target_creature
        self.scan_progress = 0.0
        self.scan_timer = 0.0
        self.scan_just_completed = False
    
    def stop_scan(self):
        """Stop scanning and reset progress."""
        self.current_target = None
        self.scan_progress = 0.0
        self.scan_timer = 0.0
        self.scan_just_completed = False
        self.completion_timer = 0.0
    
    def interrupt_scan(self):
        """Interrupt scan due to player damage or range - reset to 0."""
        self.scan_progress = 0.0
        self.scan_timer = 0.0
        self.scan_just_completed = False
    
    def update_scan(self, dt: float):
        """Update scanning progress."""
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
        """Get data for rendering scan effect."""
        if self.current_target is None or self.scan_progress <= 0:
            return None
        
        return {
            'target_pos': self.current_target.rect.center,
            'progress': self.scan_progress,
        }
        
    def shoot(self, pos: tuple[int, int]):
        pass