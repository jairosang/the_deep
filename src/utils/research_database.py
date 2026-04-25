

class ResearchDatabase:
    # Stores and manages research progress for all creatures.
    
    # Define scan times for different creature types (seconds)
    SCAN_DURATIONS = {
        "passive": 4.0,      # passive creatures: 4 seconds
        "fish-dart": 6.0,    # fish-dart (aggressive): 6 seconds
        "fish-big": 8.0,     # fish-big (aggressive): 8 seconds
    }
    
    def __init__(self):
        # Structure: {creature_species: {creature_id: {'alive': progress_percent, 'dead': progress_percent}}}
        self.research_data = {
            "passive": {},
            "fish-dart": {},
            "fish-big": {},
        }
        # track whether an alive creature has been scanned for each species
        # only alive scans allow 100% completion
        self.alive_scanned = {
            "passive": False,
            "fish-dart": False,
            "fish-big": False,
        }
    
    def get_scan_duration(self, creature_species: str) -> float:
        """Get the scan duration for a creature species."""
        return self.SCAN_DURATIONS.get(creature_species, 4.0)
    
    def get_scan_progress(self, creature_id: int, creature_species: str, is_alive: bool) -> float:
        """Get the current scan progress for a creature (0-100%)."""
        if creature_species not in self.research_data:
            return 0.0
        
        if creature_id not in self.research_data[creature_species]:
            return 0.0
        
        state_key = 'alive' if is_alive else 'dead'
        return self.research_data[creature_species][creature_id].get(state_key, 0.0)
    
    def update_scan_progress(self, creature_id: int, creature_species: str, is_alive: bool, progress: float) -> None:
        """Update the scan progress for a creature."""
        if creature_species not in self.research_data:
            return
        
        if creature_id not in self.research_data[creature_species]:
            self.research_data[creature_species][creature_id] = {'alive': 0.0, 'dead': 0.0}
        
        state_key = 'alive' if is_alive else 'dead'
        
        # Store the maximum progress achieved for this state
        current = self.research_data[creature_species][creature_id].get(state_key, 0.0)
        
        # If alive creature, mark species as having alive scan
        if is_alive and creature_species in self.alive_scanned:
            self.alive_scanned[creature_species] = True
        
        # Dead creatures always cap at 50%, alive can reach 100%
        # BUT if no alive creature has been scanned for this species, cap all at 50%
        if is_alive:
            max_progress = 100.0
        else:
            max_progress = 50.0
        
        progress = min(progress, max_progress)
        
        self.research_data[creature_species][creature_id][state_key] = max(current, progress)
    
    def get_total_species_progress(self, creature_species: str) -> float:
        """Get the best progress for a species (combines alive and dead scans)."""
        if creature_species not in self.research_data or not self.research_data[creature_species]:
            return 0.0
        
        max_progress = 0.0
        for creature_data in self.research_data[creature_species].values():
            # Take the maximum of alive or dead scan for this creature
            best = max(creature_data.get('alive', 0.0), creature_data.get('dead', 0.0))
            max_progress = max(max_progress, best)
        
        # If no alive creatures have been scanned for this species, cap progress at 50%
        if creature_species in self.alive_scanned and not self.alive_scanned[creature_species]:
            max_progress = min(max_progress, 50.0)
        
        return max_progress
