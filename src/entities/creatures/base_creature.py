import pygame
import random
from abc import abstractmethod
from src.entities.base_entity import Entity
from config import game as g_config
Vec2 = pygame.math.Vector2

class Creature(Entity):
    def __init__(self, pos, size=20, thrust=90.0):
        image = pygame.Surface((size, size))
        image.fill((30, 30, 30))
        super().__init__(image, pos)

        self.size = size
        self.thrust = thrust
        self.mass = 0

        # wander behaviour
        self._wander_dir = Vec2(1, 0)
        self._wander_timer = 0.0
        self._wander_interval = random.uniform(0.6, 1.4)

    def update(self, dt, player_pos, bounds=None):
        direction = self.think(dt, player_pos)

        # same movement
        acceleration = direction * self.thrust - (g_config["DRAG"] * self.velocity)
        self.velocity += acceleration * dt

        if self.velocity.length_squared() < 1:
            self.velocity = Vec2(0, 0)

        self.pos += self.velocity * dt

        if bounds is not None:
            self.pos.x = max(bounds.left, min(self.pos.x, bounds.right - self.size))
            self.pos.y = max(bounds.top,  min(self.pos.y, bounds.bottom - self.size))

        self.rect.topleft = (int(self.pos.x), int(self.pos.y))
        
    @abstractmethod
    def think(self, dt: float, player_pos:Vec2) -> None:    #changed to an abstract class, the subclass must implement this
        pass

    def distance_to_player(self, player) -> float:
        return self.pos.distance_to(self._player_pos(player))

    def _dir_towards(self, target: Vec2) -> Vec2:
        d = target - self.pos
        if d.length_squared() == 0:
            return Vec2(0, 0)
        return d.normalize()
    
    def _dir_away(self, target: Vec2) -> Vec2:
        d = self.pos - target
        if d.length_squared() == 0:
            return Vec2(0, 0)
        return d.normalize()
    
    def wander_dir(self, dt: float) -> Vec2:
        #Returns a changing random direction
        self._wander_timer += dt
        if self._wander_timer >= self._wander_interval:
            self._wander_timer = 0.0
            self._wander_interval = random.uniform(0.6, 1.4)

            self._wander_dir = Vec2(random.uniform(-1, 1), random.uniform(-1, 1))
            if self._wander_dir.length_squared() == 0:
                self._wander_dir = Vec2(1, 0)
            else:
                self._wander_dir = self._wander_dir.normalize()

        return self._wander_dir

    def draw(self, screen: pygame.Surface, color=(30, 30, 30)) -> None:
        pygame.draw.rect(screen, color, self.rect)