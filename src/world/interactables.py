from abc import abstractmethod
import pygame
from ui import get_font

class Interactable:
    def __init__(self, x: float, y: float, width: float, height: float) -> None:
        self.rect = pygame.Rect(x - width/2, y, width, height)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.prompt_text = "'E' to interact"

    @abstractmethod
    def interact(self) -> None:
        pass

    def draw_prompt(self, world_surface: pygame.Surface, player_pos) -> None:
        prompt_surface = get_font(10, "secondary").render(self.prompt_text, True, (255,255,255))
        
        # getting the position between the interactable and the player
        player_prompt_x = player_pos[0] - self.rect.centerx
        player_prompt_y = player_pos[1] - self.rect.centery
        distance = (player_prompt_x**2 + player_prompt_y**2) ** 0.5
        
        min_distance_from_player = 20
        
        if distance > min_distance_from_player:
            # putting the 
            the_inbetween_location_x = player_prompt_x / distance
            the_inbetween_location_y = player_prompt_y / distance
            prompt_x = player_pos[0] - the_inbetween_location_x * min_distance_from_player
            prompt_y = player_pos[1] - the_inbetween_location_y * min_distance_from_player - 30
        else:
            # if the player is very close the prompt should stay in the interactable
            prompt_x = self.rect.centerx
            prompt_y = self.rect.centery - 30
        
        prompt_rect = prompt_surface.get_rect(center=(prompt_x, prompt_y))
        background_rect = prompt_rect.inflate(12, 6)

        pygame.draw.rect(world_surface, (0, 0, 0), background_rect, border_radius=6)
        pygame.draw.rect(world_surface, (255, 255, 255), background_rect, 2, border_radius=6)
        world_surface.blit(prompt_surface, prompt_rect)

class Exit(Interactable):
    def __init__(self, x: float, y: float, width: float, height: float, on_interact=None) -> None:
        super().__init__(x, y, width, height)
        self.on_interact = on_interact
        self.prompt_text = "'E' to go underwater"


    def interact(self) -> None:
        if self.on_interact is not None:
            self.on_interact()

class Upgrades(Interactable):
    def __init__(self, x: float, y: float, width: float, height: float, on_interact=None) -> None:
        super().__init__(x, y, width, height)
        self.on_interact = on_interact
        self.prompt_text = "'E' to open upgrades"

    def interact(self) -> None:
        if self.on_interact is not None:
            self.on_interact()

class Research(Interactable):
    def __init__(self, x: float, y: float, width: float, height: float, on_interact=None) -> None:
        super().__init__(x, y, width, height)
        self.on_interact = on_interact
        self.prompt_text = "'E' to open database"

    def interact(self) -> None:
        if self.on_interact is not None:
            self.on_interact()

class Shop(Interactable):
    def __init__(self, x: float, y: float, width: float, height: float, on_interact=None) -> None:
        super().__init__(x, y, width, height)
        self.on_interact = on_interact
        self.prompt_text = "'E' to sell loot"

    def interact(self) -> None:
        if self.on_interact is not None:
            self.on_interact()

