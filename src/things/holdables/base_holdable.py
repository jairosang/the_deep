from abc import ABC, abstractmethod
from things import Thing
from pathlib import Path
import pygame
import math

class Holdable(Thing, ABC):
    is_available: bool
    name: str
    description: str    # short text, kept for menus for later
    color: tuple[int, int, int]
    image_path: Path | None
    range: float
    cooldown_s: float

    def __init__(self) -> None:
        self.image_path: Path | None = getattr(self, "image_path", None)

        if self.image_path is not None:
            try:
                loaded = pygame.image.load(str(self.image_path)).convert_alpha()
                loaded.set_colorkey((0, 0, 0))
                self.image = loaded
            except:
                # Fallback if image fails to load
                self.image = pygame.Surface((16, 16))
                self.image.fill(self.color)
        else:
            # Create colored placeholder if no image path
            self.image = pygame.Surface((16, 16))
            self.image.fill(self.color)

        super().__init__(self.image)

        self.base_image = self.image.copy()
        self.mouse_pos = pygame.math.Vector2(self.rect.center)
        self.player_center = pygame.math.Vector2(self.rect.center)
        self.orbit_radius = 25
        self._aim_direction = pygame.math.Vector2(1, 0)

    def handle_inputs(self, mouse_pos: tuple[int, int]):
        self.mouse_pos.update(mouse_pos)

        aim_vector = self.mouse_pos - self.player_center
        if aim_vector.length_squared() > 0:
            self._aim_direction = aim_vector.normalize()

    def update(self, dt, bound_rect: pygame.Rect, player_pos):
        self.player_center.update(player_pos)

        # Keep the holdable only rotating around the players center
        holdable_center = self.player_center + self._aim_direction * self.orbit_radius
        self.rect.center = (int(holdable_center.x), int(holdable_center.y))

        if bound_rect is not None:
            self.rect.clamp_ip(bound_rect)

        self.pos.update(self.rect.x, self.rect.y)

        angle = -math.degrees(math.atan2(self._aim_direction.y, self._aim_direction.x))
        angle = angle if self._aim_direction.x > 0 else angle * -1
        current_center = self.rect.center
        rotated_image = pygame.transform.rotate(self.base_image, angle)
        if self._aim_direction.x < 0:
            rotated_image = pygame.transform.flip(rotated_image, False, True)
        self.image = rotated_image
        self.rect = self.image.get_rect(center=current_center)
        self.pos.update(self.rect.x, self.rect.y)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    @abstractmethod
    def shoot(self, pos: tuple[int, int]):
        pass
    
    @property
    def get_image(self) -> pygame.Surface:
        return self.image

    