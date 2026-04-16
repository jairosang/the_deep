from abc import ABC, abstractmethod
import pygame

class Interactable(ABC):
    def __init__(self, x: float, y: float, width: float, height: float) -> None:
        self.rect = pygame.Rect(x - width/2, y, width, height)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.prompt_text = "Press E to interact"
    
    @abstractmethod
    def interact(self) -> None:
        pass

    def update(self, dt) -> None:
        pass

    def draw_prompt(self, world_surface: pygame.Surface) -> None:
        prompt_surface = pygame.font.SysFont("Segoe Print", 14).render(self.prompt_text, True, (255,255,255))
        prompt_rect = prompt_surface.get_rect(midbottom=(self.rect.centerx, self.rect.top - 6))
        background_rect = prompt_rect.inflate(24, 12)

        pygame.draw.rect(world_surface, (0, 0, 0), background_rect, border_radius=6)
        pygame.draw.rect(world_surface, (255, 255, 255), background_rect, 2, border_radius=6)
        world_surface.blit(prompt_surface, prompt_rect)

class Exit(Interactable):
    def interact(self) -> None:
        pass

class Upgrades(Interactable):
    def interact(self) -> None:
        pass

class Research(Interactable):
    def interact(self) -> None:
        pass

