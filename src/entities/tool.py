import pygame
from pathlib import Path


class Tool:
    # Simple data holder for a tool the player carries
    # the actual shooting and harvesting logic will be implemented separately
    def __init__(self, name, stat_label, stat_value, description, color=(120, 120, 120), image_path: Path | None = None) -> None:
        self.name = name
        self.stat_label = stat_label
        self.stat_value = stat_value
        self.description = description    # short text, kept for menus for later
        self.color = color  
        self.image: pygame.Surface | None = None

        if image_path is not None:
            loaded = pygame.image.load(str(image_path)).convert_alpha()

            loaded.set_colorkey((0, 0, 0))
            self.image = loaded 

    def use(self):
        # Right now Tool is just a data holder it knows its name and stats, but it doesn't do anything
        pass
