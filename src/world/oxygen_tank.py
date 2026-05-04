import pygame
from .interactables import Interactable

class OxygenTank(Interactable):
    def __init__(self, x: float, y: float, oxygen_refill: float = 30.0, on_interact=None) -> None:
        super().__init__(x, y, width=40, height=40)
        self.oxygen_refill = oxygen_refill
        self.on_interact = on_interact
        self.prompt_text = "Press E to refill O2"
        
        # Load oxygen tank sprite
        try:
            self.image = pygame.image.load("assets/sprites/oxygen-tank-pixel-art-vector.jpg")
            self.image = pygame.transform.scale(self.image, (40, 40))
            # Convert to RGBA to support transparency
            self.image = self.image.convert_alpha()
            # Make white background transparent
            self.image.set_colorkey((255, 255, 255))
        except:
            # Fallback to gray box if sprite fails to load
            self.image = pygame.Surface((40, 40))
            self.image.fill((150, 150, 150))
    
    def interact(self) -> None:
        """Interact with the oxygen tank (refill oxygen)."""
        if self.on_interact is not None:
            self.on_interact()
    
    def draw(self, world_surface: pygame.Surface) -> None:
        """Draw the oxygen tank sprite."""
        world_surface.blit(self.image, self.rect)

