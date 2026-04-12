from src.entities.base_thing import Thing
import src.utils.physics_service as phy
from config import game as g_config
from abc import ABC, abstractmethod
import pygame

class MovingThing(Thing, ABC):
    def __init__(self, image: pygame.Surface, pos: tuple[int, int] = (0,0)) -> None:
        super().__init__(image, pos)

        # the physical attributes, can be overwritten later
        self.input_direction = pygame.math.Vector2(0,0)
        self.velocity: pygame.math.Vector2 = pygame.math.Vector2(0, 0)
        self.mass = 0
        self.thrust = 0

    def update(self, dt, bound_rect: pygame.Rect, area_tiles):
        # ===== Movement update logic =======
        self._move_x(dt)                             # Player moves on one axis
        phy.check_and_resolve_player_map_collisions_x(self, area_tiles)    # Physics react
        self._move_y(dt)
        phy.check_and_resolve_player_map_collisions_y(self, area_tiles)
        # ====================================
        self._update_velocity(dt)
        self.rect.clamp_ip(bound_rect)              # Applying clamping
        self.pos.update(self.rect.x, self.rect.y)   # Updating to use the clamping

    def draw(self, surface: pygame.Surface):
        surface.blit(self.image, self.rect)
        
    # Calculate movement on the x axis
    def _move_x(self, dt):
        self.pos.x += self.velocity.x * dt
        self.rect.topleft = (int(self.pos.x), int(self.pos.y))  # sincronize the position after moving

    # Calculate movement on the y axis
    def _move_y(self, dt):
        self.pos.y += self.velocity.y * dt
        self.rect.topleft = (int(self.pos.x), int(self.pos.y))  # sincronize the position after moving

    def _update_velocity(self, dt):
        can_sprint = True if hasattr(self, "sprint_multiplier") and hasattr(self, "is_sprinting") else False

        current_thrust = self.thrust
        if can_sprint:
            # Apply extra thrust if the thing is sprinting (added type ignore because error was handled in previous statement alr but linter doesnt know it)
            current_thrust *= (self.sprint_multiplier if self.is_sprinting else 1) # type: ignore


        # Adjust acceleration and velocity according to thrust and adding slowdown with the drag
        acceleration = self.input_direction * current_thrust - (g_config["DRAG"] * self.velocity)
        self.velocity += acceleration * dt

        # Avoid floating point numbers staying there and keeping the thing moving when standing
        if self.velocity.length_squared() < 1:
            self.velocity = pygame.math.Vector2(0, 0)


